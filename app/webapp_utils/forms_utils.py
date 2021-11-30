
from compute_engine import OK

class BasicFileLoadErrorHandler(object):

    def __init__(self, filename):
        self._filename = filename
        self._response = None
        self._file = None

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, value):
        self._response = value

    @property
    def file_loaded(self):
        return self._file

    def check(self, request):
        """
        Do a basic check that the file was specified
        :param request:
        :return:
        """

        file_loaded = request.FILES.get(self._filename, None)

        if file_loaded is None:
            self._response = None
            return not OK, None

        self._file = file_loaded
        return OK