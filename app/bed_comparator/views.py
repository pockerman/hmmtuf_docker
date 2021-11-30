import uuid
import os
from pathlib import Path
import mimetypes

from django.shortcuts import render
from django.shortcuts import redirect
from django.template import loader
from django.http import HttpResponse
from django.http import Http404
from django.contrib.auth.decorators import login_required



from compute_engine import OK
from compute_engine.src.utils import read_json
from webapp_utils.helpers import make_bed_compare_path
from .forms import LoadBedFile
from .models import BedComparisonModel


template_ids = dict()
template_ids['load_bed_file_view'] = 'bed_comparator/load_bed_file_view.html'
template_ids['success_load_bed_view'] = 'bed_comparator/success_schedule_bed_compute_view.html'


@login_required(login_url='/hmmtuf_login/login/')
def load_bed_file_view(request):

    template = loader.get_template(template_ids[load_bed_file_view.__name__])
    if request.method == 'POST':

        form = LoadBedFile(template_html=template)
        if form.check(request=request) is not OK:
            return form.response

        kwargs = form.as_dict()

        # generate a new task id
        task_id = str(uuid.uuid4())

        dir_path = make_bed_compare_path(task_id=task_id)

        try:
            os.makedirs(name=dir_path)
        except Exception as e:
            print(str(e))
            raise e

        print(kwargs['bed_filename'].temporary_file_path())
        print(kwargs['bed_filename'].name)

        # generate a new model and save
        model = BedComparisonModel()
        model.task_id = task_id

        # build a DB model to monitor
        model = model.build_from_form(form=form, save=True)

        # schedule the computation
        BedComparisonModel.compute(model)

        return redirect('success_load_bed_view', task_id=task_id)

    return HttpResponse(template.render({"error_name_exist": "The HMM name exists"}, request))


@login_required(login_url='/hmmtuf_login/login/')
def success_load_bed_view(request, task_id: str) -> HttpResponse:
    """
    Serves the success or pending view for
    a bed comparison computation. The computation is
    identified by the task_id
    """
    template = loader.get_template(template_ids[success_load_bed_view.__name__])

    try:

        # check if computation finished
        model = BedComparisonModel.objects.get(task_id=task_id)
    except BedComparisonModel.DoesNotExist as e:
        raise Http404(f"Task {task_id} does not exist")

    if model.pending():
        return HttpResponse(template.render({"show_get_results_button": True,
                                             "task_id": task_id,
                                             "task_status": model.result}, request))
    elif model.failed():
        return HttpResponse(template.render({"error_task_failed": True, "task_id": task_id,
                                             "error_explanation": model.error_explanation}, request))

    # the task has finished. load the
    # summary
    summary_filename = model.summary_filename

    try:
        summary = read_json(filename=Path(summary_filename))
    except Exception as e:
        Http404(str(e))

    total = 0
    for key in summary:
        total += summary[key]

    if total != 0:
        for key in summary:
            summary[key] = (summary[key], (float(summary[key]) / float(total))*100.0)

    return HttpResponse(template.render({"summary": summary,
                                         "total": total, "task_id": task_id}, request))


@login_required(login_url='/hmmtuf_login/login/')
def download_bed_result_csv(request, task_id):
    """
    Manages the download request
    """

    try:
        # check if computation finished
        model = BedComparisonModel.objects.get(task_id=task_id)
    except BedComparisonModel.DoesNotExist as e:
        raise Http404(f"Task {task_id} does not exist")

    result_filename = model.result_filename

    try:
        # open file for read
        path = open(result_filename, 'r')
    except Exception as e:
        raise Http404(str(e))

    # Set the mime type
    mime_type, _ = mimetypes.guess_type(result_filename)

    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)

    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % 'result.csv'
    return response




