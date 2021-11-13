""" Define All Celery Tasks """
import sys
import os
from functools import wraps
import tempfile
from celery.utils.log import get_task_logger
import firebase_admin
from firebase_admin import credentials, auth, storage
from audio_watermark_web_services.celeryconf import app
from web_services.embedder import Embedder
import web_services.models

LOGGER = get_task_logger(__name__)

# decorator to avoid code duplication
def embed_job(func):
    """Decorator that will update Job with result of the function"""

    # wraps will make the name and docstring of fn available for introspection
    @wraps(func)
    def wrapper(job_id, *args, **kwargs):
        """ Wrapper to Call Function"""
        job = web_services.models.Embed.objects.get(id=job_id)
        job.status = 'started'
        job.save()
        try:
            # execute the function fn
            result, uid = func(job_id, *args, **kwargs)
            # check extract or embed
            job.result = result
            job.audio_output = result
            job.user_id = uid
            job.status = 'finished'
            job.save()
        except Exception as ex: # pylint: disable=broad-except
            exc_type, exc_obj, exc_tb = sys.exc_info() # pylint: disable=unused-variable
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            message = f'{exc_type}:{fname}:{exc_tb.tb_lineno}'
            LOGGER.info(str(ex))
            LOGGER.info(message)
            job.result = message
            job.status = 'failed'
            job.save()
    return wrapper


def extract_job(fun):
    """Decorator that will update Job with result of the function"""
    # wraps will make the name and docstring of fn available for introspection
    @wraps(fun)
    def wrapper(job_id, *args, **kwargs):
        """ Wrapper to Call Function"""
        job = web_services.models.Extract.objects.get(id=job_id)
        job.status = 'started'
        job.save()
        try:
            # execute the function fn
            result, uid = fun(job_id, *args, **kwargs)
            # check extract or embed
            job.result = result
            job.image_output = result
            job.user_id = uid
            job.status = 'finished'
            job.save()
        except Exception as ex: # pylint: disable=broad-except
            exc_type, exc_obj, exc_tb = sys.exc_info() # pylint: disable=unused-variable
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            message = f'{exc_type}:{fname}:{exc_tb.tb_lineno}'
            LOGGER.info(str(ex))
            LOGGER.info(message)
            job.result = message
            job.status = 'failed'
            job.save()
    return wrapper


# two simple numerical tasks that can be computationally intensive

@app.task
@embed_job
def embed_1(job_id, image_input, audio_input, key, accessToken, method_option): # pylint: disable=invalid-name, too-many-arguments, too-many-locals
    """Embedding Task Mode 1"""
    if method_option == 'embed_1':
        default_app = None
        if firebase_admin._DEFAULT_APP_NAME not in firebase_admin._apps: # pylint: disable=protected-access
            cred = credentials.Certificate('/app/web_services/final-project.json')
            default_app = firebase_admin.initialize_app(cred, {
                'storageBucket': 'final-project-877fd.appspot.com'
            })
        else:
            default_app = firebase_admin.get_app()
        bucket = storage.bucket()
        decoded_token = auth.verify_id_token(accessToken, app=default_app)
        with tempfile.TemporaryDirectory(prefix=f'{job_id}-') as tmpdirname:
            uid = decoded_token['uid']
            file_audio = f'{tmpdirname}/{job_id}.wav'
            file_image = f'{tmpdirname}/{job_id}.jpg'
            blob = bucket.blob(audio_input)
            blob.download_to_filename(file_audio)
            blob1 = bucket.blob(image_input)
            blob1.download_to_filename(file_image)
            embbeder = Embedder()
            finished = embbeder.embed(
                audio_path=file_audio,
                image_path=file_image,
                key=key)
            target = f'{uid}/{job_id}-watermarked.wav'
            blob_target = bucket.blob(target)
            blob_target.upload_from_filename(finished)
            return target, uid
    else:
        return 'Unsupported Method', None


@app.task
@extract_job
def extract_1(job_id, watermarked_audio_input, original_audio_input, size, key, accessToken, method_option): # pylint: disable=line-too-long, invalid-name, too-many-arguments, too-many-locals
    """Extracting Mode 1"""
    if method_option == 'extract_1':
        default_app = None
        if firebase_admin._DEFAULT_APP_NAME not in firebase_admin._apps: # pylint: disable=protected-access
            cred = credentials.Certificate('/app/web_services/final-project.json')
            default_app = firebase_admin.initialize_app(cred, {
                'storageBucket': 'final-project-877fd.appspot.com'
            })
        else:
            default_app = firebase_admin.get_app()
        bucket = storage.bucket()
        decoded_token = auth.verify_id_token(accessToken, app=default_app)
        with tempfile.TemporaryDirectory(prefix=f'{job_id}-') as tmpdirname:
            uid = decoded_token['uid']
            file_audio_watermarked = f'{tmpdirname}/{job_id}-watermarked.wav'
            file_audio_original = f'{tmpdirname}/{job_id}-original.wav'
            temp_loc_target = f'{tmpdirname}/{job_id}-extracted.jpg'
            blob = bucket.blob(watermarked_audio_input)
            blob.download_to_filename(file_audio_watermarked)
            blob1 = bucket.blob(original_audio_input)
            blob1.download_to_filename(file_audio_original)
            embbeder = Embedder()
            finished = embbeder.extract(watermarked_audio=file_audio_watermarked,
                                        original_audio=file_audio_original,
                                        key=key,
                                        location=temp_loc_target,
                                        size=int(size))
            target = f'{uid}/{job_id}-extracted.jpg'
            blob2 = bucket.blob(target)
            blob2.upload_from_filename(finished)
            return target, uid
    else:
        return 'Unsupported Method', None


# mapping from names to tasks

TASK_MAPPING = {
    'embed_1': embed_1,
    'extract_1': extract_1
}
