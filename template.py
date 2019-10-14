from __future__ import absolute_import


from ImageLibrary.image_processor import ImageProcessor
from ImageLibrary import utils

class Template(object):

    def __init__(self, error_handler, output_dir):
        self.error_handler = error_handler
        self.output_dir = output_dir

    @utils.add_error_info
    def find_template(self, image, threshold=0.95, cache=False, zone=None):
        """Finds the match with given template on the active screen. 
        
            All args except template 'image' are optional. 
            
            Returns *bool*
            
        Examples:
        | ${template} = | Find Template | template | threshold=0.95 | zone=[x  y  w  h]
        
        """
        result = ImageProcessor(self.error_handler, self.output_dir)._find_image(image, threshold, cache, zone)
        if result.found:
            return  True
        else:
            return False

    @utils.add_error_info
    def is_template_on_screen(self, image, threshold=0.95, cache=False, zone=None):
        """Checks if the given template exists on the active screen.
        
            'threshold' and 'zone' are optional.
            
            Returns *bool*.
        
        Examples:
        | ${template} = | Is Template On Screen | template | threshold=0.95 | zone=[x  y  w  h]
        
        """
        return ImageProcessor(self.error_handler, self.output_dir)._is_image_on_screen(image, threshold, cache, zone)

    @utils.add_error_info
    def template_should_be_on_screen(self, image, threshold=0.95, cache=False, zone=None):
        """Validates the presense of the given template on screen. Fails if _False_.
        
            'threshold' and 'zone' are optional. If zone is provided the template will be found in its area, if not
             - the search is on the active programm window.
        
        Examples:
        | ${template} = | Template Should Be On Screen | template | threshold=0.95 | zone=[x  y  w  h]
        
        """
        return ImageProcessor(self.error_handler, self.output_dir)._image_should_be_on_screen(image, threshold, cache, zone)
        
    @utils.add_error_info
    def template_should_not_be_on_screen(self, image, threshold=0.95, zone=None):
        """The opposite of 'Template Should Be On Screen'. Validates the absense of the given template on screen.
        
        Examples:
        | ${template} = | Template Should Not Be On Screen | template | threshold=0.95 | zone=[x  y  w  h]
        
        """
        return ImageProcessor(self.error_handler, self.output_dir)._image_should_not_be_on_screen(image, threshold, zone)
        
    @utils.add_error_info
    def wait_for_template(self, image, threshold=0.95, timeout=15, zone=None):
        """Waits until the given template appears on the screen.
            Returns *True* or *False* and warns if timeout exceeds.
        
            'threshold', 'timeoout' and 'zone' are optional.
            
            If zone is provided the template will be found in its area, if not - the search is on the active programm window.
        
        Examples:
        | ${template} = | Wait For Template | template | threshold=0.95 | zone=[x  y  w  h]
        
        Use this version if you don't need the bool result.
        | Wait For Template | template | threshold=0.95 | timeout=15 | zone=[x  y  w  h]
        
        """
        try:
            return ImageProcessor(self.error_handler, self.output_dir)._wait_for_image(image, threshold, timeout, zone)
        except TimeoutError:
            self.error_handler.report_warning('Waiting for the template for {} seconds was unsuccesfull.'.format(timeout))

    @utils.add_error_info
    def wait_for_template_to_hide(self, image, threshold=0.95, timeout=15, zone=None):
        """Waits until the given template hides from the screen.
        
            Returns warning, if timeout exceeds. Also returns *bool*.
            
            'threshold', 'timeoout' and 'zone' are optional.
        
        Examples:
        | ${template} = | Wait For Template To Hide | template | threshold=0.95 | timeout=15 | zone=[x  y  w  h]
        
        Use this version if you don't need the bool result.
        | Wait For Template | template | threshold=0.95 | timeout=15 | zone=[x  y  w  h]
        
        """
        return ImageProcessor(self.error_handler, self.output_dir)._wait_for_image_to_hide(image, threshold, timeout, zone)

    @utils.add_error_info
    def wait_for_template_to_stop(self, image, threshold=0.95, timeout=15, move_threshold=0.99, step=0.1):
        """Waits until the given template stops moving on the screen.
        
            _threshold_ - given template accuracy rate (if you don't seek the 100% accuracy which could be unreachable,
            you can set the argument from 0.8 to 0.95. Usually it is quite good interval to get the accurate comparison. 0.95 is set as default)
        
            _move_threshold_ - use to precise the fluctuations between the temporary screenshots.
            
            _step_ - frequency of taken screenshots to compare with previous one and the given template. 0.1 sec as default.
            
        Examples:
        | ${template} = | Wait For Template To Stop | template | threshold=0.95 | timeout=15 | move_threshold=0.99 | step=0.1
        
        """
        return ImageProcessor(self.error_handler, self.output_dir)._wait_for_image_to_stop(image, threshold, timeout, move_threshold, step)

    @utils.add_error_info
    def get_templates_count(self, image, threshold=0.95, cache=False, zone=None):
        """Counts the number of the given template occurences on screen (in the given zone).
            Returns an _integer_.
        
        Examples:
        | ${my_template} =  Get Templates Count | template | threshold=0.95 | zone=None
        
        """
        
        screen = ImageProcessor(self.error_handler, self.output_dir)._get_screen(cache, zone)
        return ImageProcessor(self.error_handler, self.output_dir)._get_images_count(image, threshold, cache, zone, screen)


class ComplexTemplate(object):
    def __init__(self, error_handler, output_dir):
        self.error_handler = error_handler
        self.output_dir = output_dir

    @utils.add_error_info
    def is_complex_template_on_screen(self, images_set, threshold=0.95, cache=False, zone=None):
        """Checks if the elements of the given templates set are on screen. Returns *bool*: True if all the parts from the
        set are found.
            
            Templates should be passed as a list.
        
        Examples:
        | ${complex_template} =  Is Complex Template On Screen | templates | threshold=0.95 | zone=None
        
        """
        
        on_screen = True
        screen = ImageProcessor(self.error_handler, self.output_dir).get_screenshot()
        for image in images_set:
            on_screen &= ImageProcessor(self.error_handler, self.output_dir)._is_image_on_screen(image, threshold, cache, zone, screen)
            if not on_screen:
                break

        return on_screen

    @utils.add_error_info
    def is_any_part_of_complex_template_on_screen(self, images_set, threshold=0.95, cache=False, zone=None):
        """Checks if any template from the given templates set is on the screen. Returns *bool*: True if at least one occurence matches the set.
            You can
        
        Examples:
        | ${complex_template} =  Is Any Part Of Complex Template On Screen | templates_set | threshold=0.95 | zone=None
        
        """
        screen = ImageProcessor(self.error_handler, self.output_dir).get_screenshot()
        print(images_set)
        for image in images_set:
            if ImageProcessor(self.error_handler, self.output_dir)._is_image_on_screen(image, threshold, cache, zone, screen):
                return True

        return False

