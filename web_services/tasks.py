from functools import wraps

from audio_watermark_web_services.celeryconf import app  
from .models import Job

# decorator to avoid code duplication

def update_job(fn):  
    """Decorator that will update Job with result of the function"""

    # wraps will make the name and docstring of fn available for introspection
    @wraps(fn)
    def wrapper(job_id, *args, **kwargs):
        job = Job.objects.get(id=job_id)
        job.status = 'started'
        job.save()
        try:
            # execute the function fn
            result = fn(*args, **kwargs)
            # check extract or embed
            job.result = result
            job.status = 'finished'
            job.save()
        except:
            job.result = None
            job.status = 'failed'
            job.save()
    return wrapper


# two simple numerical tasks that can be computationally intensive

@app.task
@update_job
def embed(image_location, audio_location, key, accessToken):  
    """Return 2 to the n'th power"""
    return True


@app.task
@update_job
def extract(audio_location, key, accessToken):  
    """Return the n'th Fibonacci number.
    """
    return True

# mapping from names to tasks

TASK_MAPPING = {  
    'embed': embed,
    'extract': extract
}