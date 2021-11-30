
from django.http import HttpResponse
from django.template import loader

from webapp_utils.forms_utils import BasicFileLoadErrorHandler
from compute_engine import OK


class ErrorHandler(BasicFileLoadErrorHandler):

    def __init__(self, filename, item_name, template_html):
        super(ErrorHandler, self).__init__(filename=filename)
        self._item_name = item_name
        self._template_html = template_html
        self._name = None

    @property
    def name(self):
        return self._name

    def check(self, request):

        basic_response = super(ErrorHandler, self).check(request=request)

        if basic_response is not OK:
            template = loader.get_template(self._template_html)
            self._response = HttpResponse(template.render({"error_found": "File not specified"}, request))

            return not OK

        name = request.POST.get(self._item_name, '')
        if name == '':
            template = loader.get_template(self._template_html)
            self._response = HttpResponse(template.render({"error_found": "Name not specified"}, request))
            return not OK

        self._name = name
        return OK


class RegionLoadForm(ErrorHandler):

    def __init__(self, filename, item_name, context, template_html, path):
        super(RegionLoadForm, self).__init__(filename=filename, item_name=item_name,
                                             template_html=template_html)

        self._path = path
        self._context = context
        self._chromosome = None
        self._ref_seq_region = None
        self._wga_seq_region = None
        self._no_wga_seq_region = None
        self._start_idx = None
        self._end_idx = None
        self._group_tip = None
        self._chromosome_idx = None

    @property
    def chromosome(self):
        return self._chromosome

    @property
    def ref_seq_filename(self):
        return self._path + self._ref_seq_region

    @property
    def wga_seq_filename(self):
        return self._path + self._wga_seq_region

    @property
    def no_wga_seq_filename(self):
        return self._path + self._no_wga_seq_region

    @property
    def start_idx(self):
        return self._start_idx

    @property
    def end_idx(self):
        return self._end_idx

    @property
    def group_tip(self):
        return self._group_tip

    @property
    def chromosome_idx(self):
        return self._chromosome_idx

    def check(self, request):

        file_loaded = request.FILES.get(self._filename, None)

        if file_loaded is None:
            template = loader.get_template(self._template_html)
            context = {"error_found": "File not specified"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        self._file = file_loaded

        name = request.POST.get(self._item_name, '')
        if name == '':
            template = loader.get_template(self._template_html)
            context = {"error_found": "Name not specified"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        self._name = name

        # did we also get the chromosome
        chromosome = request.POST.get('chr_name', '')

        if chromosome == '':
            template = loader.get_template(self._template_html)
            context = {"error_found": "Missing chromosome name"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        self._chromosome = chromosome
        self._ref_seq_region = request.POST.get('ref_seq_region', '')
        self._wga_seq_region = request.POST.get('wga_seq_region', '')
        self._no_wga_seq_region = request.POST.get('no_wga_seq_region', '')

        start_idx = request.POST.get('region_start_idx', '')

        if start_idx == '':
            template = loader.get_template(self._template_html)
            context = {"error_found": "Missing start index"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        end_idx = request.POST.get('region_end_idx', '')

        if end_idx == '':
            template = loader.get_template(self._template_html)
            context = {"error_found": "Missing end index"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        try:
            self._start_idx = int(start_idx)
        except ValueError as e:
            template = loader.get_template(self._template_html)
            context = {"error_found": "Start index not an integer"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        try:

            self._end_idx = int(end_idx)
        except ValueError as e:
            template = loader.get_template(self._template_html)
            context = {"error_found": "End index not an integer"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        if self._start_idx >= self._end_idx:
            template = loader.get_template(self._template_html)
            context = {"error_found": "End index not strictly greater than start index"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        if self._start_idx < 0:
            template = loader.get_template(self._template_html)
            context = {"error_found": "Start index cannot be negative"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        self._group_tip = request.POST.get('region_group_tip', '')
        if self._group_tip == '':
            template = loader.get_template(self._template_html)
            context = {"error_found": "Group tip is missing"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        self._chromosome_idx = request.POST.get('chr_idx', '')
        if self._chromosome_idx == '':
            template = loader.get_template(self._template_html)
            context = {"error_found": "Chromosome index is missing"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        try:
            self._chromosome_idx = int(self._chromosome_idx)
        except ValueError as e:
            template = loader.get_template(self._template_html)
            context = {"error_found": "Chromosome index in integer field"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        if self._chromosome_idx < 0:
            template = loader.get_template(self._template_html)
            context = {"error_found": "Chromosome index cannot be negative"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        return OK






