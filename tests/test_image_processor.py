import unittest
from ImageLibrary import ImageProcessor


class ImageProcessorTests(unittest.TestCase):

    def test_resize_image(self):
        image_processor = ImageProcessor(None, '.')
        resized_image = image_processor.resize_image(
            resize_percent=50,
            filename='rf_108x108.png',
            output_filename=None)
        new_size = resized_image.size
        self.assertEqual((54, 54), new_size)

    def test_resize_image_with_zero_percent(self):
        image_processor = ImageProcessor(None, '.')
        self.assertRaises(ValueError, image_processor.resize_image, resize_percent=0, filename='rf_108x108.png')

    def test_resize_image_with_negative_percent(self):
        image_processor = ImageProcessor(None, '.')
        self.assertRaises(ValueError, image_processor.resize_image, resize_percent=-50, filename='rf_108x108.png')

    def test_resize_image_with_non_square_ratio(self):
        image_processor = ImageProcessor(None, '.')
        resized_image = image_processor.resize_image(
            resize_percent=200,
            filename='rf_160x50.png',
            output_filename=None)
        new_size = resized_image.size
        self.assertEqual((320, 100), new_size)
