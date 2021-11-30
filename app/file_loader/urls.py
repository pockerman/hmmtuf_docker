from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('load_hmm/', views.load_hmm_json_view, name='load_hmm_json_view'),
    path('load_region/', views.load_region_view, name='load_region_view'),
    path('success_load_hmm/<str:hmm_name>/', views.success_load_view_hmm, name='success_load_view_hmm'),
    path('success_load_region/<str:region_name>/', views.success_load_view_region, name='success_load_view_region'),
]