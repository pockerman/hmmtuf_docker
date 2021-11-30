from abc import abstractmethod
from django.http import HttpResponse
from django.template import loader

from compute_engine import OK
from hmmtuf.constants import INVALID_ITEM
from hmmtuf_home.models import HMMModel, RegionModel


class ComputeFormBase(object):

    """
    Base class for computation forms
    """

    def __init__(self, template_html, context, configuration):
        self._template_html = template_html
        self._context = context
        self._configuration = configuration
        self._response = INVALID_ITEM
        self._kwargs = INVALID_ITEM

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, value):
        self._response = value

    @property
    def context(self):
        return self._context

    @property
    def template_html(self):
        return self._template_html

    @property
    def kwargs(self):
        return self._kwargs

    @kwargs.setter
    def kwargs(self, value):
        self._kwargs = value

    @abstractmethod
    def check(self, request):
        pass


class GroupViterbiComputeForm(ComputeFormBase):

    def __init__(self, template_html, context):
        super(GroupViterbiComputeForm, self).__init__(template_html=template_html,
                                                      context=context, configuration=None)

        self._group_tip = INVALID_ITEM
        self._hmm_name = INVALID_ITEM
        self._remove_dirs = INVALID_ITEM
        self._use_spade = INVALID_ITEM

        self.kwargs = {"hmm_name": self._hmm_name,
                       "group_tip": self._group_tip,
                       "remove_dirs": self._remove_dirs,
                       "use_spade": self._use_spade}

    def check(self, request):

        self._hmm_name = request.POST.get("hmm", "")
        if self._hmm_name == "":
            return not OK

        self._group_tip = request.POST.get("group_tip")

        if self._group_tip != "all":

            objects = RegionModel.objects.filter(group_tip__tip=self._group_tip)

            if len(objects) == 0:
                template = loader.get_template(self._template_html)
                self.context.update({"error_found": True,
                                      "no_seq_chromosome": "No regions for group {0}".format(self._group_tip)})

                self.response = HttpResponse(template.render(self.context, request))
                return not OK

        self._remove_dirs = request.POST.get('remove_dirs', False)
        if self._remove_dirs == 'True':
            self._remove_dirs = True

        self._use_spade = request.POST.get('use_spade', False)
        if self._use_spade == 'True':
            self._use_spade = True

        self.kwargs = {"hmm_name": self._hmm_name,
                       "group_tip": self._group_tip,
                       "remove_dirs": self._remove_dirs,
                       "use_spade": self._use_spade,}
        return OK


class ViterbiComputeForm(ComputeFormBase):

    def __init__(self, template_html, configuration, context):

        super(ViterbiComputeForm, self).__init__(template_html=template_html,
                                                 context=context,
                                                 configuration=configuration)

        self._group_tip = INVALID_ITEM
        self._hmm_name = INVALID_ITEM
        self._remove_dirs = INVALID_ITEM
        self._use_spade = INVALID_ITEM
        self._region_filename = INVALID_ITEM

        self.kwargs = {"hmm_name": self._hmm_name,
                       "group_tip": self._group_tip,
                       "remove_dirs": self._remove_dirs,
                       "use_spade": self._use_spade,
                       "region_filename": self._region_filename}

    def check(self, request):

        # find the HMM
        hmm_name = request.POST.get("hmm", '')
        hmm_model = HMMModel.objects.get(name=hmm_name)
        hmm_filename = hmm_model.file_hmm.name

        checkbox = request.POST.get('remove_dirs', False)

        if checkbox == 'True':
            checkbox = True

        use_spade = request.POST.get('use_spade', False)

        if use_spade == 'True':
            use_spade = True

        region_name = request.POST.get("region", '')
        region = RegionModel.objects.get(name=region_name)

        self.kwargs = {'hmm_name': hmm_name, 'region_filename': region.file_region.name,
                       'hmm_filename': hmm_filename, "remove_dirs": checkbox, "use_spade": use_spade, }

        return OK


