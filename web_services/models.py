""" Models Data for Database """
from django.db import models
from web_services.tasks import TASK_MAPPING

class Embed(models.Model):
    """Class describing a embed job"""

    # list of statuses that job can have
    STATUSES = (
        ('pending', 'pending'),
        ('started', 'started'),
        ('finished', 'finished'),
        ('failed', 'failed'),
    )

    METHODS = (
        ('embed_1', 'DWT Based and Arnold Transform to Image'),
    )

    status = models.CharField(
        choices=STATUSES, max_length=20, default='pending')
    method_option = models.CharField(
        choices=METHODS, max_length=100, default='0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image_input = models.TextField(default='')
    audio_input = models.TextField(default='')
    key = models.TextField(default='')
    accessToken = models.TextField(default='')
    user_id = models.TextField(null=True)
    audio_output = models.TextField(null=True)
    result = models.TextField(null=True)

    def save(self, *args, **kwargs): # pylint: disable=W0222
        """Save model and if job is in pending state, schedule it"""
        super(Embed, self).save(*args, **kwargs) # pylint: disable=R1725
        if self.status == 'pending':
            task = TASK_MAPPING[self.method_option]
            task.delay(
                job_id=self.id,
                method_option=self.method_option,
                image_input=self.image_input,
                audio_input=self.audio_input,
                key=self.key,
                accessToken=self.accessToken
            )


class Extract(models.Model):
    """ Extract Job Model """
    # list of statuses that job can have
    STATUSES = (
        ('pending', 'pending'),
        ('started', 'started'),
        ('finished', 'finished'),
        ('failed', 'failed'),
    )

    METHODS = (
        ('extract_1', 'DWT Based and Arnold Transform to Image'),
    )

    status = models.CharField(
        choices=STATUSES, max_length=20, default='pending')
    method_option = models.CharField(
        choices=METHODS, max_length=100, default='0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    watermarked_audio_input = models.TextField(default='')
    original_audio_input = models.TextField(default='')
    size = models.TextField(default='')
    key = models.TextField(default='')
    accessToken = models.TextField(default='')
    user_id = models.TextField(null=True)
    image_output = models.TextField(null=True)
    result = models.TextField(null=True)

    def save(self, *args, **kwargs): # pylint: disable=W0222
        """Save model and if job is in pending state, schedule it"""
        super(Extract, self).save(*args, **kwargs) # pylint: disable=R1725
        if self.status == 'pending':
            task = TASK_MAPPING[self.method_option]
            task.delay(job_id=self.id,
                       watermarked_audio_input=self.watermarked_audio_input,
                       original_audio_input=self.original_audio_input,
                       size=self.size,
                       key=self.key,
                       accessToken=self.accessToken,
                       method_option=self.method_option)
