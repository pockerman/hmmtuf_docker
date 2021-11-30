from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name='index'),
    path('delete_task_directories/', views.delete_task_directories_view, name='delete_task_directories_view'),
    path('delete_region_files/', views.delete_region_files_view, name='delete_region_files_view'),
    path('delete_hmm_files/', views.delete_hmm_files_view, name='delete_hmm_files_view'),
]