from web_services.embedder import Embedder
import unittest
import os

class TestEmbedder(unittest.TestCase):

    def test_embed(self):
        audio_location = 'sample/sample1.wav'
        image_input = 'sample/get-frame.png'
        my_key = 'HELLO'
        embed = Embedder()
        out = embed.embed(audio_path=audio_location, image_path=image_input, key=my_key)
        new_audio = os.path.splitext(out)[0]
        expected_location = os.path.splitext(audio_location)[0] + '-watermarked'
        self.assertEqual(new_audio, expected_location)

    def test_extract(self):
        audio_loc = 'sample/extracted-image.jpg'
        embed = Embedder()
        result = embed.extract(watermarked_audio='sample/sample1-watermarked.wav',
                  original_audio='sample/sample1.wav', key='HELLO', location=audio_loc, size=300)
        self.assertEqual(result, audio_loc)

if __name__ == '__main__':
    unittest.main()
