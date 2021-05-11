from django.views.generic import ListView

from award.models import Lecturer


class LecturerListView(ListView):
    model = Lecturer
