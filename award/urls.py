from django.urls import path

from award.views import LecturerListView, add_submission, SubmissionSuccessView

urlpatterns = [
    path('', LecturerListView.as_view(), name='lecturer-list'),
    path('submit/', add_submission, name='add-submission'),
    path('submit/success/', SubmissionSuccessView.as_view(), name='submission-success'),
]
