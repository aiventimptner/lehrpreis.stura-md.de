from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import ListView, TemplateView

from award.forms import LecturerForm, ModuleForm, StudentForm, NominationForm
from award.models import Lecturer, Module, Student, Nomination


class LecturerListView(ListView):
    model = Lecturer


def add_submission(request):
    if request.method == 'POST':
        # LectureForm
        lecturer = Lecturer.objects.filter(first_name=request.POST.get('lecturer-first_name'),
                                           last_name=request.POST.get('lecturer-last_name')).first()
        lecturer_form = LecturerForm(request.POST, prefix='lecturer')
        if lecturer:
            del lecturer_form.errors['__all__']
        else:
            if lecturer_form.is_valid():
                lecturer = lecturer_form.save()

        # ModuleForm
        module = Module.objects.filter(name=request.POST.get('module-name')).first()
        module_form = ModuleForm(request.POST, prefix='module')
        if module:
            del module_form.errors['name']
        else:
            if module_form.is_valid():
                module = module_form.save()

        if lecturer_form.is_valid() and module_form.is_valid():
            module.lecturers.add(lecturer)

        # StudentForm
        student = Student.objects.filter(email=request.POST.get('student-email')).first()
        student_form = StudentForm(request.POST, prefix='student')
        print(student_form.errors)
        if student:
            del student_form.errors['email']
        else:
            if student_form.is_valid():
                student = student_form.save()

        # NominationForm
        nomination = Nomination.objects.filter(lecturer=lecturer, module=module, student=student).first()
        nomination_form = NominationForm(request.POST, prefix='nomination')
        if nomination:
            nomination_form.add_error('__all__', ValidationError("Es liegt bereits eine Unterschrift für diese "
                                                                 "Kombination aus Dozent:in, Modul und Unterzeichner "
                                                                 "vor."))
        if (lecturer_form.is_valid() and module_form.is_valid() and
                student_form.is_valid() and nomination_form.is_valid()):
            nomination = nomination_form.save(commit=False)
            nomination.lecturer = lecturer
            nomination.module = module
            nomination.student = student
            nomination_form.save()

            return HttpResponseRedirect('success/')

    else:
        initial_data = {}

        if 'lecturer' in request.GET.keys():
            lecturer = Lecturer.objects.get(id=request.GET.get('lecturer'))
            initial_data['lecturer'] = model_to_dict(lecturer)

        lecturer_form = LecturerForm(prefix='lecturer', initial=initial_data.get('lecturer'))
        module_form = ModuleForm(prefix='module')
        student_form = StudentForm(prefix='student')
        nomination_form = NominationForm(prefix='nomination')

    return render(request, 'award/submission_form.html', {'lecturer_form': lecturer_form,
                                                          'module_form': module_form,
                                                          'student_form': student_form,
                                                          'nomination_form': nomination_form})


class SubmissionSuccessView(TemplateView):
    template_name = 'award/submission_success.html'
