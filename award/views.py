from django.shortcuts import render
from django.views.generic import ListView, TemplateView, FormView

from .forms import SubmissionForm
from .models import Lecturer


class LecturerListView(ListView):
    model = Lecturer
    queryset = Lecturer.objects.filter(nomination__verified=True)


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


def verify_token(request):
    # TODO add verification logic & replace template
    return render(request, 'award/submission_success.html')
