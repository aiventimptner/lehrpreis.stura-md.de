from django.urls import path

from award.views import LecturerListView

urlpatterns = [
    path('', LecturerListView.as_view(), name='lecturer-list'),
]
