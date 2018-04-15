import os

from celery import Celery  
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "audio_watermark_web_services.settings")

app = Celery('audio_watermark_web_services')

CELERY_TIMEZONE = 'UTC'

app.config_from_object('django.conf:settings')  
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)  