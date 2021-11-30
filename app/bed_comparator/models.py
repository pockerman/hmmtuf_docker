from django.db import models
from django.core.files.storage import FileSystemStorage

from compute_engine.src.enumeration_types import JobType, JobResultEnum
from webapp_utils.model_utils import ComputationModel
from webapp_utils.helpers import make_bed_compare_filename_path, make_viterbi_compare_filename_path

from hmmtuf.config import BED_COMPARE_FILES_ROOT, USE_CELERY

from .tasks import compute_bed_comparison_task


def upload_bed_file(instance, filename: str):
    return BED_COMPARE_FILES_ROOT + filename


class BedComparisonModel(ComputationModel):

    # the type of the computation
    JOB_TYPE = JobType.BED_COMPARISON.name

    # the viterbi path
    viterbi_filename = models.CharField(max_length=1000)

    # the bed file
    bed_filename = models.CharField(max_length=1000)

    # the result file written
    result_filename = models.CharField(max_length=1000)

    # the summary filename
    summary_filename = models.CharField(max_length=1000)

    class Meta(ComputationModel.Meta):
        db_table = 'bed_comparison_computation'

    @staticmethod
    def compute(model) ->str:

        if USE_CELERY:
            # schedule the computation
            compute_bed_comparison_task.delay(task_id=model.task_id)
            return model.task_id
        else:
            compute_bed_comparison_task(task_id=model.task_id)
            return model.task_id

    def build_from_form(self, form, save: bool = True):
        # the object does not exist we can save the file

        self.computation_type = BedComparisonModel.JOB_TYPE
        self.result = JobResultEnum.PENDING.name
        self.result_filename = make_bed_compare_filename_path(task_id=self.task_id,
                                                              bed_name="result.csv")
        self.summary_filename = make_bed_compare_filename_path(task_id=self.task_id,
                                                               bed_name="summary.json")

        fs = FileSystemStorage(BED_COMPARE_FILES_ROOT)

        bed_fileloaded = form.get_bed_file()
        viterbi_fileloaded = form.get_viterbi_file()

        bed_fileloaded_path = make_bed_compare_filename_path(task_id=self.task_id,
                                                             bed_name=bed_fileloaded.name)

        filename = fs.save(bed_fileloaded_path, bed_fileloaded)
        self.bed_filename = bed_fileloaded_path

        viterbi_fileloaded_path = make_viterbi_compare_filename_path(task_id=self.task_id,
                                                                     viterbi_name=viterbi_fileloaded.name)

        filename = fs.save(viterbi_fileloaded_path, viterbi_fileloaded)
        self.viterbi_filename = viterbi_fileloaded_path

        if save:
            self.save()
        return self




