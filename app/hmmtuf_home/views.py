import os
import shutil


from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.contrib import messages
from django.views.defaults import page_not_found
from django.views.defaults import server_error
from django.contrib.auth.decorators import login_required

from compute_engine.src.enumeration_types import JobResultEnum
from compute_engine import ERROR
from hmmtuf.config import VITERBI_PATHS_FILES_ROOT
from hmmtuf.config import DB_NAME, MEDIA_URL
from hmmtuf_compute.models import GroupViterbiComputationModel, ViterbiComputationModel
from .models import RegionModel
from .models import HMMModel
from .models import DistanceMetricTypeModel

template_ids = dict()
template_ids['home_view'] = 'hmmtuf_home/index.html'
template_ids['delete_region_files_view'] = 'hmmtuf_home/delete_region_files_view.html'
template_ids['delete_hmm_files_view'] = 'hmmtuf_home/delete_hmm_files_view.html'
template_ids['page_not_found_handler'] = '404.html'
template_ids['server_error_handler'] = '500.html'


def home_view(request) -> HttpResponse:
    """
    Index page view
    """

    template = loader.get_template(template_ids['home_view'])

    n_regions = 0
    n_hmm_models = 0
    n_tasks = 0
    n_success_tasks = 0
    n_failed_tasks = 0
    n_pending_tasks = 0
    n_dist_metrics = 0

    try:
        n_regions = RegionModel.objects.count()
        n_hmm_models = HMMModel.objects.count()
        n_tasks = GroupViterbiComputationModel.objects.count()
        n_tasks += ViterbiComputationModel.objects.count()
        n_success_tasks = len(GroupViterbiComputationModel.objects.filter(result=JobResultEnum.SUCCESS.name))
        n_success_tasks += len(ViterbiComputationModel.objects.filter(result=JobResultEnum.SUCCESS.name))
        n_failed_tasks = len(GroupViterbiComputationModel.objects.filter(result=JobResultEnum.FAILURE.name))
        n_failed_tasks += len(ViterbiComputationModel.objects.filter(result=JobResultEnum.FAILURE.name))
        n_pending_tasks = len(GroupViterbiComputationModel.objects.filter(result=JobResultEnum.PENDING.name))
        n_pending_tasks += len(ViterbiComputationModel.objects.filter(result=JobResultEnum.PENDING.name))
        n_dist_metrics = len(DistanceMetricTypeModel.objects.all())
    except Exception as e:
        print(f"{ERROR} DB error {str(e)}")

    context = {"db_name": DB_NAME,
                "n_regions": n_regions,
               "n_dist_metrics": n_dist_metrics,
               "n_hmm_models": n_hmm_models,
               "n_total_tasks": n_tasks,
               "n_success_tasks": n_success_tasks,
               "n_failed_tasks": n_failed_tasks,
               "n_pending_tasks": n_pending_tasks,
               "index_page": True, "MEDIA_URL": MEDIA_URL}
    return HttpResponse(template.render(context, request))


@login_required(login_url='/hmmtuf_login/login/')
def delete_region_files_view(request):
    template_html = 'hmmtuf_home/delete_region_files_view.html'
    context = {}
    if request.method == 'POST':

        models = RegionModel.objects.all()
        counter = 0
        for model in models:

            filename = model.file_region.name
            try:

                os.remove(filename)
                model.delete()
                counter += 1
            except Exception as e:
                messages.error(request, "Attempt to remove region "
                                        "file {0} failed".format(filename))
                return redirect("index")

        if counter == 0:
            messages.info(request, "No region files to remove")
        else:
            messages.info(request, "Successfully removed {0} region files".format(counter))
        return redirect("index")

    template = loader.get_template(template_html)
    return HttpResponse(template.render(context, request))


@login_required(login_url='/hmmtuf_login/login/')
def delete_hmm_files_view(request):
    template_html = 'hmmtuf_home/delete_hmm_files_view.html'
    context = {}
    if request.method == 'POST':

        models = HMMModel.objects.all()
        counter = 0
        for model in models:

            filename = model.file_hmm.name
            try:

                os.remove(filename)
                model.delete()
                counter += 1
            except Exception as e:
                messages.error(request, "Attempt to remove HMM "
                                        "file {0} failed".format(filename))
                return redirect("index")

        if counter == 0:
            messages.info(request, "No HMM files to remove")
        else:
            messages.info(request, "Successfully removed {0} HMM files".format(counter))
        return redirect("index")

    template = loader.get_template(template_html)
    return HttpResponse(template.render(context, request))


@login_required(login_url='/hmmtuf_login/login/')
def delete_task_directories_view(request):

    template_html = 'hmmtuf_home/delete_task_directories_view.html'
    context = {}
    if request.method == 'POST':

        tasks = list(GroupViterbiComputationModel.objects.all())
        tasks.extend(list(ViterbiComputationModel.objects.all()))
        delete_ids = []
        counter = 0
        for task in tasks:
            task_id = task.task_id.replace('-', '_')
            if os.path.isdir(VITERBI_PATHS_FILES_ROOT + task_id):
                print(VITERBI_PATHS_FILES_ROOT + task_id)
                shutil.rmtree(os.path.join(VITERBI_PATHS_FILES_ROOT, task_id))
                counter += 1

            delete_ids.append(task.task_id)

        GroupViterbiComputationModel.objects.all().delete()
        ViterbiComputationModel.objects.all().delete()
        
        if counter == 0:
            messages.info(request, "No directories to remove".format(counter))
        else:
            messages.info(request, "Successfully removed {0} directories".format(counter))
        return redirect("index")

    template = loader.get_template(template_html)
    return HttpResponse(template.render(context, request))


def page_not_found_handler(request, exception):
    return page_not_found(request=request,
                          exception=exception,
                          template_name=template_ids[page_not_found_handler.__name__])


def server_error_handler(request):
    return server_error(request=request, template_name=template_ids[server_error_handler.__name__])


