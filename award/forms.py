from datetime import timedelta
from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

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
        'expiry': timezone.make_naive(expiration),
    }

    data = {
        'nomination': nomination,
        'lecturer': nomination.lecturer,
        'link': link,
    }

    msg_html = render_to_string('award/mails/verification.html', data)
    msg_plain = render_to_string('award/mails/verification.txt', data)

    email = EmailMultiAlternatives(subject=_("Your nomination for the teaching award of the student body"),
                                   body=msg_plain,
                                   to=[nomination.get_valid_email()],
                                   reply_to=['verwaltung@stura-md.de'])
    email.attach_alternative(msg_html, 'text/html')
    email.send()


class SubmissionForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'input',
        'autocomplete': 'off',
    }), label=_("First name"))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'input',
        'autocomplete': 'off',
    }), label=_("Last name"))
    faculty = forms.CharField(widget=forms.Select(choices=Lecturer.FACULTIES), label=_("Faculty"))
    reason = forms.CharField(widget=forms.Textarea(attrs={'class': 'textarea', 'rows': 3}), label=_("Reason"))
    sub_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'input'}), label=_("Email address"))

    def clean_sub_email(self):
        data = self.cleaned_data['sub_email'].lower()
        try:
            # Override default validation message because email host hasn't been cleaned yet
            validate_domain(strip_email_subdomain(data)[0])
        except ValidationError:
            raise ValidationError(_("Only email addresses of the following domains are allowed: st.ovgu.de, ovgu.de"))
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
                msg = _("Students before you have indicated this lecturer as part "
                        "of the F%(lecturer_faculty)s. If this is not correct, please "
                        "email us at 'verwaltung@stura-md.de'.\n"
                        "If there should be a person with this name at both "
                        "faculties (F%(lecturer_faculty)s, F%(faculty)s), please contact "
                        "us via email as well." % {'lecturer_faculty': lecturer.faculty, 'faculty': faculty})
                self.add_error('faculty', msg)
                return

            if sub_email:
                email, is_student = strip_email_subdomain(sub_email)
                nomination = Nomination.objects.filter(lecturer=lecturer, sub_email=email)
                if nomination.exists():
                    raise ValidationError(
                        _("A nomination for this teacher in combination with the "
                          "given email address were already received."),
                        code='ambiguous')

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
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'input'}), label=_("Email address"))

    def clean_email(self):
        return self.cleaned_data['email'].lower()

    def clean(self):
        cleaned_data = super().clean()

        try:
            sub_email, is_student = strip_email_subdomain(cleaned_data.get('sub_email'))
        except AttributeError:
            sub_email = None

        if sub_email:
            pending_nominations = Nomination.objects.filter(
                sub_email=sub_email,
                is_verified=False,
            ).exists()

            if not pending_nominations:
                raise ValidationError(
                    _("No nomination with the specified email address could be found or "
                      "all nominations with this email address are already confirmed."),
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
