import re
import secrets

from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.db import models
from django.db.models import UniqueConstraint, CheckConstraint, Q


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
        (FMB, "Maschinenbau"),
        (FEIT, "Elektro- & Informationstechnik"),
        (FVST, "Verfahrens- & Systemtechnik"),
        (FIN, "Informatik"),
        (FWW, "Wirtschaftswissenschaften"),
        (FHW, "Humanwissenschaften"),
        (FNW, "Naturwissenschaften"),
        (FME, "Medizin"),
        (FMA, "Mathematik")
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    faculty = models.CharField(max_length=3, choices=FACULTIES)

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


PATTERN = r'^[\.0-9a-z]+@(st\.)?ovgu\.de$'


def validate_domain(value):
    match = re.match(PATTERN, value, re.IGNORECASE)
    if not match:
        raise ValidationError("Es sind nur E-Mail-Adresse der folgenden Domains erlaubt: st.ovgu.de, ovgu.de")


class Nomination(models.Model):
    class Meta:
        constraints = [
            CheckConstraint(check=Q(sub_email__iregex=PATTERN), name='check_domain_whitelist'),
            UniqueConstraint(fields=['lecturer', 'sub_email'],
                             condition=Q(sub_email__iregex=PATTERN),    # TODO condition does nothing?!
                             name='unique_nomination'),
        ]

    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    reason = models.TextField()
    sub_email = models.EmailField(validators=[validate_domain])
    sub_date = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.sub_email

    def get_first_name(self):
        username = self.sub_email.split('@')[0]
        if '.' in list(username):
            return username.split('.')[0].title()
        return username.title()


def generate_token():
    return secrets.token_urlsafe(12)


class Verification(models.Model):
    token = models.CharField(max_length=16, primary_key=True, validators=[validate_slug], default=generate_token)
    nomination = models.ForeignKey(Nomination, on_delete=models.CASCADE)
    expiration = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)
