from __future__ import division

import os
import re
from PIL import Image
from pytesseract import image_to_string
from ImageLibrary.image_processor import ImageProcessor
from ImageLibrary.error_handler import ErrorHandler
from ImageLibrary import utils
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
from robot.api import logger as LOGGER

def resize_after(img, resize):
    """"Stretches the initial image
                PIL.IMAGE filters:
                ANTIALIAS
                NEAREST
                BICUBIC
                BIL
                INEAR
    """
    """
    Loads an image from ``filename``, resizes it by ``resize_percent`` and returns the resized image.
    The resized image will is saved by default ``resized.png``.
    Percentage is relative to original size, for example 5 is half, 10 equal and 20 double size.
    Percentage must be greater than zero.
    """

    if resize > 0:
        origFile = ImageProcessor()._make_up_filename()
        img.save(origFile)
        origresize = Image.open(origFile)
        old_width, old_height = origresize.size
        new_width = int(old_width * resize)
        new_height = int(old_height * resize)
        img = img.resize((new_width, new_height), Image.ANTIALIAS)
        img.save('resized.png')
    return img


class Zone:
    def __init__(self, name, config):
        self.name = name
        self.area = None
        if isinstance(config, dict):
            self.position = tuple(config["position"])
            self.count = config["count"]
            #todo: padding and direction
            #by default padding = 0 and direction is horizontal
        elif isinstance(config, list) and len(config) == 4:
            self.area = tuple(config)
        else:
            raise RuntimeError("Zone {} configured wrong, [x, y, w, h] expected".format(name))

    @utils.add_error_info
    def get_area(self, index=None):
        if self.area is not None:
            return self.area
        else:
            assert index is not None, "Zone with subzones must be accessed by index"
            sz_height = self.position[3]
            sz_width = self.position[2] / self.count

            sz_left = self.position[0] + (int(index)-1)*sz_width
            sz_top = self.position[1]
            
            return tuple([sz_left, sz_top, sz_width, sz_height])
        
        
    '''Returns integers'''
    @utils.add_error_info
    def get_number_from_zone(self, lang=None, resize_percent=0, resize=0, contrast=0, cache=False, contour=False, invert=False, brightness=0, change_mode=True):
        img = ImageProcessor().get_image_to_recognize(self.get_area(), cache, resize_percent, contrast, contour, invert, brightness, change_mode)

        resize = int(resize)
        if int(resize) > 0:
            resize = int(resize)
            img = resize_after(img, resize)
            
        config = ""
        config += "-psm 8 -c tessedit_char_whitelist=0123456789"

        try:
            return int(image_to_string(img, config=config))
        except ValueError as e:
            msg = "Error while parsing number: " + str(e)
            ErrorHandler().report_error(msg, ("img", img))
            raise

    '''Returns float numbers'''
    @utils.add_error_info
    def get_float_number_from_zone(self, lang=None, resize_percent=0, resize=0, contrast=0, cache=False, contour=False, invert=False, brightness=0, change_mode=True):
        img = ImageProcessor().get_image_to_recognize(self.get_area(), cache, resize_percent, contrast, contour, invert, brightness, change_mode)
        resize = int(resize)
        if resize > 0:
            img = resize_after(img, resize)
            
        config = ""
        config += "-psm 8 -c tessedit_char_whitelist=.,0123456789"

        try:
            return float(image_to_string(img, config=config))
        except ValueError as e:
            msg = "Error while parsing number: " + str(e)
            ErrorHandler().report_error(msg, ("img", img))
            raise

    @utils.add_error_info
    def get_number_with_text_from_zone(self, lang=None, resize_percent=0, resize=0, contrast=0, cache=False, contour=False, invert=False, brightness=0, change_mode=True):
        img = ImageProcessor().get_image_to_recognize(self.get_area(), cache, resize_percent, contrast, contour, invert, brightness, change_mode)
        resize = int(resize)
        if resize > 0:
            img = resize_after(img, resize)
        
        config = ""
        config += "-psm 6"
    
        txt = image_to_string(img, config=config)
        
        num = re.compile('[0-9]')
        num = num.findall(txt)
        num = ''.join(num)
        num = int(num)
        
        try:
            return num
        except ValueError as e:
            msg = "Error while parsing text:" + str(e)
            ErrorHandler().report_error(msg, ("img", img))
            raise

    @utils.add_error_info
    def get_text_from_zone(self, lang=None, resize_percent=0, resize=0, contrast=0, cache=False,
                                       contour=False, invert=False, brightness=0, change_mode=True, tessdata_dir=None):

        img = ImageProcessor().get_image_to_recognize(self.get_area(), cache, resize_percent, contrast, contour, invert, brightness, change_mode)

        resize = int(resize)
        if int(resize) > 0:
            resize = int(resize)
            img = resize_after(img, resize)

        config = ""
        config += "--psm 6"

        try:
            return image_to_string(img, config=config)
        except ValueError as e:
            msg = "Error while parsing number: " + str(e)
            ErrorHandler().report_error(msg, ("img", img))
            raise

    @utils.add_error_info
    def get_image_from_zone(self, zone, image_name):
        """Returns image from given zone and saves it to 'output' under the provided image_name or default"""
        screen = self.get_area(zone)
        scr = ImageProcessor()._get_screenshot(screen)
        if image_name is not None:
            screen_name = image_name
        else:
            screen_name = 'image_from_zone'

        try:
            output = BuiltIn().get_variable_value('${OUTPUT_DIR}')
        except RobotNotRunningError:
            LOGGER.info('Could not get output dir, using default - output')
            output = os.path.join(os.getcwd(), 'output')

        scr.save(output+ '\\' + screen_name + '.png')

        return output + '\\' + screen_name + '.png'

    @utils.add_error_info
    def get_single_rgb_color_from_zone(self, zone):
        screen = self.get_area(zone)
        scr = ImageProcessor()._get_screenshot(screen)
        rgb = scr.convert('RGB')
        r, g, b = rgb.getpixel((1, 1))
    
        return [r, g, b]
