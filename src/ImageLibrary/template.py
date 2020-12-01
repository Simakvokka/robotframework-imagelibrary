from ImageLibrary import utils
from ImageLibrary.image_processor import ImageProcessor, get_image_from_config

def _get_threshold(info, threshold):
    if threshold is not None:
        return threshold
    else:
        return info[1]

class Template:
    @utils.add_error_info
    def __init__(self, name, config):
        self.name = name
        self.images = None   #if there are multiple images
        self.image = None    #if this is one image
        if isinstance(config, list):
            self.images = []
            for entry in config:
                self.images.append(get_image_from_config(entry))

        else:
            self.image = get_image_from_config(config)

    def _get_template_image(self, index):
        if self.images is not None:
            index = int(index)
            assert index != -1, "Template {} must be reached by index, but it isn't set".format(self.name)
            #assert index > 0, "Index must by more that zero"
            assert index <= len(self.images), "{} has only {} elements, index is to big".format(self.name, len(self.images))
            return self.images[index - 1]

        return self.image

    @utils.add_error_info
    def find_template(self, index=-1, threshold=None, cache=False, zone=None):
        image = self._get_template_image(index)
        return ImageProcessor().find_image(image[0], _get_threshold(image, threshold), cache, zone)

    @utils.add_error_info
    def is_template_on_screen(self, index=-1, threshold=None, cache=False, zone=None):
        image = self._get_template_image(index)
        return ImageProcessor().is_image_on_screen(image[0], _get_threshold(image, threshold), cache, zone)

    @utils.add_error_info
    def template_should_be_on_screen(self, index=-1, threshold=None, cache=False, zone=None):
        image = self._get_template_image(index)
        return ImageProcessor().image_should_be_on_screen(image[0], _get_threshold(image, threshold), cache, zone)

    @utils.add_error_info
    def template_should_not_be_on_screen(self, index=-1, threshold=None, cache=False, zone=None):
        image = self._get_template_image(index)
        return ImageProcessor().image_should_not_be_on_screen(image[0], _get_threshold(image, threshold), cache, zone)

    @utils.add_error_info
    def wait_for_template(self, index=-1, threshold=None, timeout=15, zone=None):
        image = self._get_template_image(index)
        return ImageProcessor().wait_for_image(image[0], _get_threshold(image, threshold), timeout, zone)

    @utils.add_error_info
    def wait_for_template_to_hide(self, index=-1, threshold=None, timeout=15, zone=None):
        image = self._get_template_image(index)
        return ImageProcessor().wait_for_image_to_hide(image[0], _get_threshold(image, threshold), timeout, zone)

    @utils.add_error_info
    def wait_for_template_to_stop(self, index=-1, threshold=None, timeout=15, move_threshold=0.99, step=0.1):
        image = self._get_template_image(index)
        return ImageProcessor().wait_for_image_to_stop(image[0], _get_threshold(image, threshold), timeout, move_threshold, step)

    @utils.add_error_info
    def get_templates_count(self, index=-1, threshold=None, cache=False, zone=None):
        image = self._get_template_image(index)
        return ImageProcessor().get_images_count(image[0], _get_threshold(image, threshold), cache, zone)


class ComplexTemplate(object):
    def __init__(self, name, config):
        if not isinstance(config, list):
            raise AssertionError('Config corrupted for complex template {}: must be list of filenames, {} actually'.format(name, config))

        self.name = name

        self.images = []
        if isinstance(config, list):
            for entry in config:
                self.images.append(get_image_from_config(entry))
        else:
            raise AssertionError("Complex template must contain list of images")

    @utils.add_error_info
    def is_complex_template_on_screen(self, threshold=None, cache=False, zone=None):
        on_screen = True
        screen = ImageProcessor().get_screenshot() if not cache else None

        for image in self.images:
            on_screen &= ImageProcessor().is_image_on_screen(image[0], _get_threshold(image, threshold), cache, zone, screen)
            if not on_screen:
                break

        return on_screen

    @utils.add_error_info
    def is_any_part_of_complex_template_on_screen(self, threshold=None, cache=False, zone=None):
        screen = ImageProcessor().get_screenshot() if not cache else None
        for image in self.images:
            if ImageProcessor().is_image_on_screen(image[0], _get_threshold(image, threshold), cache, zone, screen):
                return True

        return False

    @utils.add_error_info
    def wait_for_complex_template(self, threshold=None, timeout=15, zone=None):
        waiting_result = False
        for image in self.images:
            waiting_result = ImageProcessor().wait_for_image(image[0], _get_threshold(image, threshold), timeout, zone)
            if not waiting_result:
                return waiting_result
        return waiting_result

    @utils.add_error_info
    def wait_for_complex_template_to_hide(self, threshold=None, timeout=15, zone=None):
        waiting_result = False
        for image in self.images:
            waiting_result = ImageProcessor().wait_for_image_to_hide(image[0], _get_threshold(image, threshold), timeout, zone)
            if not waiting_result:
                return waiting_result
        return waiting_result
