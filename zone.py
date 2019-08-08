from __future__ import absolute_import

from pytesseract import image_to_string
from .image_processor import ImageProcessor
from .screenshot_operations import ScreenshotOperations
from .error_handler import ErrorHandler
from .open_cv import MatchObjects
from PIL import Image
import os
import re
from ImageLibrary import utils
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
from robot.api import logger as LOGGER


class Zone(object):
    def __init__(self, win_area=None):
        if win_area is not None:
            self.win_area = tuple(win_area)
        # if (isinstance(config, dict)):
        #     self.position = tuple(config["position"])
        #     self.count = config["count"]
        #     #todo: padding and direction
        #     #by default padding = 0 and directin is horizontal
        # elif isinstance(config, list) and len(config) == 4:
        #     self.area = tuple(config)
        # else:
        #     raise RuntimeError("Zone {} configured wrong, [x, y, w, h] expected".format(name))

    # @utils.add_error_info
    # def get_area(self):
    #     if self.area is not None:
    #         return self.area
    #     else:
    #         pass
        # else:
        #     assert index is not None, "Zone with subzones must be accesed by index"
        #     sz_height = self.position[3]
        #     sz_width = self.position[2] / self.count
        #
        #     sz_left = self.position[0] + (int(index)-1)*sz_width
        #     sz_top = self.position[1]
        #
        #     return tuple([sz_left, sz_top, sz_width, sz_height])
        
        
    '''Returns integers'''
    @utils.add_error_info
    def get_number_from_zone(self, zone=None, lang=None, resize_percent=0, resize=0, contrast=0, cache=False, background=None, contour=False, invert=False, brightness=0, change_mode=True):
        if background is not None:
            img = ImageProcessor().get_image_to_recognize_with_background(zone, cache, resize_percent, contrast, background, contour, brightness, invert)
        else:
            img = ImageProcessor().get_image_to_recognize(zone, cache, resize_percent, contrast, contour, invert, brightness, change_mode, self.win_area)

        print(img)

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
            return int(txt)
        except ValueError as e:
            msg = "Error while parsing number: " + str(e)
            ErrorHandler().report_error(msg, ("img", img))
            raise

    '''Returns float numbers'''
    @utils.add_error_info
    def get_float_number_from_zone(self, lang=None, resize_percent=0, resize=0, contrast=0, cache=False, contour=False, invert=False, brightness=0, change_mode=True):
        img = ImageProcessor().get_image_to_recognize(self.area, cache, resize_percent, contrast, contour, invert, brightness, change_mode)

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
            ErrorHandler().report_error(msg, ("img", img))
            raise

    @utils.add_error_info
    def get_number_with_text_from_zone(self, lang=None, resize_percent=0, resize=0, contrast=0, cache=False, background=None, contour=False, invert=False, brightness=0, change_mode=True):
        if background is not None:
            img = ImageProcessor().get_image_to_recognize_with_background(self.area, cache, resize_percent, contrast, background, contour, brightness, invert)
        else:
            img = ImageProcessor().get_image_to_recognize(self.area, cache, resize_percent, contrast, contour, invert, brightness, change_mode)
            
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
            ErrorHandler().report_error(msg, ("img", img))
            raise
        
    def get_text_from_zone(self, lang=None, resize_percent=0, contrast=0, cache=False, contour=False, invert=False, brightness=0, change_mode=True):
        
        img = ImageProcessor().get_image_to_recognize(self.area, cache, resize_percent, contrast, contour, invert, brightness, change_mode)
        
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
            ErrorHandler().report_error(msg, ("img", img))
            raise
        
    def get_image_from_zone(self, zone):
        screen = self.get_area(zone)
        scr = ImageProcessor()._get_screenshot(screen)

        try:
            output = BuiltIn().get_variable_value('${OUTPUT_DIR}')
        except RobotNotRunningError:
            LOGGER.info('Could not get output dir, using default - output')
            output = os.path.join(os.getcwd(), 'output')

        scr.save(output + '\\scr.png')

        return output + '\\scr.png'

    def is_template_in_zone(self, template, zone, invert=False):
        """Pass template(s) as images to be found on screen in the given zone.
        Takes a screenshot of the passed area and find given data on the screenshot.
        Returns results for each argument."""

        area = self.get_area(zone)
        screen = ImageProcessor()._get_screenshot(area)

        if invert:
            screen = ScreenshotOperations().invert_image(screen)

        return MatchObjects().match_objects_with_knn(screen, template)
    
    def match_template_in_zone(self, template, zone, invert=False):
        area = self.get_area(zone)
        screen = ImageProcessor()._get_screenshot(area)

        if invert:
            screen = ScreenshotOperations().invert_image(screen)

        return MatchObjects().match_objects(template, screen)

    def get_template_position(self, template, zone, threshold=None):
        """The same as is_template_in_zone, but returns templates positions after search"""
        cache = ImageProcessor().take_cache_screenshot()
        screen = ImageProcessor()._get_screen(zone, cache)

        return MatchObjects().match_and_return_coordinates(template, screen, threshold)

    # ###ANIMATIONS###
    # def wait_for_animation_stops(self, zone=None, timeout=15, threshold=0.9, step=0.1):
    #     '''Wait until animation stops in the given zone or in the whole active window if zone is not provided.
    #         Pass _zone_, _timeout_, _step_, _thrreshold_ as arguments. All are optional.
    #
    #         Examples:
    #         |   Wait For Animation Stops | zone=zone_coordinates | timeout=15 | threshold=0.95 | step=0.1
    #     '''
    #     zone = self.zones[zone].get_area() if zone is not None else None
    #     return ImageProcessor().wait_for_animation_stops(zone, timeout, threshold, step)
    #
    #
    # def wait_for_animation_starts(self, zone=None, timeout=15, threshold=0.9, step=0.1):
    #     '''Same as `Wait For Animation Stops` but on the contrary.
    #     '''
    #     zone = self.zones[zone].get_area() if zone is not None else None
    #     return ImageProcessor().wait_for_animation_starts(zone, timeout, threshold, step)
    #
    #
    # def is_zone_animating(self, zone=None, threshold=0.9, step=0.1):
    #     '''Checks if the given zone is animating. Returns boolean.
    #         Pass _zone_, _threshold_, _step_ as arguments. All are optional. If zone is not provided
    #             the while active area is taken.
    #
    #         Examples:
    #         |   ${is_animating} = | Is Zone Animating | zone=game_zone | threshold=0.9 | step=0.1
    #     '''
    #     zone = self.zones[zone].get_area() if zone is not None else None
    #     return ImageProcessor().is_animating(zone, threshold, step)

