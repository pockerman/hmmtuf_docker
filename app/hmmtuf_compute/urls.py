from django.urls import path

from . import views

urlpatterns = [

    path('hmm_viterbi/',
         views.schedule_hmm_viterbi_compute_view, name='schedule_computation_view'),
    path('hmm_group_viterbi/',
         views.schedule_group_viterbi_compute_view, name='schedule_all_viterbi_compute_view'),

    path('view_viterbi_path/<str:task_id>/',
         views.view_viterbi_path, name='view_viterbi_path'),

    path('view_group_viterbi_path/<str:task_id>/',
         views.view_group_viterbi_path, name='view_group_viterbi_path'),

    path('success_schedule_viterbi_computation/<str:task_id>/',
         views.success_schedule_viterbi_compute_view, name='success_schedule_viterbi_computation_view'),

    path('success_schedule_group_viterbi_compute/<str:task_id>/',
         views.success_schedule_group_viterbi_compute_view, name='success_schedule_group_viterbi_compute_view'),

    path('repeats_distances_plot/',
         views.view_repeats_distances_plot, name='repeats_distances_plot'),

    path('viterbi_result_csv/<str:task_id>/',
         views.download_viterbi_result_csv, name=views.download_viterbi_result_csv.__name__),

]