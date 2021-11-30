from django.urls import path

from . import views

urlpatterns = [

    path('load_bed/', views.load_bed_file_view, name=views.load_bed_file_view.__name__),
    path('success_load_bed/<str:task_id>/', views.success_load_bed_view, name=views.success_load_bed_view.__name__),
    path('result_csv/<str:task_id>/result/', views.download_bed_result_csv, name=views.download_bed_result_csv.__name__)
]