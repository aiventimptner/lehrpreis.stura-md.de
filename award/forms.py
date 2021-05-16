from django import forms

from award.models import Lecturer, Module, Student, Nomination


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


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input'}),
        }
        labels = {
            'name': 'Modul bzw. Kurs',
        }


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input'}),
            'last_name': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
        }
        labels = {
            'first_name': 'Vorname',
            'last_name': 'Nachname',
            'email': 'E-Mail-Adresse',
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
