# Import mimetypes module
import mimetypes

from django.http import HttpResponse
from django.http import Http404
from django.template import loader
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from compute_engine.src.windows import WindowType
from compute_engine import OK

from webapp_utils.helpers import make_viterbi_path_filename
from hmmtuf.constants import INVALID_TASK_ID, INVALID_ITEM
from hmmtuf.config import ENABLE_SPADE, MEDIA_URL
from hmmtuf.celery import celery_app
from hmmtuf_home.models import HMMModel, RegionModel, RegionGroupTipModel
from hmmtuf_compute import dash_viewer

from . import models
from . import forms
from . view_helpers import get_result_view_context
from . view_helpers import view_viterbi_path_exception_context
from . view_helpers import handle_success_view, get_repeats_distances_plot


def success_schedule_group_viterbi_compute_view(request, task_id):

    template_html = 'hmmtuf_compute/success_schedule_group_viterbi_compute_view.html'
    return handle_success_view(request=request,
                               template_html=template_html, task_id=task_id)


def success_schedule_viterbi_compute_view(request, task_id):
    """
    Success redirect after scheduling a Viterbi path computation
    """

    template_html = 'hmmtuf_compute/success_schedule_viterbi_compute_view.html'
    return handle_success_view(request=request,
                               template_html=template_html, task_id=task_id)


@login_required(login_url='/hmmtuf_login/login/')
def schedule_group_viterbi_compute_view(request):
    """
    Serve the view for scheduling viterbi computations
    for Groups for example compute the Viterbi path
    for chromosome 1
    """
    template_html = 'hmmtuf_compute/schedule_group_viterbi_compute_view.html'
    template = loader.get_template(template_html)

    # get the hmms we have
    hmms = HMMModel.objects.all()

    if len(hmms) == 0:
        context = {"error_empty_hmm_list": "HMM models have not been created."}
        template = loader.get_template(template_html)
        return HttpResponse(template.render(context, request))

    db_group_tips = RegionGroupTipModel.objects.all()
    if len(db_group_tips) == 0:
        context = {"no_group_list": "Chromosome groups have not been created."}
        template = loader.get_template(template_html)
        return HttpResponse(template.render(context, request))

    hmm_names = []
    for item in hmms:
        hmm_names.append(item.name)

    context = {"hmm_names": hmm_names,
               "group_tips": db_group_tips, "MEDIA_URL": MEDIA_URL}

    if ENABLE_SPADE:
        context.update({"use_spade": True})

    if request.method == 'POST':

        form = forms.GroupViterbiComputeForm(template_html=template_html, context=context)

        result = form.check(request=request)
        if result is not OK:
            return form.response

        kwargs = form.kwargs
        task_id = models.GroupViterbiComputationModel.compute(data=kwargs)

        # return the id for the computation
        return redirect('success_schedule_group_viterbi_compute_view', task_id=task_id)

    return HttpResponse(template.render(context, request))


@login_required(login_url='/hmmtuf_login/login/')
def view_group_viterbi_path(request, task_id):

    """
    View the Viterbi path of a multi-region computation
    """

    template_html = 'hmmtuf_compute/group_viterbi_result_view.html'
    template = loader.get_template(template_html)

    try:

        # if the task exists do not ask celery. This means
        # that either the task failed or succeed
        task = models.GroupViterbiComputationModel.objects.get(task_id=task_id)
        context = get_result_view_context(task=task, task_id=task_id)
        return HttpResponse(template.render(context, request))

    except ObjectDoesNotExist:

        # try to ask celery
        # check if the computation is ready
        # if yes collect the results
        # otherwise return the html
        task = celery_app.AsyncResult(task_id)

        if task is None:
            return success_schedule_group_viterbi_compute_view(request, task_id=INVALID_TASK_ID)

        context = view_viterbi_path_exception_context(task=task, task_id=task_id,
                                                      model=models.GroupViterbiComputationModel.__name__)
        return HttpResponse(template.render(context, request))


@login_required(login_url='/hmmtuf_login/login/')
def schedule_hmm_viterbi_compute_view(request):
    """
    Schedule a region Viterbi computation.
    """

    # the view html file
    template_html = 'hmmtuf_compute/schedule_viterbi_compute_view.html'
    template = loader.get_template(template_html)

    db_group_tips = RegionGroupTipModel.objects.all().order_by('tip')
    group_tips = ["None"]

    for item in db_group_tips:
        group_tips.append(item.tip)

    # get the hmms we have
    hmms = HMMModel.objects.all()

    if len(hmms) == 0:
        context = {"error_empty_hmm_list": "HMM models have not been created.", "MEDIA_URL": MEDIA_URL}
        template = loader.get_template(template_html)
        return HttpResponse(template.render(context, request))

    hmm_names = []
    for item in hmms:
        hmm_names.append(item.name)

    # get the regions we have
    regions = RegionModel.objects.all().order_by('chromosome', 'name')

    if len(regions) == 0:
        context = {"error_empty_region_list": "Regions have not been created.", }
        template = loader.get_template(template_html)
        return HttpResponse(template.render(context, request))

    region_names = []
    for item in regions:
        region_names.append(item.name)

    context = {"region_names": region_names,
               "hmm_names": hmm_names,
               'window_names': WindowType.get_window_types(),
               "sequence_groups": group_tips, "MEDIA_URL": MEDIA_URL}

    if ENABLE_SPADE:
        context.update({"use_spade": True})

    if request.method == 'POST':

        form = forms.ViterbiComputeForm(template_html=template_html,
                                        configuration=INVALID_ITEM,
                                        context=context)

        if form.check(request=request) is not OK:
            return form.response

        task_id = models.ViterbiComputationModel.compute(data=form.kwargs)

        # return the id for the computation
        return redirect('success_schedule_viterbi_computation_view', task_id=task_id)

    return HttpResponse(template.render(context, request))


@login_required(login_url='/hmmtuf_login/login/')
def view_viterbi_path(request, task_id):
    """
    Render the computed Viterbi path
    """
    template_html = 'hmmtuf_compute/viterbi_result_view.html'
    template = loader.get_template(template_html)
    try:

        # if the task exists do not ask celery. This means
        # that either the task failed or succeed
        task = models.ViterbiComputationModel.objects.get(task_id=task_id)
        context = get_result_view_context(task=task, task_id=task_id)
        return HttpResponse(template.render(context, request))
    except ObjectDoesNotExist:

        # try to ask celery
        # check if the computation is ready
        # if yes collect the results
        # otherwise return the html
        task = celery_app.AsyncResult(task_id)
        context = view_viterbi_path_exception_context(task=task, task_id=task_id)
        return HttpResponse(template.render(context, request))


@login_required(login_url='/hmmtuf_login/login/')
def view_repeats_distances_plot(request):
    """
    Serves the view for Dash based view for
    plotting repeats distances
    """

    dash_viewer.repeats_plot_viewer.layout = get_repeats_distances_plot(request=request)
    return redirect(to="/django_plotly_dash/app/repeats_plot_viewer_app/")


@login_required(login_url='/hmmtuf_login/login/')
def download_viterbi_result_csv(request, task_id: str, filename: str = 'viterbi_path.csv') -> HttpResponse:

    try:
        # check if computation finished
        model = models.ViterbiComputationModel.objects.get(task_id=task_id)
    except models.ViterbiComputationModel.DoesNotExist as e:
        raise Http404(f"Task {task_id} does not exist")

    result_filename = make_viterbi_path_filename(task_id=task_id)

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
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response



