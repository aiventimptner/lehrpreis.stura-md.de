from datetime import timedelta
from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from markdown import markdown

from .models import Lecturer, Nomination, validate_domain, Verification


def get_alt_email(value: str):
    if value is None:
        return None
    user, host = value.split('@')
    if host.startswith('st.'):
        return f"{user}@ovgu.de"
    else:
        return f"{user}@st.ovgu.de"


def send_verification_email(nomination: Nomination, request: HttpRequest):
    expiration = timezone.now() + timedelta(hours=24)
    verification = Verification.objects.create(nomination=nomination, expiration=expiration)

    link = {
        'url': request.build_absolute_uri(reverse('verify-token', kwargs={'token': verification.token})),
        'expiry': timezone.make_naive(expiration).strftime('%d.%m.%y um %H:%M Uhr'),
    }

    message = render_to_string('award/mails/verification.md', {'nomination': nomination,
                                                               'lecturer': nomination.lecturer,
                                                               'link': link})

    email = EmailMultiAlternatives(subject="Dein Vorschlag für den Lehrpreis der Studierendenschaft",
                                   body=message,
                                   to=[nomination.sub_email],
                                   reply_to=['verwaltung@stura-md.de'])
    email.attach_alternative(markdown(message), 'text/html')
    email.send()


class SubmissionForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input'}),
                                 label="Vorname")
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input'}),
                                label="Nachname")
    faculty = forms.CharField(widget=forms.Select(choices=Lecturer.FACULTIES),
                              label="Fakultät")
    reason = forms.CharField(widget=forms.Textarea(attrs={'class': 'textarea', 'rows': 3}),
                             label="Begründung")
    sub_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'input'}),
                                 label="E-Mail-Adresse",
                                 validators=[validate_domain])

    def clean_sub_email(self):
        return self.cleaned_data['sub_email'].lower()

    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get('sub_email')
        email_alt = get_alt_email(cleaned_data.get('sub_email'))

        already_submitted = Nomination.objects.filter(
            lecturer__first_name=cleaned_data.get('first_name'),
            lecturer__last_name=cleaned_data.get('last_name'),
            lecturer__faculty=cleaned_data.get('faculty')
        ).filter(
            Q(sub_email=email) | Q(sub_email=email_alt)
        ).exists()
        if already_submitted:
            raise ValidationError("Eine Unterschrift für diese Lehrperson in Kombination "
                                  "mit der angegeben E-Mail-Adresse liegt bereits vor.", code='ambiguous')

    def save(self, request: HttpRequest):
        lecturer, create = Lecturer.objects.get_or_create(first_name=self.cleaned_data['first_name'],
                                                          last_name=self.cleaned_data['last_name'],
                                                          faculty=self.cleaned_data['faculty'])
        nomination = Nomination.objects.create(lecturer=lecturer,
                                               reason=self.cleaned_data['reason'],
                                               sub_email=self.cleaned_data['sub_email'])

        send_verification_email(nomination, request)

