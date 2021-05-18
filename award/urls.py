from django.urls import path

from .views import LecturerListView, SubmissionFormView, SubmissionSuccessView, verify_token

urlpatterns = [
    path('', LecturerListView.as_view(), name='lecturer-list'),
    path('submit/', SubmissionFormView.as_view(), name='submission-create'),
    path('submit/success/', SubmissionSuccessView.as_view(), name='submission-success'),
    path('verify/<slug:token>/', verify_token, name='verify-token'),
]
