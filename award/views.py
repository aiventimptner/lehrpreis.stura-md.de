from django.views.generic import ListView, TemplateView, FormView

from .forms import SubmissionForm
from .models import Lecturer


class LecturerListView(ListView):
    model = Lecturer


class SubmissionFormView(FormView):
    form_class = SubmissionForm
    template_name = 'award/submission_form.html'
    success_url = 'success/'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class SubmissionSuccessView(TemplateView):
    template_name = 'award/submission_success.html'
