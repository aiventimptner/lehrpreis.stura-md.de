from django.shortcuts import render
from django.utils import timezone
from django.views.generic import ListView, TemplateView, FormView

from .forms import SubmissionForm
from .models import Lecturer, Verification


class LecturerListView(ListView):
    model = Lecturer
    queryset = Lecturer.objects.filter(nomination__verified=True).distinct()


class SubmissionFormView(FormView):
    form_class = SubmissionForm
    template_name = 'award/submission_form.html'
    success_url = 'success/'

    def get_initial(self):
        initial = super().get_initial()
        initial.update(self.request.GET.dict())
        return initial

    def form_valid(self, form):
        form.save()
        form.send_verification_email(self.request)
        return super().form_valid(form)


class SubmissionSuccessView(TemplateView):
    template_name = 'award/submission_success.html'


def verify_token(request, token):
    try:
        verification = Verification.objects.get(pk=token)
    except Verification.DoesNotExist:
        feedback = {
            'valid_token': False,
            'title': "Token existiert nicht",
            'message': "Der verwendete Link ist beschädigt oder veraltet. Bitte verwende nur "
                       "den Link, welchen du per E-Mail von uns bekommen hast.",
        }
        return render(request, 'award/verification.html', {'feedback': feedback})

    if timezone.now() > verification.expiration:
        expiry = timezone.make_naive(verification.expiration).strftime('%d.%m.%y um %H:%M Uhr')
        feedback = {
            'valid_token': False,
            'title': "Token ist abgelaufen",
            'message': f"Der verwendete Link war nur bis zum {expiry} gültig.",
        }
        return render(request, 'award/verification.html', {'feedback': feedback})

    nomination = verification.nomination
    verification.delete()

    nomination.verified = True
    nomination.save()

    lecturer = nomination.lecturer

    feedback = {
        'valid_token': True,
        'title': "Token ist gültig",
        'message': f"Dein Vorschlag für {lecturer.get_full_name()} wurde erfolgreich bestätigt."
    }

    return render(request, 'award/verification.html', {'feedback': feedback})
