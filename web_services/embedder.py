import numpy as np
from pydub import AudioSegment
import pywt
import cv2
from .read_image import arnold_from_file, anti_arnold_iteration
from scipy.io import wavfile
from scipy.fftpack import dct, idct
import random
import os

class Embedder:
    def _input_image_to_coef(self, coef=None, image=None):
        j = 0
        output = []
        for i, data in enumerate(coef):
            if j >= 0 and j < len(image):
                data = data+image[j]
                j = j + 1
                output.append(data)
            else:
                output.append(data)
        return output

    def _dwt_two_level(self, data=None, mode='haar'):
        cA1, cD1 = pywt.dwt(data, mode)
        cA2, cD2 = pywt.dwt(cA1, mode)
        return cA1, cD1, cA2, cD2

    def _idwt_two_level(self, cD1=None, cA2=None, cD2=None, mode='haar'):
        cA1 = pywt.idwt(cA2, cD2, mode)
        newAudioFloat = pywt.idwt(cA1, cD1, mode)
        newAudio = np.array(newAudioFloat).astype(int)
        return newAudio

    def _key_to_integer(self, key=None):
        if key is not None:
            sum = 0
            for x in key:
                sum = sum + ord(x)
            random.seed(sum)
            return random.randint(10, 30)
        else:
            return 10

    def _insert_data_to_frame(self, audio=None, image=None):
        cA1, cD1, cA2, cD2 = self._dwt_two_level(audio, 'haar')
        output = self._input_image_to_coef(cD2, image)
        newAudio = self._idwt_two_level(cD1, cA2, output, 'haar')
        return newAudio

    def _processed_image(self, image_path=None, key=None):
        # count round from key
        round = self._key_to_integer(key)
        # generate scrambled image
        image = arnold_from_file(image_path, round)
        if image is not None:
            # cv2.imwrite('../sample/scrambled.jpg',image)
            # change to image array
            img_array = np.reshape(image, image.shape[0]*image.shape[1])
            # normalize
            return [x / 255 for x in img_array]
        else:
            return None

    def embed(self, audio_path=None, image_path=None, key=None):
        audio_name, audio_ext = os.path.splitext(audio_path)
        newLocation = audio_name + '-watermarked' + audio_ext
        img_array = self._processed_image(image_path, key)
        if img_array is None:
            print('No Image')
            return 'No Image'
        else:
            if audio_ext == '.wav':
                # read audio
                try:
                    sounds = AudioSegment.from_file(audio_path)
                    # check audio channels, if stereo just edit left channel
                    if (sounds.channels == 2):
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
                            audio_array[1] = audio_array[1]._spawn(right_samples)

                        newAudioLeft = self._insert_data_to_frame(
                            left_samples, img_array)
                        new_left_channel = audio_array[0]._spawn(newAudioLeft)
                        newAudioSound = AudioSegment.from_mono_audiosegments(
                            new_left_channel, audio_array[1])
                        newAudioSound.export(newLocation, format='wav')
                        return newLocation
                    else:
                        samples = sounds.get_array_of_samples()
                        newAudioData = self._insert_data_to_frame(samples, img_array)
                        newSound = sounds._spawn(newAudioData)
                        newSound.export(newLocation, format='wav')
                        return newLocation
                except Exception as excep:
                    return str(excep)   
            else:
                return 'Unsupported Format'

    def extract(self, watermarked_audio=None, original_audio=None, key=None, location=None, size=0):
        try:
            round = self._key_to_integer(key)
            ori = AudioSegment.from_file(original_audio)
            watermark = AudioSegment.from_file(watermarked_audio)
            if (watermark.channels == ori.channels):
                if (watermark.channels == 2):
                    ori_monos = ori.split_to_mono()
                    watermark_monos = watermark.split_to_mono()
                    left_samples_ori = ori_monos[0].get_array_of_samples()
                    left_samples_watermark = watermark_monos[0].get_array_of_samples(
                    )
                    cA1_ori, cD1_ori = pywt.dwt(left_samples_ori, 'haar')
                    cA2_ori, cD2_ori = pywt.dwt(cA1_ori, 'haar')
                    cA1_water, cD1_water = pywt.dwt(left_samples_watermark, 'haar')
                    cA2_water, cD2_water = pywt.dwt(cA1_water, 'haar')
                    out_image = []
                    if len(cD2_water) <= len(cD2_ori):
                        j = 0
                        for i, content in enumerate(cD2_water):
                            if j >= 0 and j < size*size:
                                out_image.append(content - cD2_ori[i])
                                j = j + 1
                            else:
                                break
                        out_image[:] = [x * 255 for x in out_image]
                    else:
                        j = 0
                        for i, content in enumerate(cD2_ori):
                            if j >= 0 and j < size*size:
                                out_image.append(cD2_water[i] - content)
                                j = j + 1
                            else:
                                break
                        out_image[:] = [x * 255 for x in out_image]

                    matrix_image = np.reshape(np.array(out_image), (size, size))
                    # cv2.imwrite('../sample/before.jpg', matrix_image)
                    extracted_image = anti_arnold_iteration(matrix_image,round)
                    cv2.imwrite(location,extracted_image)
                    return location
                else:
                    left_samples_ori = ori.get_array_of_samples()
                    left_samples_watermark = watermark.get_array_of_samples()
                    cA1_ori, cD1_ori = pywt.dwt(left_samples_ori, 'haar')
                    cA2_ori, cD2_ori = pywt.dwt(cA1_ori, 'haar')
                    cA1_water, cD1_water = pywt.dwt(left_samples_watermark, 'haar')
                    cA2_water, cD2_water = pywt.dwt(cA1_water, 'haar')

                    out_image = []
                    if len(cD2_water) <= len(cD2_ori):
                        j = 0
                        for i, content in enumerate(cD2_water):
                            if j >= 0 and j < size*size:
                                out_image.append(content - cD2_ori[i])
                                j = j + 1
                            else:
                                break
                        out_image[:] = [x * 255 for x in out_image]
                    else:
                        j = 0
                        for i, content in enumerate(cD2_ori):
                            if j >= 0 and j < size*size:
                                out_image.append(cD2_water[i] - content)
                                j = j + 1
                            else:
                                break
                        out_image[:] = [x * 255 for x in out_image]

                    matrix_image = np.reshape(np.array(out_image), (size, size))
                    # cv2.imwrite('../sample/before.jpg', matrix_image)
                    extracted_image = anti_arnold_iteration(matrix_image,round)
                    cv2.imwrite(location,extracted_image)
                    return location
            else:
                return 'Not Same Audio Channels'
        except Exception as Except:
            return str(Except)
            

if __name__ == '__main__':
    embed = Embedder()
    out = embed.embed(audio_path='../sample/classical.wav', image_path='../sample/get-frame.png', key='HELLO')
    # out = embed.embed(audio_path='../sample/Beat_Your_Competition.mp3', image_path='../sample/final.jpg', key='HELLO')
    # out = embed.embed(audio_path='../sample/a2002011001-e02.wav', image_path='../sample/black.jpg', key='HELLO')
    # out = embed.embed(audio_path='../sample/a2002011001-e02-128k.mp3', image_path='../sample/A.jpg', key='HELLO')
    # print(out)
    embed.extract(watermarked_audio='../sample/classical-watermarked.wav',
                  original_audio='../sample/classical.wav', key='HELLO', location='../sample/extracted-image.jpg', size=300)
