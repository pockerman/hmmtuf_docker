from django.db import models

"""
from hmmtuf.settings import REGIONS_FILES_ROOT
from hmmtuf.settings import HMM_FILES_ROOT

def upload_hmm_file(instance, filename):
    return HMM_FILES_ROOT + filename #'/'.join(['content', instance.user.username, filename])

def upload_region_file(instance, filename):
    return REGIONS_FILES_ROOT + filename #'/'.join(['content', instance.user.username, filename])

# Create your models here.

class FilesModel(models.Model):

    id = models.AutoField(primary_key=True)

    # name of the file that describes the model
    #filename = models.CharField(max_length=100)

    # a user defined name to distinguish
    name = models.CharField(max_length=100)

    # the extension of the file
    extension = models.CharField(max_length=10)

    class Meta:
        abstract = True

    def __str__(self):
        return "%s "%(self.name)


class HMMModel(FilesModel):

    file_hmm = models.FileField(upload_to=upload_hmm_file)

    class Meta(FilesModel.Meta):
        db_table = 'hmm_model'
        constraints = [
            models.UniqueConstraint(fields=['name', ], name='HMM unique  name constraint')
        ]

    def __str__(self):
        return "%s %s" % (self.name, self.file_hmm)


class RegionModel(FilesModel):

    file_region = models.FileField(upload_to=upload_region_file)
    chromosome = models.CharField(max_length=10)

    class Meta(FilesModel.Meta):
        db_table = 'region_model'
        constraints = [
            models.UniqueConstraint(fields=['name', ], name='Region unique  name constraint')
        ]

    def __str__(self):
        return "%s %s" % (self.name, self.file_region)

"""
