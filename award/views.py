from django.shortcuts import render, reverse
from django.utils import timezone
from django.views.generic import ListView, TemplateView, FormView
from markdown import markdown

from .forms import SubmissionForm, RenewTokenForm
from .models import Lecturer, Verification


class LecturerListView(ListView):
    model = Lecturer
    queryset = Lecturer.objects.filter(nomination__is_verified=True).distinct().order_by('first_name', 'last_name')


class SubmissionFormView(FormView):
    form_class = SubmissionForm
    template_name = 'award/submission_form.html'
    success_url = 'success/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['privacy'] = markdown("Wir benötigen deine E-Mail-Adresse um deine Identität zu bestätigen und "
                                      "Falschangaben zu verhindern. Die personenbezogenen Daten werden von uns stets "
                                      "vertraulich behandelt und nicht an Dritte weitergegeben. Sämtliche "
                                      "eingereichten Vorschläge werden für **maximal 6 Monate** aufbewahrt und "
                                      "anschließend unwiderruflich gelöscht.")
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial.update(self.request.GET.dict())
        return initial

    def form_valid(self, form):
        form.save(self.request)
        return super().form_valid(form)


class SubmissionSuccessView(TemplateView):
    template_name = 'award/success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['feedback'] = markdown(f"Dein Vorschlag ist erfolgreich bei uns eingegangen. **Du musst als letzten "
                                       f"Schritt noch deinen Vorschlag bestätigen, in dem du auf den Link klickst, "
                                       f"welchen wir dir eben per E-Mail geschickt haben.** Wenn du noch weitere "
                                       f"Vorschläge einreichen oder bereits existierende Vorschläge unterzeichnen "
                                       f"möchtest kannst du einfach wieder zur "
                                       f"[Startseite]({reverse('lecturer-list')}) zurückkehren.")
        return context


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
            'token_expired': True,
            'sub_email': verification.nomination.get_valid_email(),
        }
        return render(request, 'award/verification.html', {'feedback': feedback})

    nomination = verification.nomination
    verification.delete()

    nomination.is_verified = True
    nomination.save()

    lecturer = nomination.lecturer

    feedback = {
        'valid_token': True,
        'title': "Token ist gültig",
        'message': f"Dein Vorschlag für {lecturer.get_full_name()} wurde erfolgreich bestätigt."
    }

    return render(request, 'award/verification.html', {'feedback': feedback})


class RenewTokenView(FormView):
    form_class = RenewTokenForm
    template_name = 'award/renew-token.html'
    success_url = 'success/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['privacy'] = markdown("Die eingegebene E-Mail-Adresse wird von uns **nicht gespeichert**. Wir "
                                      "verwenden Sie lediglich für das Versenden der benötigten E-Mails.")
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial.update(self.request.GET.dict())
        return initial

    def form_valid(self, form):
        form.renew_tokens(self.request)
        return super().form_valid(form)


class RenewTokenSuccessView(TemplateView):
    template_name = 'award/success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['feedback'] = markdown("Wir haben dir für alle noch offenen Vorschlägen soeben eine neue E-Mail mit "
                                       "gültigem Bestätigungslink geschickt. **Sämtliche alte E-Mails mit einem "
                                       "Bestätigungslink, welche du noch in deinem Postfach hast, sind nun nicht "
                                       "länger gültig.**")
        return context
