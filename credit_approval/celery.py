# myproject/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('credit_approval')
# Pull configs from Django settings, using CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')
# Auto-discover tasks.py in each installed app
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
