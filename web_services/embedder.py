""" Embedder Module """
import random
import os
import numpy as np
from pydub import AudioSegment
import pywt
import cv2
from read_image import arnold_from_file, anti_arnold_iteration

class Embedder:
    """ Embedder Class """
    @staticmethod
    def _input_image_to_coef(coef=None, image=None):
        j = 0
        output = []
        for data in coef:
            if j >= 0 and j < len(image):
                data = data + image[j]
                j = j + 1
                output.append(data)
            else:
                output.append(data)
        return output

    @staticmethod
    def _dwt_two_level(data=None, mode='haar'):
        ca1, cd1 = pywt.dwt(data, mode)
        ca2, cd2 = pywt.dwt(ca1, mode)
        return ca1, cd1, ca2, cd2

    @staticmethod
    def _idwt_two_level(cd1=None, ca2=None, cd2=None, mode='haar'):
        ca1 = pywt.idwt(ca2, cd2, mode)
        new_audio_float = pywt.idwt(ca1, cd1, mode)
        new_audio = np.array(new_audio_float).astype(int)
        return new_audio

    @staticmethod
    def _key_to_integer(key=None):
        default_num = 10
        if key is not None:
            val = 0
            for charachter in key:
                val = val + ord(charachter)
            random.seed(val)
            default_num = random.randint(10, 30)
        return default_num

    @staticmethod
    def _insert_data_to_frame(audio=None, image=None):
        ca1, cd1, ca2, cd2 = Embedder._dwt_two_level(audio, 'haar') # pylint: disable=unused-variable
        out = Embedder._input_image_to_coef(cd2, image)
        new_audio = Embedder._idwt_two_level(cd1, ca2, out, 'haar')
        return new_audio

    @staticmethod
    def _processed_image(image_path=None, key=None):
        # count round from key
        rounds = Embedder._key_to_integer(key)
        # generate scrambled image
        image = arnold_from_file(image_path, rounds)
        out = None
        if image is not None:
            # change to image array
            img_array = np.reshape(image, image.shape[0] * image.shape[1])
            # normalize
            out = [x / 255 for x in img_array]
        return out

    def embed(self, audio_path=None, image_path=None, key=None): # pylint: disable=too-many-locals
        """ Main embed """
        audio_name, audio_ext = os.path.splitext(audio_path)
        new_location = audio_name + '-watermarked' + audio_ext
        img_array = self._processed_image(image_path, key)
        if img_array is None: # pylint: disable=too-many-nested-blocks
            return 'No Image'
        else:
            if audio_ext == '.wav':
                # read audio
                try:
                    sounds = AudioSegment.from_file(audio_path)
                    if len(img_array) > len(sounds):
                        return 'Not Enough to Save'
                    else:
                        # check audio channels, if stereo just edit left channel
                        if sounds.channels == 2:
                            audio_array = sounds.split_to_mono()
                            left_samples = audio_array[0].get_array_of_samples()
                            right_samples = audio_array[1].get_array_of_samples()
                            append = len(left_samples) % 4
                            if append != 0:
                                i = 0
                                while i < 4 - append:
                                    left_samples.append(-128)
                                    right_samples.append(-128)
                                    i = i + 1
                                audio_array[1] = audio_array[1]._spawn(right_samples) # pylint: disable=protected-access
                            new_audio_left = Embedder._insert_data_to_frame(
                                left_samples, img_array)
                            new_left_channel = audio_array[0]._spawn(new_audio_left) # pylint: disable=protected-access
                            new_audio_sound = AudioSegment.from_mono_audiosegments(
                                new_left_channel,
                                audio_array[1])
                            new_audio_sound.export(new_location, format='wav')
                            return new_location
                        else:
                            samples = sounds.get_array_of_samples()
                            new_audio_data = self._insert_data_to_frame(
                                samples, img_array)
                            new_sound = sounds._spawn(new_audio_data) # pylint: disable=protected-access
                            new_sound.export(new_location, format='wav')
                            return new_location
                except Exception as excep: # pylint: disable=broad-except
                    return str(excep)
            else:
                return 'Unsupported Format'

    def extract(self, watermarked_audio=None, original_audio=None, key=None, location=None, size=0): # pylint: disable=too-many-arguments,too-many-locals, too-many-branches, too-many-statements
        """ Extract Method Main """
        try: # pylint: disable=too-many-nested-blocks
            rounds = self._key_to_integer(key)
            ori = AudioSegment.from_file(original_audio)
            watermark = AudioSegment.from_file(watermarked_audio)
            if watermark.channels == ori.channels:
                if watermark.channels == 2:
                    ori_monos = ori.split_to_mono()
                    watermark_monos = watermark.split_to_mono()
                    left_samples_ori = ori_monos[0].get_array_of_samples()
                    left_samples_watermark = watermark_monos[0].get_array_of_samples(
                    )
                    ca1_ori, cd1_ori = pywt.dwt(left_samples_ori, 'haar') # pylint: disable=unused-variable
                    ca2_ori, cd2_ori = pywt.dwt(ca1_ori, 'haar') # pylint: disable=unused-variable
                    ca1_water, cd1_water = pywt.dwt( # pylint: disable=unused-variable
                        left_samples_watermark, 'haar')
                    ca2_water, cd2_water = pywt.dwt(ca1_water, 'haar')
                    out_image = []
                    if len(ca2_water) <= len(cd2_ori):
                        j = 0
                        for i, content in enumerate(cd2_water):
                            if j >= 0 and j < size * size:
                                out_image.append(content - cd2_ori[i])
                                j = j + 1
                            else:
                                break
                        out_image[:] = [x * 255 for x in out_image]
                    else:
                        j = 0
                        for i, content in enumerate(cd2_ori):
                            if j >= 0 and j < size * size:
                                out_image.append(cd2_water[i] - content)
                                j = j + 1
                            else:
                                break
                        out_image[:] = [x * 255 for x in out_image]

                    matrix_image = np.reshape(
                        np.array(out_image), (size, size))
                    extracted_image = anti_arnold_iteration(
                        matrix_image, rounds)
                    cv2.imwrite(location, extracted_image) # pylint: disable=no-member
                    return location
                else:
                    left_samples_ori = ori.get_array_of_samples()
                    left_samples_watermark = watermark.get_array_of_samples()
                    ca1_ori, cd1_ori = pywt.dwt(left_samples_ori, 'haar')
                    ca2_ori, cd2_ori = pywt.dwt(ca1_ori, 'haar')
                    ca1_water, ca1_water = pywt.dwt(
                        left_samples_watermark, 'haar')
                    cd2_water, cd2_water = pywt.dwt(ca1_water, 'haar')

                    out_image = []
                    if len(cd2_water) <= len(cd2_ori):
                        j = 0
                        for i, content in enumerate(cd2_water):
                            if j >= 0 and j < size * size:
                                out_image.append(content - cd2_ori[i])
                                j = j + 1
                            else:
                                break
                        out_image[:] = [x * 255 for x in out_image]
                    else:
                        j = 0
                        for i, content in enumerate(cd2_ori):
                            if j >= 0 and j < size * size:
                                out_image.append(cd2_water[i] - content)
                                j = j + 1
                            else:
                                break
                        out_image[:] = [x * 255 for x in out_image]

                    matrix_image = np.reshape(
                        np.array(out_image), (size, size))
                    extracted_image = anti_arnold_iteration(
                        matrix_image, round)
                    cv2.imwrite(location, extracted_image) # pylint: disable=no-member
                    return location
            else:
                return 'Not Same Audio Channels'
        except Exception as ex: # pylint: disable=broad-except
            return str(ex)


if __name__ == '__main__':
    EMBED = Embedder()
    OUTPUT = EMBED.embed(
        audio_path='../sample/classical.wav',
        image_path='../sample/get-frame.png',
        key='HELLO')
    """
    out = embed.embed(
        audio_path='../sample/Beat_Your_Competition.mp3',
        image_path='../sample/final.jpg',
        key='HELLO')
    out = embed.embed(
        audio_path='../sample/a2002011001-e02.wav',
        image_path='../sample/black.jpg',
        key='HELLO')
    out = embed.embed(
        audio_path='../sample/a2002011001-e02-128k.mp3',
        image_path='../sample/A.jpg',
        key='HELLO')
    """
    EMBED.extract(
        watermarked_audio='../sample/classical-watermarked.wav',
        original_audio='../sample/classical.wav',
        key='HELLO',
        location='../sample/extracted-image.jpg',
        size=300)
