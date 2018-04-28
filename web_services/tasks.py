""" Define All Celery Tasks """
import sys
import os
from functools import wraps
import tempfile
from celery.utils.log import get_task_logger
import pyrebase
import firebase_admin
from firebase_admin import credentials, auth
from audio_watermark_web_services.celeryconf import app
from .models import Embed, Extract
from .embedder import Embedder

LOGGER = get_task_logger(__name__)

CONFIG = {
    'apiKey': 'AIzaSyCA0Hw7fo3rQXb6zoVSr386HADe1V_VD-U',
    'authDomain': 'final-project-877fd.firebaseapp.com',
    'databaseURL': 'https://final-project-877fd.firebaseio.com',
    'storageBucket': 'final-project-877fd.appspot.com',
    'serviceAccount': '/app/web_services/final-project.json'
}

# decorator to avoid code duplication
def embed_job(func):
    """Decorator that will update Job with result of the function"""

    # wraps will make the name and docstring of fn available for introspection
    @wraps(func)
    def wrapper(job_id, *args, **kwargs):
        """ Wrapper to Call Function"""
        job = Embed.objects.get(id=job_id)
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
            message = '{}:{}:{}'.format(exc_type, fname, exc_tb.tb_lineno)
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
        job = Extract.objects.get(id=job_id)
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
            message = '{}:{}:{}'.format(exc_type, fname, exc_tb.tb_lineno)
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
        firebase = pyrebase.initialize_app(CONFIG)
        cred = credentials.Certificate('/app/web_services/final-project.json')
        default_app = firebase_admin.initialize_app(cred)
        storage = firebase.storage()
        decoded_token = auth.verify_id_token(accessToken, app=default_app)
        with tempfile.TemporaryDirectory(prefix='{}-'.format(job_id)) as tmpdirname:
            uid = decoded_token['uid']
            file_audio = '{}/{}.wav'.format(tmpdirname, job_id)
            file_image = '{}/{}.jpg'.format(tmpdirname, job_id)
            storage.child(audio_input).download(file_audio, accessToken)
            storage.child(image_input).download(file_image, accessToken)
            embbeder = Embedder()
            finished = embbeder.embed(
                audio_path=file_audio,
                image_path=file_image,
                key=key)
            target = '{}/{}-watermarked.wav'.format(uid, job_id)
            storage.child(target).put(finished, accessToken)
            return target, uid
    else:
        return 'Unsupported Method', None


@app.task
@extract_job
def extract_1(job_id, watermarked_audio_input, original_audio_input, size, key, accessToken, method_option): # pylint: disable=line-too-long, invalid-name, too-many-arguments, too-many-locals
    """Extracting Mode 1"""
    if method_option == 'extract_1':
        firebase = pyrebase.initialize_app(CONFIG)
        cred = credentials.Certificate('/app/web_services/final-project.json')
        default_app = firebase_admin.initialize_app(cred)
        storage = firebase.storage()
        decoded_token = auth.verify_id_token(accessToken, app=default_app)
        with tempfile.TemporaryDirectory(prefix='{}-'.format(job_id)) as tmpdirname:
            uid = decoded_token['uid']
            file_audio_watermarked = '{}/{}-watermarked.wav'.format(
                tmpdirname, job_id)
            file_audio_original = '{}/{}-original.wav'.format(
                tmpdirname, job_id)
            temp_loc_target = '{}/{}-extracted.jpg'.format(tmpdirname, job_id)
            storage.child(watermarked_audio_input).download(
                file_audio_watermarked, accessToken)
            storage.child(original_audio_input).download(
                file_audio_original, accessToken)
            embbeder = Embedder()
            finished = embbeder.extract(watermarked_audio=file_audio_watermarked,
                                        original_audio=file_audio_original,
                                        key=key,
                                        location=temp_loc_target,
                                        size=int(size))
            target = '{}/{}-extracted.jpg'.format(uid, job_id)
            storage.child(target).put(finished, accessToken)
            return target, uid
    else:
        return 'Unsupported Method', None


# mapping from names to tasks

TASK_MAPPING = {
    'embed_1': embed_1,
    'extract_1': extract_1
}
