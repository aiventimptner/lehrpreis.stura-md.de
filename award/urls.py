from django.urls import path

from .views import LecturerListView, SubmissionFormView, SubmissionSuccessView

urlpatterns = [
    path('', LecturerListView.as_view(), name='lecturer-list'),
    path('submit/', SubmissionFormView.as_view(), name='submission-create'),
    path('submit/success/', SubmissionSuccessView.as_view(), name='submission-success'),
]
