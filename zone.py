from __future__ import absolute_import
import os
import re
from PIL import Image
from pytesseract import image_to_string
from .image_processor import ImageProcessor
from .error_handler import ErrorHandler
from .open_cv import MatchObjects
from ImageLibrary import utils
from .screenshot_operations import ScreenshotOperations
from GUIProcess import GUIProcess
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
from robot.api import logger as LOGGER



class Zone(object):
    def __init__(self, screenshot_folder):
        self.screenshot_folder = screenshot_folder
        
    '''Returns integers'''
    @utils.add_error_info
    def get_number_from_zone(self, zone=None, lang=None, resize_percent=0, resize=0, contrast=0, cache=False, background=None, invert=False, brightness=0, change_mode=True):
        self.window_area = GUIProcess().get_window_area()

        if background is not None:
            img = ImageProcessor().get_image_to_recognize_with_background(zone, cache, resize_percent, contrast, background, brightness, invert)
        else:
            img = ImageProcessor().get_image_to_recognize(zone, cache, resize_percent, contrast, invert, brightness, change_mode, self.window_area)

        if resize > 0:
            resize = int(resize)
            origFile = ImageProcessor()._make_up_filename()
            img.save(origFile)
            origresize = Image.open(origFile)
            width, height = origresize.size
            width_resize = width * int(resize) / width + width
            height_resize = height * int(resize) / height + height
            img = origresize.resize((int(round(width_resize)), int(round(height_resize))), Image.ANTIALIAS)
            img.save('resized.png')
        
        
        mydir = os.path.abspath(os.path.dirname(__file__))
        resdir = os.path.abspath(os.path.join(os.sep, mydir, r'..\..\resources'))
    
        config = ""
        if lang:
            config += ("--tessdata-dir %s -l %s " % (resdir, lang)).replace("\\", "//")
        config += "-psm 8 -c tessedit_char_whitelist=0123456789"
            
        txt = image_to_string(img, config=config)

        try:
            return txt
        except ValueError as e:
            msg = "Error while parsing number: " + str(e)
            ErrorHandler(self.screenshot_folder).report_error(msg, ("img", img))
            raise

    '''Returns float numbers'''
    @utils.add_error_info
    def get_float_number_from_zone(self, zone=None, lang=None, resize_percent=0, resize=0, contrast=0, cache=False, invert=False, brightness=0, change_mode=True):
        self.window_area = GUIProcess().get_window_area()

        img = ImageProcessor().get_image_to_recognize(zone, cache, resize_percent, contrast, invert, brightness, change_mode, self.window_area)

        if resize > 0:
            resize = int(resize)
            origFile = ImageProcessor()._make_up_filename()
            img.save(origFile)
            origresize = Image.open(origFile)
            width, height = origresize.size
            width_resize = width * int(resize) / width + width
            height_resize = height * int(resize) / height + height
            img = origresize.resize((int(round(width_resize)), int(round(height_resize))), Image.ANTIALIAS)
            img.save('resized.png')

        mydir = os.path.abspath(os.path.dirname(__file__))
        resdir = os.path.abspath(os.path.join(os.sep, mydir, r'..\..\resources'))

        config = ""
        if lang:
            config += ("--tessdata-dir %s -l %s " % (resdir, lang)).replace("\\", "//")
        config += "-psm 8 -c tessedit_char_whitelist=.,0123456789"

        txt = image_to_string(img, config=config)
        txt = float(txt)
        try:
            return txt
        except ValueError as e:
            msg = "Error while parsing number: " + str(e)
            ErrorHandler(self.screenshot_folder).report_error(msg, ("img", img))
            raise

    @utils.add_error_info
    def get_number_with_text_from_zone(self, zone=None, lang=None, resize_percent=0, resize=0, contrast=0, cache=False, background=None, invert=False, brightness=0, change_mode=True):
        self.window_area = GUIProcess().get_window_area()

        if background is not None:
            img = ImageProcessor().get_image_to_recognize_with_background(zone, cache, resize_percent, contrast, invert, brightness, change_mode)
        else:
            img = ImageProcessor().get_image_to_recognize(zone, cache, resize_percent, contrast, invert, brightness, change_mode, self.window_area)

        if resize > 0:
            resize = int(resize)
            origFile = ImageProcessor()._make_up_filename()
            img.save(origFile)
            origresize = Image.open(origFile)
            width, height = origresize.size
            width_resize = width * int(resize) / width + width
            height_resize = height * int(resize) / height + height
            img = origresize.resize((int(round(width_resize)), int(round(height_resize))), Image.ANTIALIAS)
            img.save('resized.png')

        mydir = os.path.abspath(os.path.dirname(__file__))
        resdir = os.path.abspath(os.path.join(os.sep, mydir, r'..\..\resources'))

        config = ""
        if lang:
            config += ("--tessdata-dir %s -l %s " % (resdir, lang)).replace("\\", "//")
        config += "-psm 6"

        txt = image_to_string(img, config=config)

        num = re.compile('[0-9]')
        num = num.findall(txt)
        num = ''.join(num)

        try:
            return int(num)
        except ValueError as e:
            msg = "Error while parsing text:" + str(e)
            ErrorHandler(self.screenshot_folder).report_error(msg, ("img", img))
            raise

    def get_text_from_zone(self, zone=None, lang=None, resize_percent=0, contrast=0, cache=False, invert=False, brightness=0, change_mode=True):
        self.window_area = GUIProcess().get_window_area()

        img = ImageProcessor().get_image_to_recognize(zone, cache, resize_percent, contrast, invert, brightness, change_mode, self.window_area)

        mydir = os.path.abspath(os.path.dirname(__file__))
        resdir = os.path.abspath(os.path.join(os.sep, mydir, r'..\..\resources'))

        config = ""
        if lang:
            config += ("--tessdata-dir %s -l %s " % (resdir, lang)).replace("\\", "//")
        config += "-psm 6"

        txt = image_to_string(img, config=config)

        try:
            return txt
        except ValueError as e:
            msg = "Error while parsing text:" + str(e)
            ErrorHandler(self.screenshot_folder).report_error(msg, ("img", img))
            raise


    def get_image_from_zone(self, zone):
        window_area = GUIProcess().get_window_area()
        scr = ImageProcessor()._get_screenshot(zone, window_area)

        try:
            output = BuiltIn().get_variable_value('${OUTPUT_DIR}')
        except RobotNotRunningError:
            LOGGER.info('Could not get output dir, using default - output')
            output = os.path.join(os.getcwd(), 'output')

        scr.save(output + '\\scr.png')

        return output + '\\scr.png'

    # def is_template_in_zone(self, template, invert=False):
    #     """Pass template(s) as images to be found on screen in the given zone.
    #     Takes a screenshot of the passed area and find given data on the screenshot.
    #     Returns results for each argument."""
    #
    #     window_area = GUIProcess().get_window_area()
    #     screen = ImageProcessor()._get_screenshot(window_area)
    #
    #     if invert:
    #         screen = ScreenshotOperations().invert_image(screen)

    #    return MatchObjects().match_objects_with_knn(screen, template)

    # def match_template_in_zone(self, template, zone, invert=False):
    #     window_area = GUIProcess().get_window_area()
    #     screen = ImageProcessor()._get_screenshot(zone, window_area)
    #
    #     if invert:
    #         screen = ScreenshotOperations().invert_image(screen)
    #
    #     return MatchObjects().match_objects(template, screen)

    def get_template_position(self, template, zone, threshold=None):
        """The same as is_template_in_zone, but returns templates positions after search"""
        cache = ImageProcessor().take_cache_screenshot()
        screen = ImageProcessor()._get_screen(zone, cache)

        return MatchObjects().match_and_return_coordinates(template, screen, threshold)

