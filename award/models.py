import secrets

from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.db import models


class Lecturer(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['first_name', 'last_name'], name='unique fullname')
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
        return self.full_name()

    def full_name(self):
        return f"{self.first_name} {self.last_name}"


def validate_ovgu(value):
    if value.split('@')[-1] not in ['ovgu.de', 'st.ovgu.de']:
        raise ValidationError("Es sind nur E-Mail-Adresse der folgenden Domains erlaubt: st.ovgu.de, ovgu.de")


class Nomination(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['lecturer', 'sub_email'], name='unique nomination')
        ]

    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    reason = models.TextField()
    sub_email = models.EmailField(validators=[validate_ovgu])
    sub_date = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.sub_email


def generate_token():
    return secrets.token_urlsafe(12)


class Verification(models.Model):
    token = models.CharField(max_length=16, primary_key=True, validators=[validate_slug], default=generate_token)
    nomination = models.ForeignKey(Nomination, on_delete=models.CASCADE)
    expiration = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)
