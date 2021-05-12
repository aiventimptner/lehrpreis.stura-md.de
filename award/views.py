from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import ListView, TemplateView

from award.forms import LecturerForm, ModuleForm, NominationForm
from award.models import Lecturer, Module, Nomination


class LecturerListView(ListView):
    model = Lecturer


def add_submission(request):
    if request.method == 'POST':
        lecturer_form = LecturerForm(request.POST)
        if lecturer_form.has_error('__all__'):
            lecturer_form.errors.pop('__all__')

        module_form = ModuleForm(request.POST)
        if module_form.has_error('name'):
            module_form.errors.pop('name')

        nomination_form = NominationForm(request.POST)

        if lecturer_form.is_valid() and module_form.is_valid() and nomination_form.is_valid():
            if Lecturer.objects.filter(**lecturer_form.cleaned_data).exists():
                lecturer = Lecturer.objects.get(**lecturer_form.cleaned_data)
            else:
                lecturer = lecturer_form.save()

            if Module.objects.filter(**module_form.cleaned_data).exists():
                module = Module.objects.get(**module_form.cleaned_data)
            else:
                module = module_form.save()

            module.lecturers.add(lecturer)

            nomination = nomination_form.save(commit=False)
            nomination.lecturer = lecturer
            nomination.module = module
            nomination.save()

            return HttpResponseRedirect('success/')

    else:
        lecturer_form = LecturerForm(instance=Lecturer())
        module_form = ModuleForm(instance=Module())
        nomination_form = NominationForm(instance=Nomination())

    return render(request, 'award/submission_form.html', {'lecturer_form': lecturer_form,
                                                          'module_form': module_form,
                                                          'nomination_form': nomination_form})


class SubmissionSuccessView(TemplateView):
    template_name = 'award/submission_success.html'
