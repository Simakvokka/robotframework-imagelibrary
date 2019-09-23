from __future__ import absolute_import


from ImageLibrary.image_processor import ImageProcessor
from ImageLibrary import utils

class Template(object):

    def __init__(self, error_handler, output_dir):
        self.error_handler = error_handler
        self.output_dir = output_dir

    @utils.add_error_info
    def find_template(self, image, threshold=0.95, cache=False, zone=None):
        '''Finds the match with given template on the active screen.
           Pass _zone_, _timeout_, _step_, _thrreshold_ as arguments.
        
        :param image: img.png
        :param threshold: 0.95
        :param zone: [x  y  w  h]
        :return:
        '''
        
        return ImageProcessor(self.error_handler, self.output_dir).find_image(image, threshold, cache, zone)

    @utils.add_error_info
    def is_template_on_screen(self, image, threshold=0.95, cache=False, zone=None):
        '''Checks if the given template exists on the active screen. Returns bool.
            'threshold' and 'zone' are optional.
        
        :param image: img.png
        :param threshold: 0.95
        :param zone: [x  y  w  h]
        :return: bool
        
        '''
        return ImageProcessor(self.error_handler, self.output_dir).is_image_on_screen(image, threshold, cache, zone)

    @utils.add_error_info
    def template_should_be_on_screen(self, image, threshold=0.95, cache=False, zone=None):
        '''Validates the presense of the given template on screen. Fails if False.
            'threshold' and 'zone' are optional.
        
        :param image: img.png
        :param threshold: 0.95
        :param zone: [x  y  w  h]
        :return:
        '''
        return ImageProcessor(self.error_handler, self.output_dir).image_should_be_on_screen(image, threshold, cache, zone)
        
    @utils.add_error_info
    def template_should_not_be_on_screen(self, image, threshold=0.95, cache=False, zone=None):
        '''Validates the absense of the given template on screen. Fails if False.
            'threshold' and 'zone' are optional.
        
        :param image: img.png
        :param threshold: 0.95
        :param zone: [x  y  w  h]
        :return:
        '''
        return ImageProcessor(self.error_handler, self.output_dir).image_should_not_be_on_screen(image, threshold, cache, zone)
        
    @utils.add_error_info
    def wait_for_template(self, image, threshold=0.95, timeout=15, zone=None):
        '''Waits until the given template shown on the screen.
            'threshold', 'timeoout' and 'zone' are optional.
        
        :param image: img.png
        :param threshold: 0.95
        :param timeout: 15
        :param zone: [x  y  w  h]
        :return:
        '''
        try:
            return ImageProcessor(self.error_handler, self.output_dir).wait_for_image(image, threshold, timeout, zone)
        except TimeoutError:
            self.error_handler.report_warning('Waiting for the template for {} seconds was unsuccesfull.'.format(timeout))

    @utils.add_error_info
    def wait_for_template_to_hide(self, image, threshold=0.95, timeout=15, zone=None):
        '''Waits until the given template hides from the screen.
            Returns warning, if timeout exceeded. Also returns bool.
            Use as this if you want a return: ${a} =  Wait For Template To Hide    template=img.png
        
        :param image: img.png
        :param threshold: 0.95
        :param timeout: 15
        :param zone: [x  y  w  h]
        :return: bool
        '''
        return ImageProcessor(self.error_handler, self.output_dir).wait_for_image_to_hide(image, threshold, timeout, zone)

    @utils.add_error_info
    def wait_for_template_to_stop(self, image, threshold=0.95, timeout=15, move_threshold=0.99, step=0.1):
        '''Waits until the given template stops moving on the screen.
        
        :param image: img.png
        :param threshold: 0.95
        :param timeout: 15
        :param move_threshold: 0.99
        :param step: 0.1
        :return:
        '''
        return ImageProcessor(self.error_handler, self.output_dir).wait_for_image_to_stop(image, threshold, timeout, move_threshold, step)

    @utils.add_error_info
    def get_templates_count(self, image, threshold=0.95, cache=False, zone=None):
        '''Counts the number of given template occurence on screen.
            Returns an integer amount.
        
        :param image: img.png
        :param threshold: 0.95
        :param zone: [x  y  w  h]
        :return: int
        '''
        return ImageProcessor(self.error_handler, self.output_dir).get_images_count(image, threshold, cache, zone)


class ComplexTemplate(object):
    def __init__(self, error_handler, output_dir):
        self.error_handler = error_handler
        self.output_dir = output_dir

    @utils.add_error_info
    def is_complex_template_on_screen(self, images_set, threshold=0.95, cache=False, zone=None):
        '''Checks if the elements of the given templates set are on screen.
        
        :param images_set: list
        :param threshold: 0.95
        :param zone: [x  y  w  h] or None
        :return: bool
        '''
        on_screen = True
        screen = ImageProcessor(self.error_handler, self.output_dir).get_screenshot() if not cache else None
        for image in images_set:
            on_screen &= ImageProcessor(self.error_handler, self.output_dir).is_image_on_screen(image, threshold, cache, zone, screen)
            if not on_screen:
                break

        return on_screen

    @utils.add_error_info
    def is_any_part_of_complex_template_on_screen(self, images_set, threshold=0.95, cache=False, zone=None):
        '''Checks if any template of the given template set is on the screen.
        
        :param images_set: img.png
        :param threshold: 0.95
        :param zone: [x  y  w  h] or None
        :return: bool
        '''
        screen = ImageProcessor(self.error_handler, self.output_dir).get_screenshot() if not cache else None
        for image in images_set:
            if ImageProcessor(self.error_handler, self.output_dir).is_image_on_screen(image, threshold, cache, zone, screen):
                return True

        return False

