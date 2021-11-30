import copy

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from compute_engine import INFO
from compute_engine.src.enumeration_types import JobType, JobResultEnum

from hmmtuf.config import USE_CELERY
from hmmtuf_home.models import ComputationModel
from hmmtuf_home.models import HMMModel
from hmmtuf_home.models import RegionGroupTipModel

from .tasks import compute_viterbi_path_task
from .tasks import compute_group_viterbi_path_task as v_group_path_task


class ViterbiComputationModelBase(ComputationModel):
    """
    Base class for Viterbi path calculation model
    """

    # the tip used for the computation
    group_tip = models.ForeignKey(RegionGroupTipModel, on_delete=models.CASCADE)

    # the hmm model used for the computation
    hmm = models.ForeignKey(HMMModel, on_delete=models.CASCADE)

    # start index of the first region in the group
    start_region_idx = models.IntegerField(null=True)

    # end index of the first region in the group
    end_region_idx = models.IntegerField(null=True)

    # flag indicating that the computation uses SPADE
    use_spade = models.BooleanField(default=False)

    class Meta(ComputationModel.Meta):
        abstract = True

    @staticmethod
    def get_as_map(model: object) -> dict:

        model_dict = copy.deepcopy(model.__dict__)
        if '_state' in model_dict:
            model_dict.pop('_state')
        return model_dict


class GroupViterbiComputationModel(ViterbiComputationModelBase):
    """
    Represents a group Viterbi computation task in the DB
    All fields are NULL by default as the computation may fail
    before computing the relevant field. Instances of this class
    are created by the tasks.compute_viterbi_path_task
    which tries to fill in as many fields as possible. Upon successful
    completion of the task all fields should have valid values
    """

    # the type of the computation
    JOB_TYPE = JobType.GROUP_VITERBI.name

    class Meta(ComputationModel.Meta):
        db_table = 'group_viterbi_computation'

    @staticmethod
    def build_from_map(map_data, save):

        try:
            computation = GroupViterbiComputationModel.objects.get(task_id=map_data["task_id"])
            return computation
        except ObjectDoesNotExist:

            computation = ViterbiComputationModel()
            computation.task_id = map_data["task_id"]
            computation.result = map_data["result"]
            computation.error_explanation = map_data["error_explanation"]
            computation.computation_type = GroupViterbiComputationModel.JOB_TYPE
            computation.hmm_name = map_data["hmm_name"]
            computation.group_tip = map_data["group_tip"]
            computation.start_region_idx = map_data["start_region_idx"]
            computation.end_region_idx = map_data["end_region_idx"]

            if save:
                computation.save()
                print("{0} saved computation: {1}".format(INFO, map_data["task_id"]))
            return computation

    @staticmethod
    def compute(data):

        hmm_name = data['hmm_name']

        if USE_CELERY:
            # schedule the computation
            task = v_group_path_task.delay(hmm_name=hmm_name, group_tip=data["group_tip"],
                                           remove_dirs=data["remove_dirs"], use_spade=data["use_spade"])

            return task.id
        else:

            import uuid
            task_id = str(uuid.uuid4())
            v_group_path_task(task_id=task_id, hmm_name=hmm_name,
                              group_tip=data["group_tip"], remove_dirs=data["remove_dirs"],
                              use_spade=data["use_spade"])
            return task_id

    @staticmethod
    def get_invalid_map(task, result):
        data_map = dict()

        data_map["task_id"] = task.id
        data_map["result"] = JobResultEnum.FAILURE.name
        data_map["error_explanation"] = str(result)
        data_map["computation_type"] = JobType.GROUP_VITERBI.name
        data_map["hmm_filename"] = result["hmm_filename"]
        data_map["group_tip"] = result["group_tip"]
        data_map["start_region_idx"] = result["start_region_idx"]
        data_map["end_region_idx"] = result["end_region_idx"]
        return data_map


class ViterbiComputationModel(ViterbiComputationModelBase):
    """
    DB model for a Viterbi computation task
    All fields are NULL by default as the computation may fail
    before computing the relevant field. Instances of this class
    are created by the tasks.compute_viterbi_path_task
    which tries to fill in as many fields as possible. Upon successful
    completion of the task all fields should have valid values
    """

    # the type of the computation
    JOB_TYPE = JobType.VITERBI.name

    class Meta(ComputationModel.Meta):
        db_table = 'viterbi_computation'

    @staticmethod
    def build_from_map(map_data, save):

        """
        Build a ViterbiComputationModel model from map data
        """
        try:
            computation = ViterbiComputationModel.objects.get(task_id=map_data["task_id"])
            return computation
        except ObjectDoesNotExist:

            computation = ViterbiComputationModel()
            computation.task_id = map_data["task_id"]
            computation.result = map_data["result"]
            computation.error_explanation = map_data["error_explanation"]
            computation.computation_type = ViterbiComputationModel.JOB_TYPE
            computation.hmm = map_data["hmm"]
            computation.group_tip = map_data["group_tip"]
            computation.start_region_idx = map_data["start_region_idx"]
            computation.end_region_idx = map_data["end_region_idx"]

            if save:
                computation.save()
                print("{0} saved computation: {1}".format(INFO, map_data["task_id"]))
            return computation

    @staticmethod
    def compute(data):

        hmm_name = data['hmm_name']
        region_filename = data['region_filename']

        if USE_CELERY:

            # schedule the computation
            task = compute_viterbi_path_task.delay(region_filename=region_filename,
                                                   hmm_name=hmm_name,  remove_dirs=data["remove_dirs"],
                                                   use_spade=data["use_spade"])
            return task.id
        else:

            import uuid
            from .tasks import compute_viterbi_path
            task_id = str(uuid.uuid4())
            compute_viterbi_path(task_id=task_id,
                                 region_filename=region_filename, hmm_name=hmm_name,
                                 remove_dirs=data["remove_dirs"], use_spade=data["use_spade"], )
            return task_id

    @staticmethod
    def get_invalid_map(task, result) -> dict:
        data_map = dict()

        data_map["task_id"] = task.id
        data_map["result"] = JobResultEnum.FAILURE.name
        data_map["error_explanation"] = str(result)
        data_map["computation_type"] = JobType.VITERBI.name
        data_map["hmm"] = result["hmm"]
        return data_map
