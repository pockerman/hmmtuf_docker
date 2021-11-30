import os
from celery import Celery
from django.conf import settings
from .celery_settings import CELERY_RESULT_BACKEND
from .celery_settings import CELERY_TASK_SERIALIZER
from .celery_settings import CELERY_RESULT_SERIALIZER
from .celery_settings import BROKER_URL

# the celery application
celery_app = Celery('hmmtuf',
                    backend=CELERY_RESULT_BACKEND,
                    broker=BROKER_URL,
                    task_serializer=CELERY_TASK_SERIALIZER,
                    result_serializer=CELERY_RESULT_SERIALIZER)

celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

