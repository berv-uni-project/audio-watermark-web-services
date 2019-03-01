""" Embedder Module """
import random
import os
import numpy as np
from pydub import AudioSegment
import pywt
import cv2
from .read_image import arnold_from_file, anti_arnold_iteration
from .read_image import arnold_rgb_iteration

class Embedder:
    """ Embedder Class """
    _id = 0
    _name = 'DWT BASED ALGORITHM by Bervianto'

    def get_id(self):
        """
        GET ID of Emmbedder Class
        """
        return self._id

    def get_name(self):
        """
        GET Name of Emmbedder Class
        """
        return self._name

    @staticmethod
    def _input_image_to_coef(coef=None, image=None):
        j = 0
        output = []
        for data in coef:
            if 0 <= j < len(image):
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
        new_audio = np.int_(new_audio_float)
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
    def _insert_data_to_frame(audio=None, image=None, mode='haar'):
        ca1, cd1, ca2, cd2 = Embedder._dwt_two_level(audio, mode)  # pylint: disable=unused-variable
        out = Embedder._input_image_to_coef(cd2, image)
        new_audio = Embedder._idwt_two_level(cd1, ca2, out, mode)
        return new_audio

    @staticmethod
    def _processed_image_greyscale(image_path=None, key=None):
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

    @staticmethod
    def _processed_image(image_path=None, key=None):
        rounds = Embedder._key_to_integer(key)
        b, g, r = arnold_rgb_iteration(image_path, rounds) # pylint: disable=invalid-name
        out = None
        if (r is not None) and (g is not None) and (b is not None):
            r_arr = np.reshape(r, r.shape[0] * r.shape[1])
            b_arr = np.reshape(b, b.shape[0] * b.shape[1])
            g_arr = np.reshape(g, g.shape[0] * g.shape[1])
            temp_1 = np.append(b_arr, g_arr)
            out_np = np.append(temp_1, r_arr)
            out = [x for x in out_np]
        return out

    @staticmethod
    def _extract_from_cd2(cd2_ori, cd2_water, size=0, is_rgb=True):
        total = 0
        multiply = 1
        if is_rgb:
            total = 3 * (size * size)
        else:
            total = size * size
            multiply = 255
        out_image = []
        if len(cd2_water) <= len(cd2_ori):
            j = 0
            for i, content in enumerate(cd2_water):
                if 0 <= j < total:
                    out_image.append(content - cd2_ori[i])
                    j = j + 1
                else:
                    break
            out_image[:] = [x * multiply for x in out_image]
        else:
            j = 0
            for i, content in enumerate(cd2_ori):
                if 0 <= j < total:
                    out_image.append(cd2_water[i] - content)
                    j = j + 1
                else:
                    break
            out_image[:] = [x * multiply for x in out_image]
        return out_image

    def embed(self, audio_path=None, image_path=None, key=None):  # pylint: disable=too-many-locals
        """ Main embed """
        audio_name, audio_ext = os.path.splitext(audio_path)
        new_location = audio_name + '-watermarked' + audio_ext
        if audio_ext == '.wav':
            # read audio
            try:
                sounds = AudioSegment.from_file(audio_path)
                img_array = None
                if sounds.sample_width == 1:
                    # greyscale/blackwhite only for 8 bit
                    img_array = self._processed_image_greyscale(
                        image_path, key)
                else:
                    # RGB for 16 bit or more
                    img_array = self._processed_image(image_path, key)
                if img_array is None:
                    raise ValueError('Not have image value')
                if len(img_array) > sounds.frame_count():
                    raise ValueError('Image provided not have enough space')
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
                        audio_array[1] = audio_array[1]._spawn(right_samples)  # pylint: disable=protected-access
                    new_audio_left = Embedder._insert_data_to_frame(
                        left_samples, img_array, 'haar')
                    new_left_channel = audio_array[0]._spawn(new_audio_left)  # pylint: disable=protected-access
                    new_audio_sound = AudioSegment.from_mono_audiosegments(
                        new_left_channel,
                        audio_array[1])
                    new_audio_sound.export(new_location, format='wav')
                    return new_location

                if sounds.channels == 1:
                    samples = sounds.get_array_of_samples()
                    new_audio_data = self._insert_data_to_frame(
                        samples, img_array)
                    new_sound = sounds._spawn(new_audio_data)  # pylint: disable=protected-access
                    new_sound.export(new_location, format='wav')
                    return new_location

                raise ValueError('Sound channels not supported')
            except Exception as excep:  # pylint: disable=broad-except
                return str(excep)
        else:
            return 'Unsupported Format'

    def extract(self, watermarked_audio=None, original_audio=None, key=None, location=None, size=0):  # pylint: disable=too-many-arguments,too-many-locals, too-many-branches, too-many-statements
        """ Extract Method Main """
        try:  # pylint: disable=too-many-nested-blocks
            rounds = self._key_to_integer(key)
            ori = AudioSegment.from_file(original_audio)
            watermark = AudioSegment.from_file(watermarked_audio)
            if watermark.channels != ori.channels: # pylint: disable=no-else-return
                return 'Not Same Audio Channels'
            if watermark.channels == 2:
                is_rgb = True
                if ori.sample_width == 1: # pylint: disable=no-else-return
                    is_rgb = False # 8 bit
                ori_monos = ori.split_to_mono()
                watermark_monos = watermark.split_to_mono()
                left_samples_ori = ori_monos[0].get_array_of_samples()
                left_samples_watermark = watermark_monos[0].get_array_of_samples(
                )
                ca1_ori, cd1_ori, ca2_ori, cd2_ori = self._dwt_two_level(left_samples_ori) # pylint: disable=unused-variable
                ca1_water, cd1_water, ca2_water, cd2_water = self._dwt_two_level(left_samples_watermark) # pylint: disable=unused-variable,line-too-long
                out_image = Embedder._extract_from_cd2(
                    cd2_ori, cd2_water, size, is_rgb)
                extracted_image = None
                if is_rgb:
                    b_g_r = np.split(np.array(out_image), 3)
                    b_arr = b_g_r[0]
                    g_arr = b_g_r[1]
                    r_arr = b_g_r[2]
                    b = np.reshape(b_arr, (size, size)) # pylint: disable=invalid-name
                    g = np.reshape(g_arr, (size, size)) # pylint: disable=invalid-name
                    r = np.reshape(r_arr, (size, size)) # pylint: disable=invalid-name
                    b_extracted = anti_arnold_iteration(
                        b, rounds)
                    g_extracted = anti_arnold_iteration(
                        g, rounds)
                    r_extracted = anti_arnold_iteration(
                        r, rounds)
                    extracted_image = cv2.merge((b_extracted, g_extracted, r_extracted)) # pylint: disable=no-member
                else:
                    matrix = np.reshape(out_image, (size, size))
                    extracted_image = anti_arnold_iteration(matrix, rounds)
                cv2.imwrite(location, extracted_image) # pylint: disable=no-member
                return location
            else:
                is_rgb = True
                if ori.sample_width == 1: # pylint: disable=no-else-return
                    is_rgb = False # 8 bit
                left_samples_ori = ori.get_array_of_samples()
                left_samples_watermark = watermark.get_array_of_samples()
                ca1_ori, cd1_ori, ca2_ori, cd2_ori = self._dwt_two_level(
                        left_samples_ori)
                ca1_water, cd1_water, ca2_water, cd2_water = self._dwt_two_level(
                        left_samples_watermark)
                out_image = Embedder._extract_from_cd2(
                        cd2_ori, cd2_water, size, is_rgb)
                extracted_image = None
                if is_rgb:
                    b_g_r = np.split(np.array(out_image), 3)
                    b_arr = b_g_r[0]
                    g_arr = b_g_r[1]
                    r_arr = b_g_r[2]
                    b = np.reshape(b_arr, (size, size)) # pylint: disable=invalid-name
                    g = np.reshape(g_arr, (size, size)) # pylint: disable=invalid-name
                    r = np.reshape(r_arr, (size, size)) # pylint: disable=invalid-name
                    b_extracted = anti_arnold_iteration(
                        b, rounds)
                    g_extracted = anti_arnold_iteration(
                        g, rounds)
                    r_extracted = anti_arnold_iteration(
                        r, rounds)
                    extracted_image = cv2.merge((b_extracted, g_extracted, r_extracted)) # pylint: disable=no-member
                else:
                    matrix = np.reshape(out_image, (size, size))
                    extracted_image = anti_arnold_iteration(matrix, rounds)
                cv2.imwrite(location, extracted_image) # pylint: disable=no-member
                return location
        except Exception as ex:  # pylint: disable=broad-except
            return str(ex)

if __name__ == '__main__':
    MY_KEY = 'HELLO'
    SIZE_KEY = 256
    ENTER = '../sample/Lena.bmp'
    EMBED = Embedder()
    OUTPUT = EMBED.embed(
        audio_path='../sample/a2002011001-e02.wav',
        image_path=ENTER,
        key=MY_KEY)
    """
    out = embed.embed(
        audio_path='../sample/a2002011001-e02.wav',
        image_path='../sample/black.jpg',
        key='HELLO')
    """
    HASIL = EMBED.extract(
        watermarked_audio='../sample/a2002011001-e02-watermarked.wav',
        original_audio='../sample/a2002011001-e02.wav',
        key=MY_KEY,
        location='../sample/extracted-image.jpg',
        size=SIZE_KEY)
