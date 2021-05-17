from django import forms
from django.core.exceptions import ValidationError

from .models import Lecturer, Nomination, validate_ovgu


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
                                 validators=[validate_ovgu])

    def clean(self):
        cleaned_data = super().clean()
        nomination = Nomination.objects.filter(lecturer__first_name=cleaned_data.get('first_name'),
                                               lecturer__last_name=cleaned_data.get('last_name'),
                                               lecturer__faculty=cleaned_data.get('faculty'),
                                               sub_email=cleaned_data.get('sub_email')).first()
        if nomination:
            raise ValidationError("Eine Unterschrift für diese Lehrperson in Kombination "
                                  "mit der angegeben E-Mail-Adresse liegt bereits vor.", code='not unique')

    def save(self):
        lecturer, create = Lecturer.objects.get_or_create(first_name=self.cleaned_data['first_name'],
                                                          last_name=self.cleaned_data['last_name'],
                                                          faculty=self.cleaned_data['faculty'])
        nomination = Nomination.objects.create(lecturer=lecturer,
                                               reason=self.cleaned_data['reason'],
                                               sub_email=self.cleaned_data['sub_email'])
        # TODO send mail to validate submission
