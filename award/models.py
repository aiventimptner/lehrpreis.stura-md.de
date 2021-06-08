import secrets

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.db import models
from django.db.models import UniqueConstraint, CheckConstraint, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Lecturer(models.Model):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['first_name', 'last_name'], name='unique_fullname'),
        ]

    FMB = 'MB'
    FEIT = 'EIT'
    FVST = 'VST'
    FIN = 'IN'
    FWW = 'WW'
    FHW = 'HW'
    FNW = 'NW'
    FME = 'ME'
    FMA = 'MA'

    FACULTIES = [
        (FMB, _("Mechanical Engineering")),
        (FEIT, _("Electrical Engineering & Information Technology")),
        (FVST, _("Process & Systems Engineering")),
        (FIN, _("Computer Science")),
        (FWW, _("Economics and Management")),
        (FHW, _("Humanities, Social Science & Education")),
        (FNW, _("Natural Science")),
        (FME, _("Medicine")),
        (FMA, _("Mathematics"))
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    faculty = models.CharField(max_length=3, choices=FACULTIES)

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


def validate_domain(value: str):
    if not value.endswith('@ovgu.de'):
        raise ValidationError(_("Es sind nur E-Mail-Adresse mit der Endung '@ovgu.de' erlaubt."))


class Nomination(models.Model):
    class Meta:
        constraints = [
            CheckConstraint(check=Q(sub_email__endswith='@ovgu.de'), name='check_domain_whitelist'),
            UniqueConstraint(fields=['lecturer', 'sub_email'], name='unique_nomination'),
        ]

    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    reason = models.TextField()
    sub_email = models.EmailField(validators=[validate_domain])
    sub_date = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    is_student = models.BooleanField()

    def __str__(self):
        return self.get_full_name()

    def get_username(self):
        return self.sub_email.split('@')[0]

    def get_full_name(self):
        return self.get_username().replace('.', ' ').title()

    def get_valid_email(self):
        if self.is_student:
            user, host = self.sub_email.split('@')
            return f"{user}@st.{host}"
        return self.sub_email


def generate_token():
    return secrets.token_urlsafe(12)


class Verification(models.Model):
    token = models.CharField(max_length=16, primary_key=True, validators=[validate_slug], default=generate_token)
    nomination = models.ForeignKey(Nomination, on_delete=models.CASCADE)
    expiration = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token

    @admin.display(boolean=True)
    def is_expired(self):
        return timezone.now() > self.expiration
