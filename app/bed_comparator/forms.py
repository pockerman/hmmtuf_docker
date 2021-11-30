from django.http import HttpResponse
from django.template import loader
from webapp_utils.forms_utils import BasicFileLoadErrorHandler

from compute_engine import OK


class LoadBedFile(object):

    def __init__(self, template_html):
        self._bed_checker = BasicFileLoadErrorHandler(filename="bed_filename")
        self._viterbi_checker = BasicFileLoadErrorHandler(filename="viterbi_filename")
        self._template_html = template_html

    def get_bed_file(self):
        return self._bed_checker.file_loaded

    def get_viterbi_file(self):
        return self._viterbi_checker.file_loaded

    def as_dict(self):
        return {"viterbi_filename": self.get_bed_file(), "bed_filename": self.get_viterbi_file()}

    def check(self, request):

        # check
        response = self._bed_checker.check(request=request)

        # if fail return an error message
        if response is not OK:

            if type(self._template_html) == 'str':
                template = loader.get_template(self._template_html)
            else:
                template = self._template_html
            self.response = HttpResponse(template.render({"error_found": "Bed file not specified"}, request))
            return not OK

        response = self._viterbi_checker.check(request=request)

        if response is not OK:
            template = loader.get_template(self._template_html)
            self.response = HttpResponse(template.render({"error_found": "Viterbi file not specified"}, request))
            return not OK

        return  OK