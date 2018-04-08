from django.db import models

# Create your models here.
class Job(models.Model):  
    """Class describing a computational job"""

    # currently, available types of job are:
    TYPES = (
        ('embed', 'embed'),
        ('extract', 'extract'),
    )

    # list of statuses that job can have
    STATUSES = (
        ('pending', 'pending'),
        ('started', 'started'),
        ('finished', 'finished'),
        ('failed', 'failed'),
    )

    type = models.CharField(choices=TYPES, max_length=20)
    status = models.CharField(choices=STATUSES, max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image_input = models.TextField(null=True)
    audio_input = models.TextField(null=True)
    key = models.TextField(null=True)
    accessToken = models.TextField(null=True)
    image_output = models.TextField(null=True)
    audio_output = models.TextField(null=True)
    result = models.TextField(null = True)
    def save(self, *args, **kwargs):
        """Save model and if job is in pending state, schedule it"""
        super(Job, self).save(*args, **kwargs)
        if self.status == 'pending':
            from .tasks import TASK_MAPPING
            task = TASK_MAPPING[self.type]
            task.delay(job_id=self.id, n=self.argument)