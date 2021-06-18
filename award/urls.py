from django.urls import path

from . import views

urlpatterns = [
    path('', views.LecturerListView.as_view(), name='lecturer-list'),
    path('lecturer/', views.LecturerSelectView.as_view(), name='lecturer-select'),
    path('lecturer/<int:pk>/', views.LecturerDetailView.as_view(), name='lecturer-detail'),
    path('renew/', views.RenewTokenView.as_view(), name='renew-token'),
    path('renew/success/', views.RenewTokenSuccessView.as_view(), name='renew-token-success'),
    path('submit/', views.SubmissionFormView.as_view(), name='submission-create'),
    path('submit/success/', views.SubmissionSuccessView.as_view(), name='submission-success'),
    path('verify/<slug:token>/', views.verify_token, name='verify-token'),
]
