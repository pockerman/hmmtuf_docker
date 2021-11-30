from django.db import models
from django.core.files.storage import FileSystemStorage

from compute_engine.src.enumeration_types import JobResultEnum
from compute_engine import DEFAULT_ERROR_EXPLANATION
from webapp_utils.model_utils import ComputationModel
from hmmtuf.config import REGIONS_FILES_ROOT
from hmmtuf.config import HMM_FILES_ROOT


def upload_hmm_file(instance, filename):
    return HMM_FILES_ROOT + filename #'/'.join(['content', instance.user.username, filename])


def upload_region_file(instance, filename):
    return REGIONS_FILES_ROOT + filename #'/'.join(['content', instance.user.username, filename])


class FilesModel(models.Model):
    """
    Abstract DB model for files
    """

    # a user defined name to distinguish
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "%s " % self.name


class HMMModel(FilesModel):
    """
    DB HMM model
    """

    file_hmm = models.FileField(upload_to=upload_hmm_file)

    class Meta(FilesModel.Meta):
        db_table = 'hmm_model'
        constraints = [
            models.UniqueConstraint(fields=['name', ], name='HMM unique  name constraint')
        ]

    def __str__(self):
        return "%s %s" % (self.name, self.file_hmm)

    @staticmethod
    def build_from_form(inst, form, save=True):
        # the object does not exist we can save the file
        file_loaded = form.file_loaded
        fs = FileSystemStorage(HMM_FILES_ROOT)
        file_loaded_name = form.name + '.json'
        filename = fs.save(file_loaded_name, file_loaded)

        inst.file_hmm = HMM_FILES_ROOT + file_loaded_name
        inst.name = form.name
        inst.extension = 'json'

        if save:
            inst.save()
        return inst


class RegionGroupTipModel(models.Model):

    # tip used to group region models
    tip = models.CharField(max_length=100, null=False, unique=True)

    # chromosome of the region group
    chromosome = models.CharField(max_length=10, null=False, unique=True)

    class Meta:
        db_table = 'region_group_tip'

    def __str__(self):
        return "%s" % self.tip


class RegionModel(FilesModel):
    """
    DB Region model
    """

    # the file representing the region
    file_region = models.FileField(upload_to=upload_region_file, null=False)

    # the chromosome of the region
    chromosome = models.CharField(max_length=10, null=False)
    chromosome_index = models.IntegerField(default=-1, null=False)

    # files used to extract the region
    ref_seq_file = models.CharField(max_length=1000, null=False)
    wga_seq_file = models.CharField(max_length=1000, null=False)
    no_wga_seq_file = models.CharField(max_length=1000, null=False)

    # global start index of the region
    start_idx = models.IntegerField(null=False)

    # global end index of the region
    end_idx = models.IntegerField(null=False)

    # group the region belongs to
    group_tip = models.ForeignKey(RegionGroupTipModel, on_delete=models.CASCADE, null=False)

    class Meta(FilesModel.Meta):
        db_table = 'region_model'
        constraints = [
            models.UniqueConstraint(fields=['name', ], name='Region unique  name constraint')
        ]

    def __str__(self):
        return "%s %s" % (self.name, self.file_region)

    @staticmethod
    def build_from_form(inst, form, save=True):

        # the object does not exist we can save the file
        file_loaded = form.file_loaded
        fs = FileSystemStorage(REGIONS_FILES_ROOT)

        file_loaded_name = form.name + '_' + form.chromosome + '_' + str(form.start_idx)
        file_loaded_name += '_' + str(form.end_idx) + '.txt'
        filename = fs.save(file_loaded_name, file_loaded)

        inst.name = form.name
        inst.file_region = REGIONS_FILES_ROOT + file_loaded_name
        inst.name = form.name
        inst.extension = 'txt'
        inst.chromosome = form.chromosome
        inst.ref_seq_file = form.ref_seq_filename
        inst.wga_seq_file = form.wga_seq_filename
        inst.no_wga_seq_file = form.no_wga_seq_filename
        inst.start_idx = form.start_idx
        inst.end_idx = form.end_idx
        inst.chromosome_index = form.chromosome_idx

        if save:
            inst.save()
        return inst


class ViterbiSequenceModel(models.Model):

    # the group tip
    group_tip = models.ForeignKey(RegionGroupTipModel, on_delete=models.CASCADE, null=False)

    # the file representing the region
    file_sequence = models.FileField(null=False)

    # region name
    region = models.ForeignKey(RegionModel, on_delete=models.CASCADE, null=False)

    class Meta:
        db_table = 'viterbi_seq_model'

    def __str__(self):
        return "%s" % self.group_tip


class BackendTypeModel(models.Model):
    """
    DB model for the backend used for computations
    """

    type_name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'backend_type_model'

    def __str__(self):
        return "%s" % self.type_name


class DistanceMetricTypeModel(models.Model):
    """
    DB model for distance metric types
    """

    # string describing the class name
    # of the metric
    type = models.CharField(max_length=100, unique=True)

    # short name to refer to the metric
    short_cut = models.CharField(max_length=50, unique=True, default="INVALID")

    class Meta:
        db_table = 'distance_metric_type'

    def __str__(self):
        return "%s " % self.type


class DistanceSequenceTypeModel(models.Model):
    """
    DB model for distance sequence type
    """

    CHOICES = [("NORMAL", "NORMAL"),
               ("PURINE", "PURINE"),
               ("AMINO", "AMINO"),
               ("WEAK_HYDROGEN", "WEAK_HYDROGEN"), ]

    # a user defined name to distinguish
    type = models.CharField(max_length=100, unique=True, choices=CHOICES)

    class Meta:
        db_table = 'distance_sequence_type'

    def __str__(self):
        return "%s " % self.type


class HHMStateTypesModel(models.Model):
    """
    DB model for HMM state types
    """

    type = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'hmm_state_types'

    def __str__(self):
        return "%s " % self.type


class RepeatsModel(models.Model):
    """
    DB model for repeats
    """
    # the chromosome
    chromosome = models.CharField(max_length=100, unique=False)

    # the start index
    start_idx = models.IntegerField(unique=False)

    # the end index
    end_idx = models.IntegerField(unique=False)

    # the repeat sequence
    repeat_seq = models.CharField(max_length=500)

    # the state of the repeat comming from HMM
    hmm_state_id = models.ForeignKey(HHMStateTypesModel, on_delete=models.CASCADE)

    # gc percentage
    gc = models.FloatField(default=0.0)

    # min GC
    gc_min = models.FloatField(default=0.0)

    # max GC
    gc_max = models.FloatField(default=0.0)

    # whether the region contains repeats
    has_repeats = models.BooleanField(default=False)

    # number of repeats
    n_repeats = models.IntegerField(default=0)

    # the alignement sequence
    align_seq = models.CharField(max_length=500, default=None)

    # unit seq sequence
    unit_seq = models.CharField(max_length=500, default=None)

    class Meta:
        db_table = 'repeats'


class RepeatsDistancesModel(models.Model):
    """
    DB model for distances between the repeats
    """

    # the start index
    repeat_idx_1 = models.ForeignKey(RepeatsModel, on_delete=models.CASCADE,
                                     related_name='%(class)s_repeat_idx_1',
                                     default=None)

    # the end index
    repeat_idx_2 = models.ForeignKey(RepeatsModel, on_delete=models.CASCADE,
                                     related_name='%(class)s_repeat_idx_2',
                                     default=None)

    # the start index
    hmm_state_idx_1 = models.ForeignKey(HHMStateTypesModel, on_delete=models.CASCADE,
                                        related_name='%(class)s_hmm_state_idx_1',
                                        default=None)

    # the end index
    hmm_state_idx_2 = models.ForeignKey(HHMStateTypesModel, on_delete=models.CASCADE,
                                        related_name='%(class)s_hmm_state_idx_2',
                                        default=None)

    # the metric value computed
    value = models.FloatField()

    # the metric type used for the calculation
    metric_type_id = models.ForeignKey(DistanceMetricTypeModel, on_delete=models.CASCADE)

    # whether the calculation is based on
    # the original repeats NORMAL or the formed purine group PURINE
    # or amino group AMINO or weak hydrogen bond group WEAK_HYDROGEN
    sequence_type_id = models.ForeignKey(DistanceSequenceTypeModel, on_delete=models.CASCADE)

    # flag indicating if the metric is normalized
    is_normalized = models.BooleanField(default=True)

    class Meta:
        db_table = 'repeats_distances'








