from django import forms

from award.models import Lecturer, Nomination


class LecturerForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input'}),
            'last_name': forms.TextInput(attrs={'class': 'input'}),
        }
        labels = {
            'first_name': 'Vorname',
            'last_name': 'Nachname',
        }


class NominationForm(forms.ModelForm):
    class Meta:
        model = Nomination
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'textarea', 'rows': '3'}),
        }
        labels = {
            'reason': 'Gründe für herausragende Lehre',
        }
