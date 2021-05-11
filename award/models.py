from django.core.validators import EmailValidator
from django.db import models


class Lecturer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['first_name', 'last_name'], name='unique fullname')
        ]

    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Module(models.Model):
    name = models.CharField(max_length=250, unique=True)
    lecturers = models.ManyToManyField(Lecturer)


class Nomination(models.Model):
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    reason = models.TextField()
    submitter_email = models.EmailField(unique=True, validators=[EmailValidator(allowlist=['st.ovgu.de', 'ovgu.de'])])
