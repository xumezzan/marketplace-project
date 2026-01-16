import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('service_market')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'process-refunds-every-15-min': {
        'task': 'apps.responses.tasks.process_refunds_for_unviewed_responses',
        'schedule': 900.0, # 15 minutes
    },
}
