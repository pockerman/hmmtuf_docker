BROKER_URL = 'pyamqp://guest@localhost//'
CELERY_RESULT_BACKEND = 'amqp://' #'rpc://' #'sqlite://localhost' #'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Nairobi'