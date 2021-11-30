from django.template import loader
from django.http import HttpResponse

from dash.dependencies import Input, Output
import dash

from db.sqlite3_db_connector import SQLiteDBConnector
from compute_engine.src.utils import get_sequence_name, get_tdf_file
from compute_engine.src.enumeration_types import JobResultEnum, JobType
from compute_engine.src.dash_helpers import create_figure_plot, get_layout

from compute_engine import INFO
from hmmtuf_compute import dash_viewer
from webapp_utils.helpers import make_bed_path
from webapp_utils.helpers import get_configuration
from hmmtuf.constants import INVALID_TASK_ID
from hmmtuf.config import DATABASES, MEDIA_URL
from hmmtuf_home.models import DistanceSequenceTypeModel, DistanceMetricTypeModel, RegionModel

from .models import ViterbiComputationModel, GroupViterbiComputationModel


def get_repeats_distances_plot(request):

    # we also need to add
    # a callback to check on the result
    @dash_viewer.repeats_plot_viewer.callback(Output("error-messages-id", component_property='children'),
                                              Output("normal-bar-chart", "figure"),
                                              Output("normal-n-distances", component_property='children'),
                                              Output("tuf-bar-chart", "figure"),
                                              Output("tuf-n-distances", component_property='children'),
                                              Output("core-bar-chart", "figure"),
                                              Output("core-n-distances", component_property='children'),
                                              [Input("dropdown-sequence", "value"),
                                               Input("dropdown-distance", "value"),
                                               Input("dropdown-gc-limit-type", "value"),
                                               Input("dropdown-gc-limit", "value"),
                                               Input("gc-limit-value", "value"),
                                               Input("compute-btn", "n_clicks")
                                               ])
    def update_bar_chart(seq_type, distance_type, gc_limit_type,
                         gc_limiter, gc_value, btn_clicked) -> tuple:

        print("{0} Calling callback= update_bar_chart... ".format(INFO))
        print("{0} {1} ".format(INFO, dash.callback_context.triggered))

        if len(dash.callback_context.triggered) == 0:
            btn_clicks = 0
        else:

            # get the changes
            changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

            # if the compute bth is in the changes
            # this means we triger a compute
            if 'compute-btn' in changed_id:
                btn_clicks = 1
            else:
                btn_clicks = 0

        print("{0} Button clicks={1}".format(INFO, btn_clicks))
        metric_type_id = distance_type
        sequence_type_id = seq_type
        error_message = ""

        figs_ids = [1, 2, 3]
        figs = []
        for fid in figs_ids:
            db_connector = SQLiteDBConnector(db_file=DATABASES["default"]["NAME"])
            db_connector.connect()
            error_message, fig, rows = create_figure_plot(state_type_id=fid,
                                                          metric_type_id=metric_type_id,
                                                          sequence_type_id=sequence_type_id,
                                                          gc_limit_type=gc_limit_type,
                                                          gc_limiter=gc_limiter,
                                                          gc_value=gc_value, btn_clicks=btn_clicks,
                                                          db_connector=db_connector)
            figs.append(fig)
            figs.append(rows)

        return error_message, figs[0], figs[1], figs[2], figs[3], figs[4], figs[5],

    seq_types = DistanceSequenceTypeModel.objects.all()
    dist_types = DistanceMetricTypeModel.objects.all()

    unique_seq_types = [(0, 'Select')]
    unique_dist_types = [(0, 'Select')]

    for i, x in enumerate(dist_types):
        unique_dist_types.append((i + 1, x.type))

    for i, x in enumerate(seq_types):
        unique_seq_types.append((i + 1, x.type))

    return get_layout(unique_seq_types=unique_seq_types, unique_dist_types=unique_dist_types)


def get_result_view_context(task, task_id):

    if task.result == JobResultEnum.FAILURE.name:
        context = {'error_task_failed': True,
                   "error_message": task.error_explanation,
                   'task_id': task_id, "computation": task, "MEDIA_URL": MEDIA_URL}
        return context
    elif task.result == JobResultEnum.PENDING.name:

        context = {'show_get_results_button': True,
                   'task_id': task_id,
                   'task_status': JobResultEnum.PENDING.name, "MEDIA_URL": MEDIA_URL}

        return context

    else:
        # this is success
        configuration = get_configuration()
        regions = RegionModel.objects.filter(group_tip__tip=task.group_tip).order_by('start_idx')

        chromosome = regions[0].chromosome

        wga_name = regions[0].wga_seq_file.split("/")[-1]
        wga_seq_name = get_sequence_name(configuration=configuration, seq=wga_name)
        wga_tdf_file = get_tdf_file(configuration=configuration, seq=wga_name)

        no_wga_name = regions[0].no_wga_seq_file.split("/")[-1]
        no_wga_seq_name = get_sequence_name(configuration=configuration, seq=no_wga_name)
        no_wga_tdf_file = get_tdf_file(configuration=configuration, seq=no_wga_name)

        context = {'task_status': task.result,
                   "computation": task,
                   "wga_seq_name": wga_seq_name,
                   "no_wga_seq_name": no_wga_seq_name,
                   "wga_tdf_file": wga_tdf_file,
                   "no_wga_tdf_file": no_wga_tdf_file,
                   "locus": chromosome,
                   "start_region_idx": task.start_region_idx,
                   "end_region_idx": task.end_region_idx, "MEDIA_URL": MEDIA_URL}

        if task.computation_type == JobType.VITERBI.name:

            # if we haven't asked for SPADE then
            # there is nothing to show on IGV. Just
            # show the download viterbi path button
            context["show_download_btn"] = True
            context['task_id'] = task_id

            if task.use_spade:
                context["use_spade"] = True
                context["normal_bed_url"] = make_bed_path(task_id=task_id, bed_name='normal.bed')
                context["tuf_bed_url"] = make_bed_path(task_id=task_id, bed_name='tuf.bed')
                context["deletion_bed_url"] = make_bed_path(task_id=task_id, bed_name="deletion.bed")
                context["duplication_bed_url"] = make_bed_path(task_id=task_id, bed_name="duplication.bed")
                context["gap_bed_url"] = make_bed_path(task_id=task_id, bed_name="gap.bed")
                context["repeats_bed_url"] = make_bed_path(task_id=task_id, bed_name="rep.bed")
                context["quad_bed_url"] = make_bed_path(task_id=task_id, bed_name="quad.bed")
                context["tdt_bed_url"] = make_bed_path(task_id=task_id, bed_name="tdt.bed")

            return context

        if task.computation_type == JobType.GROUP_VITERBI.name:

            context["normal_bed_url"] = make_bed_path(task_id=task_id, bed_name=chromosome + '/normal.bed')
            context["tuf_bed_url"] = make_bed_path(task_id=task_id, bed_name=chromosome + '/tuf.bed')
            context["deletion_bed_url"] = make_bed_path(task_id=task_id, bed_name=chromosome + '/deletion.bed')
            context["duplication_bed_url"] = make_bed_path(task_id=task_id, bed_name=chromosome + '/duplication.bed')
            context["gap_bed_url"] = make_bed_path(task_id=task_id, bed_name=chromosome + '/gap.bed')
            context["repeats_bed_url"] = make_bed_path(task_id=task_id, bed_name=chromosome + '/rep.bed')
            context["quad_bed_url"] = make_bed_path(task_id=task_id, bed_name=chromosome + '/quad.bed')
            context["tdt_bed_url"] = make_bed_path(task_id=task_id, bed_name=chromosome + '/tdt.bed')
            return context


def view_viterbi_path_exception_context(task, task_id, model=ViterbiComputationModel.__name__):

    context = {'task_status': task.status, "MEDIA_URL": MEDIA_URL}

    if task.status == JobResultEnum.PENDING.name:

        context.update({'show_get_results_button': True,
                        'task_id': task_id})

    elif task.status == JobResultEnum.SUCCESS.name:

        result = task.get()
        if model == ViterbiComputationModel.__name__:
            computation = ViterbiComputationModel.build_from_map(result, save=True)
            context.update({"computation": computation})
        elif model == GroupViterbiComputationModel.__name__:
            computation = GroupViterbiComputationModel.build_from_map(result, save=True)
            context.update({"computation": computation})
        else:
            raise ValueError("Model name: {0} not found".format(INFO, model))
    elif task.status == JobResultEnum.FAILURE.name:

        result = task.get(propagate=False)

        if model == ViterbiComputationModel.__name__:

            data_map = ViterbiComputationModel.get_invalid_map(task=task, result=result)
            computation = ViterbiComputationModel.build_from_map(data_map, save=True)
            context.update({'error_task_failed': True,
                            "error_message": str(result),
                            'task_id': task_id, "computation": computation})

        elif model == GroupViterbiComputationModel.__name__:

            result = task.get(propagate=False)
            data_map = GroupViterbiComputationModel.get_invalid_map(task=task, result=result)
            computation = GroupViterbiComputationModel.build_from_map(data_map, save=True)
            context.update({'error_task_failed': True,
                            "error_message": str(result),
                            'task_id': task_id,
                            "computation": computation})

        else:
            raise ValueError("Model name: {0} not found".format(INFO, model))

    return context


def handle_success_view(request, template_html, task_id, **kwargs):

    template = loader.get_template(template_html)

    context = {"task_id": task_id, "MEDIA_URL": MEDIA_URL}
    if task_id == INVALID_TASK_ID:
        error_msg = "Task does not exist"
        context.update({"error_msg": error_msg})

    if kwargs is not None:
        context.update(kwargs)

    return HttpResponse(template.render(context, request))



