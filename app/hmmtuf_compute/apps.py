from django.apps import AppConfig
from django_plotly_dash import DjangoDash


class HmmtufComputeConfig(AppConfig):

    name = 'hmmtuf_compute'

    def ready(self):
        """
        Initialization of the application
        """
        pass


class HmmtufComputeConfigWithDashViewer(object):

    def __init__(self) -> None:
        self._kmer_viewer_app = DjangoDash('kmer_viewer_app')
        self._repeats_plot_viewer_app = DjangoDash('repeats_plot_viewer_app')

    @property
    def kmer_viewer(self) -> DjangoDash:
        return self._kmer_viewer_app

    @property
    def repeats_plot_viewer(self) -> DjangoDash:
        return self._repeats_plot_viewer_app
