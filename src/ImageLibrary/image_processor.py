from __future__ import absolute_import
from __future__ import division

import datetime
import math
import os

import pyautogui
from ImageLibrary import utils
from ImageLibrary.GUIProcess import GUIProcess
from ImageLibrary.error_handler import ErrorHandler
from ImageLibrary.errors import *
from ImageLibrary.open_cv import OpenCV
from ImageLibrary.screenshot_operations import ScreenshotOperations
from PIL import Image, ImageChops, ImageOps
from robot.api import logger as LOGGER
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05

DEFAULT_THRESHOLD = 0.99
DEFAULT_TIMEOUT = 15


# def get_image_from_config(config):
#     '''get_image_from_config(config) -> tuple(PIL image, threshold)
#         In almost every place, where you can define image in config, you can write:
#         place:
#             image.png
#         place:
#             image: image.png
#         place:
#             image: image.png
#             threshold: 0.99
#         If threshold is not defined, DEFAULT_THRESHOLD will be used
#     '''
#     if isinstance(config, basestring):
#         return (ImageProcessor().load_image(config), DEFAULT_THRESHOLD)
#     elif isinstance(config, dict):
#         assert "image" in config, "image must be defined"
#         threshold = float(config["threshold"]) if "threshold" in config else DEFAULT_THRESHOLD
#         assert threshold > 0 and threshold <= 1, "Threshold must be in (0, 1)"
#         return (ImageProcessor().load_image(config["image"]), threshold)
#
#     raise AssertionError("Config is malformed: {} is not a valid entry for image".format(config))


class FindResult(object):
    def __init__(self, x, y, width, height, threshold, image, screen, found):
        self.x = x  # left
        self.y = y  # top
        self.width = width
        self.height = height
        self.threshold = threshold  # actual threshold
        self.image = image  # image, what was found
        self.screen = screen  # screen, where it was found
        self.found = found  # was template really found
    
    def get_pos(self):
        return (self.x, self.y, self.width, self.height)


class ImageProcessor(object):
    ###Image processing system - open files if needed, find them on screen, etc
    
    def __init__(self, error_handler, output_dir):
        self.cv = OpenCV()
        self.cache_screenshot = None
        self.error_handler = error_handler
        self.output_dir = output_dir
    
    def _screenshot(self, zone=None):
        # _screenshot([area]) -> Image
        # Get screenshot of specified area or whole game window if rect is None
        # Coordinates are calculating from left-top corner of window
        
        win_area = GUIProcess().get_window_area()
        
        if zone is not None:
            im = pyautogui.screenshot(
                region=(win_area[0] + int(zone[0]), win_area[1] + int(zone[1]), int(zone[2]), int(zone[3])))
        else:
            im = pyautogui.screenshot(region=win_area)
        return im
    
    def get_screenshot(self):
        # for external use, without areas
        # self.win_area = GUIProcess().get_window_area()
        # return pyautogui.screenshot(region=self.win_area)
        return pyautogui.screenshot()
    
    def load_image(self, image):
        try:
            return Image.open(image)
        except IOError:
            pass
            # self.error_handler.report_error("Not opened image {}".format(image))
            # raise CanNotOpenImageException(image)
    
    def _get_screen(self, cache=None, zone=None, screen=None):
        # _get_screen(cache, zone, screen) -> PIL image
        # cache - bool, use cached image or make new
        # zone - tuple(x, y, w, h)
        # screen - PIL image. Don't use with cache option
        #
        # Cache - user logic, screen - for internal use
        
        search_zone = zone
        scr = screen
        
        if scr is not None:
            img = scr
            return img
        elif cache:
            if self.cache_screenshot is None:
                raise CacheError
            img = self.cache_screenshot
            return img
        else:
            return self._screenshot(search_zone)
            
            # if area is not None:
            #     return img.crop((search_zone[0], search_zone[1], search_zone[0] + search_zone[2], search_zone[1] + search_zone[3]))
            # else:
            #     return img
    
    def take_cache_screenshot(self):
        return self.get_screenshot()
    
    def _find_image_result(self, img, screen_img, threshold):
        result = OpenCV().find_template(img, screen_img, threshold)
        if result is not None:
            return FindResult(*result, image=img, screen=screen_img, found=True)
        else:
            return FindResult(None, None, None, None, None, image=img, screen=screen_img, found=False)  # nothing found
    
    def _find_image(self, image, threshold=0.99, cache=False, zone=None, screen=None):
        # _find_image(image, threshold, cache, zone) -> FindResult
        threshold = float(threshold)
        cache = utils.to_bool(cache)
        
        assert threshold > 0 and threshold <= 1, "Threshold must be between (0, 1)"
        screen_img = self._get_screen(cache, zone, screen)
        img = self.load_image(image)
        return self._find_image_result(img, screen_img, threshold)
    
    def find_image(self, image, threshold=0.99, cache=False, zone=None, screen=None):
        result = ImageProcessor(self.error_handler, self.output_dir)._find_image(image, threshold, cache, zone,
                                                                                 screen).found
        if result:
            LOGGER.info('Template was found on screen with threshold:{}'.format(threshold))
            return True
        else:
            LOGGER.info('Template was not found on screen with threshold {}'.format(threshold))
            return False
    
    def _is_image_on_screen(self, image, threshold=0.99, cache=False, zone=None, screen=None):
        return self._find_image(image, threshold, cache, zone, screen).found
    
    def _image_should_be_on_screen(self, image, threshold=0.99, cache=False, zone=None, screen=None):
        result = self._find_image(image, threshold, cache, zone, screen)
        if result.found:
            return True
        self.error_handler.report_warning("First try was unsuccessful")
        
        # try again
        utils.sleep(0.020)
        result = self._find_image(image, threshold, cache, zone)
        if result.found:
            return True
        
        image_info = ("image", result.image)
        screen_info = ("screen", result.screen)
        msg = "Image was not found at screen with threshold {}".format(threshold)
        self.error_handler.report_error(msg, image_info, screen_info)
        raise RuntimeError(msg)
    
    def _image_should_not_be_on_screen(self, image, threshold=0.99, cache=False, zone=None, screen=None):
        result = self._find_image(image, threshold, cache, zone, screen)
        if not result.found:
            return True
        self.error_handler.report_warning("First try was unsuccessful")
        
        # try again
        utils.sleep(0.020)
        result = self._find_image(image, threshold, cache, zone, screen)
        if not result.found:
            return True
        
        image_info = ("image", result.image)
        screen_info = ("screen", result.screen)
        msg = "Image was found on screen with threshold {}".format(threshold)
        self.error_handler.report_error(msg, image_info, screen_info)
        raise RuntimeError(msg)
    
    def _wait_for_image(self, image, threshold=0.99, timeout=15, zone=None):
        timeout = float(timeout)
        start_time = datetime.datetime.now()
        
        img = self.load_image(image)
        
        while True:
            screen_img = self._get_screen(False, zone)
            result = self._find_image_result(img, screen_img, threshold)
            if result.found:
                return True
            utils.sleep(0)
            if (datetime.datetime.now() - start_time).seconds > int(timeout):
                break
        
        image_info = ("image", result.image)
        screen_info = ("screen", result.screen)
        
        msg = "Waiting for image was unsucessful with threshold {} and timeout {} sec".format(threshold, int(timeout))
        self.error_handler.report_warning(msg, image_info, screen_info)
        return False
    
    def _wait_for_image_to_hide(self, image, threshold=0.99, timeout=15, zone=None):
        timeout = float(timeout)
        start_time = datetime.datetime.now()
        
        img = self.load_image(image)
        
        while True:
            screen_img = self._screenshot(zone)
            result = self._find_image_result(img, screen_img, threshold)
            if not result.found:
                return True
            utils.sleep(0)
            if (datetime.datetime.now() - start_time).seconds > int(timeout):
                break
        
        image_info = ("image", result.image)
        screen_info = ("screen", result.screen)
        msg = "Waiting for image hide was unsuccessful for threshold {} and timeout {}".format(threshold, int(timeout))
        self.error_handler.report_warning(msg, image_info, screen_info)
        return False
    
    def _wait_for_image_to_stop(self, image, threshold=0.99, timeout=15, move_threshold=0.99, step=0.1):
        timeout = float(timeout)
        threshold = float(threshold)
        move_threshold = float(move_threshold)
        step = float(step)
        
        assert threshold > 0 and threshold <= 1, "Threshold must be between in (0, 1)"
        assert move_threshold > 0 and move_threshold <= 1, "Move threshold must be between (0, 1)"
        
        img = self.load_image(image)
        
        start_time = datetime.datetime.now()
        
        new_screen = self._screenshot()
        new_pos = self._find_image_result(img, new_screen, threshold)
        
        while True:
            old_scren = new_screen
            old_pos = new_pos
            utils.sleep(step)
            new_screen = self._screenshot()
            new_pos = self._find_image_result(img, new_screen, threshold)
            
            if old_pos.found and new_pos.found:  # template is on screen, not blinking and whatever else
                ds = math.hypot(new_pos.x - old_pos.x, new_pos.y - old_pos.y)
                diag = 1280  # hypot for 1024x768
                if 1 - ds / diag > threshold:
                    return True
            
            if (datetime.datetime.now() - start_time).seconds > int(timeout):
                break
        
        image_info = ("image", new_pos.image)
        screen_info = ("screen", new_pos.screen)
        msg = "Waiting for image stop was unsuccessful for threshold {} and timeout {}".format(threshold, int(timeout))
        self.error_handler.report_warning(msg, image_info, screen_info)
        return False
    
    def find_multiple_images(self, image, threshold=0.99, cache=False, zone=None, screen=None):
        # _find_image(image, threshold, cache, zone) -> list(FindResult)
        
        
        threshold = float(threshold)
        cache = utils.to_bool(cache)
        
        screen_img = self._get_screen(cache, zone, screen)
        img = self.load_image(image)
        
        poses = OpenCV().find_multiple_templates(img, screen_img, threshold)
        
        result = []
        for pos in poses:
            result.append(FindResult(*pos, image=img, screen=screen_img, found=True))
        
        return result
    
    def _get_images_count(self, image, threshold=0.99, cache=False, zone=None, screen=None):
        return len(self.find_multiple_images(image, threshold, cache, zone, screen))
    
    def find_one_of(self, images, cache=False, zone=None, screen=None):
        ###Find one of images. The one with max threshold wins and will be returned or None if no one found
        assert len(images) > 0, "At least one image must be set"
        
        screen_img = self._get_screen(False, zone, screen)
        results = []
        
        for image_info in images:
            result = self._find_image_result(image_info[0], screen_img, float(image_info[1]))
            if result.found:
                results.append(result)
        
        if not results:
            return None
        
        return sorted(results, key=lambda res: res.threshold, reverse=True)[0]
    
    def find_all_of(self, images, cache=False, zone=None, screen=None):
        pass
    
    def wait_for_one_of(self, images, timeout=15, zone=None):
        # wait_for_one_of_images(images, timeout, step, zone) -> bool
        # images - list of (image, threshold, bool)
        #     image - PIL image
        #     threshold - threshold for image
        #     bool - True for wait for show, False for wait for hide
        
        assert len(images) > 0, "You are trying to wait for empty list of images. Really?"
        
        timeout = float(timeout)
        start_time = datetime.datetime.now()
        
        while True:
            screen_img = self._screenshot(zone)
            for image_info in images:
                # todo: optimize
                result = self._find_image_result(image_info[0], screen_img, float(image_info[1]))
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
    
    def resize_image(self, resize_percent, filename, output_filename='resized.png'):
        """
        Loads an image from ``filename``, resizes it by ``resize_percent`` and returns the resized image.
        If ``output_filename`` is not None, the resized image will also be saved to file (default ``resized.png``).

        Percentage is relative to original size, for example 50 is half, 100 equal and 200 double size.

        Percentage must be greater than zero.
        """
        with Image.open(filename) as input_image:
            if resize_percent <= 0:
                raise ValueError('resize_percent must be greater zero')
            old_width, old_height = input_image.size
            new_width = int(old_width * resize_percent / 100)
            new_height = int(old_height * resize_percent / 100)
            output_image = input_image.resize((new_width, new_height), Image.ANTIALIAS)
            if output_filename:
                output_image.save(output_filename)
        return output_image

    def get_image_to_recognize(self, zone, resize_percent, contrast, invert, brightness, change_mode, win_area, cache):
        
        im = self.check_to_resize(zone, resize_percent)
    
        if change_mode:
            im = self.cv.prepare_image_to_recognize(im)
        
        if invert:
            im = self.cv.prepare_image_to_recognize(im)
            im = ImageOps.invert(im)
            im.save('inverted.png')
        
        if contrast != 0 and brightness != 0:
            im = ScreenshotOperations().change_brightness(im, brightness)
            im = ScreenshotOperations().change_contrast(im, contrast)
            im.save('contrast_and_brightness.png')

        
        elif contrast != 0:
            im = ScreenshotOperations().change_contrast(im, contrast)
            im.save('contrasted.png')

        elif brightness != 0:
            im = ScreenshotOperations().change_brightness(im, brightness)
            im.save('brightness.png')
            
        return im
    
    def get_image_to_recognize_with_background(self, zone, resize_percent, contrast, background, brightness,
                                               invert, cache):
        ### Merges the screenshot image and the background and makes a new image with a plain background. After converts image to black and grey colors and inverts
        # colors. Background images of each game are stored in l_screens\background folder. Use the same image name and 'background' parameter name
        #  in test: background = game_name
        
        im = self.check_to_resize(zone, resize_percent)
        
        result = im
        
        if background is not None:
            image1 = Image.open(background)
            try:
                image = ImageChops.difference(image1, im)
                image = image.convert('L')
                result = ImageOps.invert(image)
            except ValueError:
                LOGGER.error('Images do not match. To remove background images should be the same size.')
                raise
        
        if contrast and brightness != 0:
            result = ScreenshotOperations().change_contrast(result, contrast)
            result = ScreenshotOperations().change_brightness(result, brightness)
            result.save('contrast_and_brightness.png')
        
        elif brightness != 0:
            result = ScreenshotOperations().change_brightness(result, brightness)
            result.save('brightness.png')
        
        elif contrast != 0:
            result = ScreenshotOperations().change_contrast(result, contrast)
            result.save('contrast.png')
        
        if invert:
            result = ImageOps.invert(result)
            result.save('invert.png')
        
        return result
    
    def check_to_resize(self, zone, resize_percent):
        orig = self._screenshot(zone)
        origFile = self._make_up_filename()
        orig.save(origFile)
        
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
                            "guiproc-screenshot-%d.png" % self._screenshot_counter)
    
    # animations
    def _wait_for_animation_stops(self, zone, timeout=DEFAULT_TIMEOUT, threshold=DEFAULT_THRESHOLD, step=0.05):
        timeout = float(timeout)
        threshold = float(threshold)
        step = float(step)
        
        new_screen = self._screenshot(zone)
        start_time = datetime.datetime.now()
        
        while True:
            utils.sleep(step)
            old_screen = new_screen
            new_screen = self._get_screen(False, zone)
            
            result = self._find_image_result(new_screen, old_screen, threshold)
            if result.found:
                return True
            if (datetime.datetime.now() - start_time).seconds > timeout:
                break
        
        self.error_handler.report_warning("Timeout exceeded while waiting for animation stops")
        return False
    
    def _wait_for_animation_starts(self, zone, timeout=DEFAULT_TIMEOUT, threshold=DEFAULT_THRESHOLD, step=0.05):
        timeout = float(timeout)
        threshold = float(threshold)
        step = float(step)
        
        new_screen = self._screenshot(zone)
        start_time = datetime.datetime.now()
        
        while True:
            utils.sleep(step)
            old_screen = new_screen
            new_screen = self._get_screen(False, zone)
            
            result = self._find_image_result(new_screen, old_screen, threshold)
            if not result.found:
                return True
            if (datetime.datetime.now() - start_time).seconds > timeout:
                break
        
        self.error_handler.report_warning("Timeout exceeded while waiting for animation starts")
        return False
    
    def _is_zone_animating(self, zone, threshold=DEFAULT_THRESHOLD, step=0.5):
        threshold = float(threshold)
        step = float(step)
        
        old_screen = self._screenshot(zone)
        utils.sleep(step)
        new_screen = self._screenshot(zone)
        
        return not self._find_image_result(new_screen, old_screen, threshold).found
    
    def save_zone_content_to_output(self, zone):
        ###FOR DEBUG: saves the content (screenshot) of the provided zone. Pass zone. Image is saved in the output folder in launcher
        
        
        screen_img = self._screenshot(zone)
        ErrorHandler().save_pictures([(screen_img, "zone")])
    
    def _is_animating(self, zone, threshold, step):
        threshold = float(threshold)
        step = float(step)
        
        old_screen = self._get_screen(False, zone)
        utils.sleep(step)
        new_screen = self._get_screen(False, zone)
        
        return not self._find_image_result(new_screen, old_screen, threshold).found
