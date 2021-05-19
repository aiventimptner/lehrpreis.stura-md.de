from django.urls import path

from . import views

urlpatterns = [
    path('', views.LecturerListView.as_view(), name='lecturer-list'),
    path('submit/', views.SubmissionFormView.as_view(), name='submission-create'),
    path('submit/success/', views.SubmissionSuccessView.as_view(), name='submission-success'),
    path('verify/<slug:token>/', views.verify_token, name='verify-token'),
]
