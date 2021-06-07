import datetime
import math
import os
import pyautogui

from PIL import Image, ImageChops, ImageOps

from robot.api import logger as LOGGER
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError

from ImageLibrary.singleton import Singleton
from ImageLibrary.error_handler import ErrorHandler
from ImageLibrary import errors, utils
from ImageLibrary.screenshot_operations import ScreenshotOperations
from ImageLibrary.open_cv import MatchObjects


pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05

DEFAULT_THRESHOLD = 0.99

def get_image_from_config(config):
    """get_image_from_config(config) -> tuple(PIL image, threshold)
        In almost every place, where you can define image in config, you can write:
        place:
            image.png
        place:
            image: image.png
        place:
            image: image.png
            threshold: 0.99
        If threshold is not defined, DEFAULT_THRESHOLD will be used
    """
    #loads image to further processing (image is loaded in PIL.Image format)
    if isinstance(config, (str, bytes)):
        #if single string
        return ImageProcessor().load_image(config), DEFAULT_THRESHOLD
    elif isinstance(config, dict):
        #if image has threshold parameter and forms a dict type
        assert "image" in config, "image must be defined"
        threshold = float(config["threshold"]) if "threshold" in config else DEFAULT_THRESHOLD
        assert 0 < threshold <= 1, "Threshold must be in (0, 1)"
        return ImageProcessor().load_image(config["image"]), threshold
    elif isinstance(config, list):
        return config
        # for image in config:
        #     return ImageProcessor().load_image(image), DEFAULT_THRESHOLD
    raise AssertionError("Config is malformed: {} is not a valid entry for image".format(config))

class FindResult:
    def __init__(self, x, y, width, height, threshold, image, screen, found):
        self.x = x                  #left
        self.y = y                  #top
        self.width = width
        self.height = height
        self.threshold = threshold  #actual threshold
        self.image = image          #image, what was found
        self.screen = screen        #screen, where it was found
        self.found = found          #was template really found

    def get_pos(self):
        return (self.x, self.y, self.width, self.height)

class ImageProcessor(metaclass=Singleton):
    """Image processing system - open files if needed, find them on screen, etc"""

    def __init__(self, rect, cv, reference_folders, error_handler):
        self.rect = rect
        self.cv = cv
        self.error_handler = error_handler
        self.reference_folders = reference_folders
        self.cache_screenshot = None

    def get_window_rect(self):
        #rect is calculated in suite setup before calling Init ImageLibrary keyword and passed as arg
        return self.rect

    def hide_cursor(self):
        where_to_move = (self.rect[0] + 1023, self.rect[1] + 767)
        if pyautogui.position() != where_to_move:
            pyautogui.moveTo(*where_to_move)

    def _get_screenshot(self, area=None):
        """get_screenshot([area]) -> Image
            Get screenshot of specified area or whole active window if rect is None
            Coordinates are calculating from left-top corner of window
        """
        assert self.rect is not None, "Init window area before use"

        self.hide_cursor()
        if area is not None:
            im = pyautogui.screenshot(region=(self.rect[0] + area[0], self.rect[1] + area[1], area[2], area[3]))
        else:
            im = pyautogui.screenshot(region=self.rect)
        return im

    def get_screenshot(self):
        #for external use, without areas
        self.hide_cursor()
        return pyautogui.screenshot()

    def load_image(self, image):
        """Load image from reference folders"""
        if isinstance(image, Image.Image):
            return image

        img = None
        for folder in self.reference_folders:
            try:
                return Image.open(os.path.join(folder, image))
            except IOError:
                pass

        self.error_handler.report_error("Not opened image {} in [{}]".format(image, ", ".join(self.reference_folders)))
        raise errors.CanNotOpenImageException(image)

    def _get_screen(self, cache=False, zone=None, screen=None):
        """S._get_screen(cache, zone, screen) -> PIL image
            cache - bool, use cached image or make new
            zone - tuple(x, y, w, h)
            screen - PIL image. Don't use with cache option

            Cache - user logic, screen - for internal use
        """
        area = zone

        if screen is not None:
            img = screen
        elif cache:
            if self.cache_screenshot is None:
                raise errors.CacheError
            img = self.cache_screenshot
        else:
            return self._get_screenshot(area)

        if area is not None:
            return img.crop((area[0], area[1], area[0] + area[2], area[1] + area[3]))
        else:
            return img

    def take_cache_screenshot(self):
        self.cache_screenshot = self._get_screenshot()

    def find_image_result(self, img, screen_img, threshold):
        #find template on screen using OpenCV functions
        result = self.cv.find_template(img, screen_img, threshold)
        if result is not None:
            return FindResult(*result, image=img, screen=screen_img, found=True)
        else:
            return FindResult(None, None, None, None, None, image=img, screen=screen_img, found=False) #nothing found

    def find_image(self, image, threshold=0.99, cache=False, zone=None, screen=None):
        """S.find_image(image, threshold, cache, zone) -> FindResult"""
        threshold = float(threshold)
        cache = utils.to_bool(cache)

        assert 0 < threshold <= 1, "Threshold must be in (0, 1)"

        #get the screenshot to search on
        screen_img = self._get_screen(cache, zone, screen)
        #load the template image
        img = self.load_image(image)
        #locate the image with threshold and return result
        return self.find_image_result(img, screen_img, threshold)

    def is_image_on_screen(self, image, threshold=0.99, cache=False, zone=None, screen=None):
        return self.find_image(image, threshold, cache, zone, screen).found

    def image_should_be_on_screen(self, image, threshold=0.99, cache=False, zone=None, screen=None):
        # Keyword tries to find image twice.
        # If the second try fails - fails.
        result = self.find_image(image, threshold, cache, zone, screen)
        if result.found:
            return True
        ErrorHandler().report_warning("First try to locate image on screen was unsuccessful")

        #try again
        utils.sleep(0.020)
        result = self.find_image(image, threshold, cache, zone)
        if result.found:
            return True

        image_info = ("image", result.image)
        screen_info = ("screen", result.screen)
        msg = "Image was not found at screen with threshold {}".format(threshold)
        self.error_handler.report_error(msg, image_info, screen_info)
        raise RuntimeError(msg)

    def image_should_not_be_on_screen(self, image, threshold=0.99, cache=False, zone=None, screen=None):
        # Keyword tries to check image absence twice.
        # If the second try fails - fails.
        result = self.find_image(image, threshold, cache, zone, screen)
        if not result.found:
            return True
        ErrorHandler().report_warning("First try was unsuccessful")

        #try again
        utils.sleep(0.020)
        result = self.find_image(image, threshold, cache, zone)
        if not result.found:
            return True

        image_info = ("image", result.image)
        screen_info = ("screen", result.screen)
        msg = "Image was found at screen with threshold {}".format(threshold)
        self.error_handler.report_error(msg, image_info, screen_info)
        raise RuntimeError(msg)

    def wait_for_image(self, image, threshold=0.99, timeout=15, zone=None):
        timeout = float(timeout)
        start_time = datetime.datetime.now()

        #prepare image to analyze (PIL.Image format)
        img = self.load_image(image)

        #tries to locate image for given timeout
        while True:
            screen_img = self._get_screen(False, zone)
            result = self.find_image_result(img, screen_img, threshold)
            if result.found:
                return True
            utils.sleep(0)
            if (datetime.datetime.now() - start_time).seconds > timeout:
                break

        image_info = ("image", result.image)
        screen_info = ("screen", result.screen)
        msg = "Waiting for image was unsuccessful for threshold {}".format(threshold)
        self.error_handler.report_warning(msg, image_info, screen_info)
        return False

    def wait_for_image_to_hide(self, image, threshold=0.99, timeout=15, zone=None):
        timeout = float(timeout)
        start_time = datetime.datetime.now()

        # prepare image to analyze (PIL.Image format)
        img = self.load_image(image)

        # tries to locate image absence for given timeout
        while True:
            screen_img = self._get_screen(False, zone)
            result = self.find_image_result(img, screen_img, threshold)
            if not result.found:
                return True

            utils.sleep(0)
            if (datetime.datetime.now() - start_time).seconds > timeout:
                break

        image_info = ("image", result.image)
        screen_info = ("screen", result.screen)
        msg = "Waiting for image hide was unsuccessful for threshold {}".format(threshold)
        self.error_handler.report_warning(msg, image_info, screen_info)
        return False

    def wait_for_image_to_stop(self, image, threshold=0.99, timeout=15, move_threshold=0.99, step=0.1):
        timeout = float(timeout)
        threshold = float(threshold)
        move_threshold = float(move_threshold)
        step = float(step)

        assert 0 < threshold <= 1, "Threshold must be in (0, 1]"
        assert 0 < move_threshold <= 1, "Move threshold must be in (0, 1)"

        # prepare image to analyze (PIL.Image format)
        img = self.load_image(image)
        # calculate start time for timeout
        start_time = datetime.datetime.now()
        #get screenshot and locate image on it
        new_screen = self._get_screenshot()
        new_pos = self.find_image_result(img, new_screen, threshold)

        #compares last and current OpenCV template search results.
        while True:
            old_screen = new_screen
            old_pos = new_pos
            utils.sleep(step)
            new_screen = self._get_screenshot()
            new_pos = self.find_image_result(img, new_screen, threshold)

            if old_pos.found and new_pos.found:     #template is on screen, not blinking and whatever else
                #calculate the distance from the origin to the coordinates given (Euclidian norm)
                ds = math.hypot(new_pos.x-old_pos.x, new_pos.y-old_pos.y)
                diag = 1280     #hypot for 1024x768
                if 1 - ds/diag > threshold:
                    return True

            if (datetime.datetime.now() - start_time).seconds > timeout:
                break

        image_info = ("image", new_pos.image)
        screen_info = ("screen", new_pos.screen)
        msg = "Waiting for image stop was unsuccessful for threshold {}".format(threshold)
        self.error_handler.report_warning(msg, image_info, screen_info)
        return False

    def find_multiple_images(self, image, threshold=0.99, cache=False, zone=None, screen=None):
        """find_image(image, threshold, cache, zone) -> list(FindResult)"""

        threshold = float(threshold)
        cache = utils.to_bool(cache)

        screen_img = self._get_screen(cache, zone, screen)
        img = self.load_image(image)

        poses = self.cv.find_multiple_templates(img, screen_img, threshold)

        result = []
        for pos in poses:
            result.append(FindResult(*pos, image=img, screen=screen_img, found=True))

        return result

    def get_images_count(self, image, threshold=0.99, cache=False, zone=None, screen=None):
        return len(self.find_multiple_images(image, threshold, cache, zone, screen))

    def find_one_of(self, images, cache=False, zone=None, screen=None):
        """Find one of images. The one with max threshold wins and will be returned or None if no one found"""
        assert len(images) > 0, "At least one image must be set"

        screen_img = self._get_screen(False, zone, screen)
        results = []

        for image_info in images:
            result = self.find_image_result(image_info[0], screen_img, float(image_info[1]))
            if result.found:
                results.append(result)

        if not results:
            return None

        return sorted(results, key=lambda res: res.threshold, reverse=True)[0]

    def find_all_of(self, images, cache=False, zone=None, screen=None):
        pass

    def wait_for_one_of(self, images, timeout=15, zone=None):
        """wait_for_one_of_images(images, timeout, step, zone) -> bool
            images - list of (image, threshold, bool)
                image - PIL image
                threshold - threshold for image
                bool - True for wait for show, False for wait for hide
        """
        assert len(images) > 0, "You are trying to wait for empty list of images. Really?"

        timeout = float(timeout)
        start_time = datetime.datetime.now()

        #loops through images in list and locates image on screen. Returns search results.
        #if not timeout repeats taking new screenshots and searching images on it.
        #ends loop on timeout
        while True:
            screen_img = self._get_screen(False, zone)
            for image_info in images:
                #todo: optimize
                result = self.find_image_result(image_info[0], screen_img, float(image_info[1]))
                if result.found == utils.to_bool(image_info[2]):
                    return result

            utils.sleep(0)
            if (datetime.datetime.now() - start_time).seconds > timeout:
                break

        images_info = []
        for index, image in enumerate(images):
            images_info.append(("image_{}_threshold_{}".format(index, image[1]), image[0]))

        images_info.append(("screen", screen_img))
        self.error_handler.report_warning("Waiting for one of the images was unsuccessful", *images_info)
        return result

    def wait_for_all_of(self, images, timeout=15, zone=None):
        pass
    
    
    def resize_image(self, resize_percent, origFile):
        """"Stretches the initial image
            PIL.IMAGE filters:
                ANTIALIAS
                NEAREST
                BICUBIC
                BILINEAR
        """
        origresize = Image.open(origFile)
        width, height = origresize.size
        width_resize = int(resize_percent) + width
        height_resize = int(resize_percent) + height
        origresize = origresize.resize((int(round(width_resize)), int(round(height_resize))), Image.ANTIALIAS)
        
        return origresize

    def get_image_to_recognize(self, zone, cache, resize_percent, contrast, contour, invert, brightness, change_mode):

        contrast = int(contrast)
        brightness = float(brightness)
        resize_percent = int(resize_percent)

        im = self.check_to_resize(cache, zone, resize_percent)
        if change_mode:
            im = self.cv.prepare_image_to_recognize(im)
        im.save('prepared.png')
        
        if invert:
            im = self.cv.prepare_image_to_recognize(im)
            im = ImageOps.invert(im)
            im.save('invert.png')
        elif invert and change_mode == False:
            im = ImageOps.invert(im)
            im.save('invert.png')
            
        if contour:
            im = ScreenshotOperations().change_contour(im)
            im.save('contour.png')

        if contrast != 0 and brightness != 0:
            im = ScreenshotOperations().change_brightness(im, brightness)
            im = ScreenshotOperations().change_contrast(im, contrast)
            im.save('contrasted_brightness.png')

        else:
            if contrast != 0:
                im = ScreenshotOperations().change_contrast(im, contrast)
                im.save('contrast.png')

            elif brightness > 0:
                im = ScreenshotOperations().change_brightness(im, brightness)
                im.save('brightness.png')

        return im
    
    
    def check_to_resize(self, cache, zone, resize_percent):
        
        orig = self._get_screen(cache, zone)
        origFile = self._make_up_filename()
    
        if resize_percent != 0:
            resized = self.resize_image(resize_percent, origFile)
        else:
            resized = orig
        return resized

    _screenshot_counter = 0
    
    def _make_up_filename(self):
        try:
            output = BuiltIn().get_variable_value('${OUTPUT_DIR}')
        except RobotNotRunningError:
            LOGGER.info('Could not get output dir, using default - output')
            output = os.path.join(os.getcwd(), 'output')
    
        output = os.path.abspath(output)
        if not os.path.exists(output):
            os.mkdir(output)
        self._screenshot_counter += 1
    
        return os.path.join(output,
                            "guiproc-screenshot-%d.png" % (self._screenshot_counter))

        