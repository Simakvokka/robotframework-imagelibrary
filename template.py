from __future__ import absolute_import


from ImageLibrary.image_processor import ImageProcessor
from ImageLibrary import utils

#        self.area = GUIProcess().get_window_area()

class Template(object):

    def __init__(self, error_handler, output_dir):
        self.error_handler = error_handler
        self.output_dir = output_dir

    @utils.add_error_info
    def find_template(self, image, threshold=0.95, cache=False, zone=None):
        return ImageProcessor(self.error_handler, self.output_dir).find_image(image, threshold, cache, zone)

    @utils.add_error_info
    def is_template_on_screen(self, image, threshold=0.95, cache=False, zone=None):
        return ImageProcessor(self.error_handler, self.output_dir).is_image_on_screen(image, threshold, cache, zone)

    @utils.add_error_info
    def template_should_be_on_screen(self, image, threshold=0.95, cache=False, zone=None):
        return ImageProcessor(self.error_handler, self.output_dir).image_should_be_on_screen(image, threshold, cache, zone)

    @utils.add_error_info
    def template_should_not_be_on_screen(self, image, threshold=0.95, cache=False, zone=None):
        return ImageProcessor(self.error_handler, self.output_dir).image_should_not_be_on_screen(image, threshold, cache, zone)

    #@utils.add_error_info
    def wait_for_template(self, image, threshold=0.95, timeout=15, zone=None):
        return ImageProcessor(self.error_handler, self.output_dir).wait_for_image(image, threshold, timeout, zone)

    @utils.add_error_info
    def wait_for_template_to_hide(self, image, threshold=0.95, timeout=15, zone=None):
        return ImageProcessor(self.error_handler, self.output_dir).wait_for_image_to_hide(image, threshold, timeout, zone)

    @utils.add_error_info
    def wait_for_template_to_stop(self, image, threshold=0.95, timeout=15, move_threshold=0.99, step=0.1):
        return ImageProcessor(self.error_handler, self.output_dir).wait_for_image_to_stop(image, threshold, timeout, move_threshold, step)

    @utils.add_error_info
    def get_templates_count(self, image, threshold=0.95, cache=False, zone=None):
        return ImageProcessor(self.error_handler, self.output_dir).get_images_count(image, threshold, cache, zone)


class ComplexTemplate(object):
    def __init__(self, error_handler, output_dir):
        self.error_handler = error_handler
        self.output_dir = output_dir

    @utils.add_error_info
    def is_complex_template_on_screen(self, images_set, threshold=0.95, cache=False, zone=None):
        #self.window_area = GUIProcess().get_window_area()
        on_screen = True
        screen = ImageProcessor(self.error_handler, self.output_dir).get_screenshot() if not cache else None
        for image in images_set:
            on_screen &= ImageProcessor(self.error_handler, self.output_dir).is_image_on_screen(image, threshold, cache, zone, screen)
            if not on_screen:
                break

        return on_screen

    @utils.add_error_info
    def is_any_part_of_complex_template_on_screen(self, images_set, threshold=0.95, cache=False, zone=None):
        #self.window_area = GUIProcess().get_window_area()
        screen = ImageProcessor(self.error_handler, self.output_dir).get_screenshot() if not cache else None
        for image in images_set:
            if ImageProcessor(self.error_handler, self.output_dir).is_image_on_screen(image, threshold, cache, zone, screen):
                return True

        return False

