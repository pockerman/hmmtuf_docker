from django.contrib import admin

# Register your models here.

# Register your models here.
from .models import ViterbiComputationModel
from .models import GroupViterbiComputationModel


class ViterbiComputationAdmin(admin.ModelAdmin):
    fields = ['task_id',  'result', 'error_explanation', 'group_tip', 'computation_type']
    list_display = ('task_id', 'result', 'error_explanation')


class GroupViterbiComputationAdmin(admin.ModelAdmin):
    fields = ['task_id', 'result', 'error_explanation', 'group_tip', 'computation_type']
    list_display = ('task_id', 'result', 'error_explanation', 'group_tip')


admin.site.register(ViterbiComputationModel, ViterbiComputationAdmin)
admin.site.register(GroupViterbiComputationModel, GroupViterbiComputationAdmin)


