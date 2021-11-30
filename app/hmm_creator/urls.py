from django.urls import path

from . import views

urlpatterns = [
    path('create_hmm/', views.create_hmm_view, name='create_hmm_view'),
    path('success_create_hmm/<str:hmm_name>/', views.success_create_hmm_view, name='success_create_hmm_view'),

]