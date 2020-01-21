import unittest
from ImageLibrary import ImageProcessor


class ImageProcessorTests(unittest.TestCase):

    def test_resize_image(self):
        image_processor = ImageProcessor(None, '.')
        resized_image = image_processor.resize_image(
            resize_percent=50,
            origFile='rf_108x108.png')
        new_size = resized_image.size
        self.assertEqual((54, 54), new_size)
