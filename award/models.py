from django.core.validators import EmailValidator
from django.db import models


class Lecturer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['first_name', 'last_name'], name='unique fullname')
        ]

    def __str__(self):
        return self.full_name()

    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Module(models.Model):
    name = models.CharField(max_length=250, unique=True)
    lecturers = models.ManyToManyField(Lecturer)

    def __str__(self):
        return self.name


class Nomination(models.Model):
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    reason = models.TextField()
    sub_email = models.EmailField(unique=True, validators=[EmailValidator(allowlist=['st.ovgu.de', 'ovgu.de'])])
    sub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sub_email
