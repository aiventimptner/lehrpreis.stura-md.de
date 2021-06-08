from datetime import timedelta
from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from markdown import markdown

from .models import Lecturer, Nomination, Verification, validate_domain


def strip_email_subdomain(email: str) -> (str, bool):
    user, host = email.split('@')
    if host.startswith('st.'):
        return f"{user}@{host[3:]}", True
    return f"{user}@{host}", False


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
                                   to=[nomination.get_valid_email()],
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
                                 label="E-Mail-Adresse")

    def clean_sub_email(self):
        data = self.cleaned_data['sub_email'].lower()
        try:
            # Override default validation message because email host hasn't been cleaned yet
            validate_domain(strip_email_subdomain(data)[0])
        except ValidationError:
            raise ValidationError("Es sind nur E-Mail-Adresse der folgenden Domains erlaubt: st.ovgu.de, ovgu.de")
        return data

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        faculty = cleaned_data.get('faculty')
        sub_email = cleaned_data.get('sub_email')

        if first_name and last_name:
            try:
                lecturer = Lecturer.objects.get(first_name=first_name, last_name=last_name)
            except Lecturer.DoesNotExist:
                lecturer = None
            if lecturer and lecturer.faculty != faculty:
                msg = (f"Studierende vor dir haben diese Lehrperson als Teil der "
                       f"F{lecturer.faculty} angeben. Sollte das nicht "
                       f"korrekt sein, schreibe uns bitte eine Mail an 'verwaltung@stura-md.de'.\n"
                       f"Falls es an beiden Fakultäten (F{lecturer.faculty}, F{faculty}) jeweils eine "
                       f"Person mit diesem Namen geben sollte, melde dich bitte ebenfalls per E-Mail bei "
                       f"uns.")
                self.add_error('faculty', msg)
                return

            if sub_email:
                email, is_student = strip_email_subdomain(sub_email)
                nomination = Nomination.objects.filter(lecturer=lecturer, sub_email=email)
                if nomination.exists():
                    raise ValidationError("Eine Unterschrift für diese Lehrperson in Kombination "
                                          "mit der angegeben E-Mail-Adresse liegt bereits vor.", code='ambiguous')

    def save(self, request: HttpRequest):
        lecturer, create = Lecturer.objects.get_or_create(first_name=self.cleaned_data['first_name'],
                                                          last_name=self.cleaned_data['last_name'],
                                                          faculty=self.cleaned_data['faculty'])
        sub_email, is_student = strip_email_subdomain(self.cleaned_data['sub_email'])
        # Check if submitter already nominated once and use same email host instead of provided value
        is_student = Nomination.objects.filter(
            sub_email=sub_email
        ).values_list('is_student', flat=True).first() or is_student
        nomination = Nomination.objects.create(lecturer=lecturer,
                                               reason=self.cleaned_data['reason'],
                                               sub_email=sub_email,
                                               is_student=is_student)

        send_verification_email(nomination, request)


class RenewTokenForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'input'}), label="E-Mail-Adresse")

    def clean_email(self):
        return self.cleaned_data['email'].lower()

    def clean(self):
        cleaned_data = super().clean()

        try:
            sub_email, _ = strip_email_subdomain(cleaned_data.get('sub_email'))
        except AttributeError:
            sub_email = None

        if sub_email:
            pending_nominations = Nomination.objects.filter(
                sub_email=sub_email,
                is_verified=False,
            ).exists()

            if not pending_nominations:
                raise ValidationError("Es konnte kein Vorschlag mit der angegebenen E-Mail-Adresse gefunden werden "
                                      "oder es sind bereits alle Vorschläge mit dieser E-Mail-Adresse bestätigt.",
                                      code='unknown')

    def renew_tokens(self, request: HttpRequest):
        sub_email, is_student = strip_email_subdomain(self.cleaned_data['email'])

        verifications = Verification.objects.filter(
            nomination__sub_email=sub_email,
            nomination__is_verified=False,
        ).all()

        for verification in verifications:
            verification.delete()

        nominations = Nomination.objects.filter(
            sub_email=sub_email,
            is_verified=False,
        ).all()

        for nomination in nominations:
            send_verification_email(nomination, request)
