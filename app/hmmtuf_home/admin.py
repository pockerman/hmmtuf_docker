from django.contrib import admin

from .models import HMMModel
from .models import RegionModel
from .models import RegionGroupTipModel
from .models import ViterbiSequenceModel
from .models import DistanceMetricTypeModel
from .models import DistanceSequenceTypeModel
from .models import RepeatsModel
from .models import RepeatsDistancesModel
from .models import HHMStateTypesModel


class HMMModelAdmin(admin.ModelAdmin):
    fields = ['name', 'file_hmm']
    list_display = ('name', 'file_hmm')


class RegionModelAdmin(admin.ModelAdmin):
    fields = ['name', 'chromosome', 'chromosome_index',
              'file_region', 'ref_seq_file', 'wga_seq_file', 'no_wga_seq_file',
              'start_idx', 'end_idx', 'group_tip']
    list_display = ('name', 'chromosome', 'start_idx', 'end_idx', 'group_tip')


class RegionGroupTipModelAdmin(admin.ModelAdmin):
    fields = ['tip', 'chromosome']
    list_display = ('id', 'tip', 'chromosome')


class ViterbiSequenceModelAdmin(admin.ModelAdmin):
    fields = ['group_tip', 'file_sequence']
    list_display = ('id', 'group_tip', 'file_sequence', 'region')


class DistanceMetricTypeAdmin(admin.ModelAdmin):
    fields = ['type', 'short_cut', ]
    list_display = ('type', 'short_cut')


class DistanceSequenceTypeAdmin(admin.ModelAdmin):
    fields = ['type', ]
    list_display = ('type',)


class RepeatsAdmin(admin.ModelAdmin):
    fields = ['chromosome',  'start_idx', 'end_idx', 'hmm_state_id', 'gc', 'repeat_seq', ]
    list_display = ('chromosome',  'start_idx', 'end_idx', 'hmm_state_id', 'gc', 'repeat_seq')


class RepeatsDistancesAdmin(admin.ModelAdmin):
    fields = ['repeat_idx_1', 'repeat_idx_2', 'hmm_state_idx_1',
              'hmm_state_idx_2',  'value', 'metric_type_id', 'sequence_type_id', 'is_normalized']
    list_display = ('repeat_idx_1', 'repeat_idx_2', 'hmm_state_idx_1',
                     'hmm_state_idx_2',  'value', 'metric_type_id', 'sequence_type_id', 'is_normalized')


class HHMStateTypesModelAdmin(admin.ModelAdmin):
    fields = ['type', ]
    list_display = ('type', )


admin.site.register(DistanceMetricTypeModel, DistanceMetricTypeAdmin)
admin.site.register(DistanceSequenceTypeModel, DistanceSequenceTypeAdmin)
admin.site.register(RepeatsModel, RepeatsAdmin)
admin.site.register(RepeatsDistancesModel, RepeatsDistancesAdmin)
admin.site.register(HMMModel, HMMModelAdmin)
admin.site.register(RegionModel, RegionModelAdmin)
admin.site.register(RegionGroupTipModel, RegionGroupTipModelAdmin)
admin.site.register(ViterbiSequenceModel, ViterbiSequenceModelAdmin)
admin.site.register(HHMStateTypesModel, HHMStateTypesModelAdmin)
