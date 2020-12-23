from __future__ import absolute_import

import os
import re

from ImageLibrary import utils
from ImageLibrary.GUIProcess import GUIProcess
from ImageLibrary.error_handler import ErrorHandler
from ImageLibrary.image_processor import ImageProcessor
from ImageLibrary.open_cv import MatchObjects
from PIL import Image
from pytesseract import image_to_string
from robot.api import logger as LOGGER

def resize_img(img, resize):
    resize = int(resize) * 10

    wpercent = (int(resize) / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((int(resize), hsize), Image.ANTIALIAS)
    img.save('resized.png')
    
    return img


class Zone(object):
    def __init__(self, screenshot_folder, error_handler):
        self.screenshot_folder = screenshot_folder
        self.error_handler = error_handler
        self.cache = False
    
    '''Returns integers'''
    
    @utils.add_error_info
    def get_number_from_zone(self, zone=None, lang=None, resize_percent=0, resize=0, contrast=0,
                             background=None, invert=False, brightness=0, change_mode=True, tessdata_dir=None,
                             cache=False):
        """Returns an integer from the given zone. NB! If zone is not provided the whole acctive window is taken.

            Examples:
            | Get Number From Zone | zone=[x  y  w  h] | lang=eng | resize_percent=15 | resize=0.95 | contrast=0.1 | background=${None} | invert=${False} |
            brightness=0 | change_mode=${True}

            *resize_percent* - changes the screeshot size right after it is taken\n

            vs *resize* - changes the screenshot size after all other operations with screenshot (contrast, invert, etc)\n

            *contrast* - changes the contrast of the screeshot\n
            *background* - provide the pattern image of the same size, as the keyword zone. As param value pass the pattern location\n
            the common parts of two images will be removed returning the difference image.\n
            *invert* - inverts the colors (mind that it inverts the black-white image; if you want to keep the original colors, use with \n
            change_mode=${False} param).
            *change_mode* - by default is ${True}, changes to black-white format. If you need to keep the original - pass ${False)


        """
        
        self.window_area = GUIProcess().get_window_area()
        
        if background is not None:
            img = ImageProcessor(self.error_handler, self.screenshot_folder).get_image_to_recognize_with_background(
                zone, resize_percent, contrast, background, brightness, invert, cache)
        else:
            img = ImageProcessor(self.error_handler, self.screenshot_folder).get_image_to_recognize(zone,
                                                                                                    resize_percent,
                                                                                                    contrast, invert,
                                                                                                    brightness,
                                                                                                    change_mode,
                                                                                                    self.window_area,
                                                                                                    cache)
        
        if int(resize) > 0:
            resize = int(resize)
            img = resize_img(img, resize)
            
        config = ""
        if lang:
            mydir = os.path.abspath(os.path.dirname(__file__))
            resdir = os.path.abspath(os.path.join(os.sep, mydir, tessdata_dir))
            config += ("--tessdata-dir %s -l %s " % (resdir, lang)).replace("\\", "//")
        config += "--psm 8 -c tessedit_char_whitelist=0123456789"
        
        txt = image_to_string(img, config=config)
        
        try:
            return int(txt)
        except ValueError as e:
            msg = "Error while parsing number: " + str(e)
            ErrorHandler(self.screenshot_folder).report_error(msg, ("img", img))
            raise
    
    '''Returns float numbers'''
    
    @utils.add_error_info
    def get_float_number_from_zone(self, zone=None, lang=None, resize_percent=0, resize=0, contrast=0, background=None,
                                   invert=False, brightness=0, change_mode=True, tessdata_dir=None, cache=False):
        """Returns the *float*. For details check `Get Number From Zone`
            Examples:
            | Get Float Number From Zone | zone=[x  y  w  h] | lang=eng | resize_percent=15 | resize=0.95 | contrast=0.1 | background=${None} | invert=${False} |
            brightness=0 | change_mode=${True}
        """
        
        self.window_area = GUIProcess().get_window_area()
        
        if background is not None:
            img = ImageProcessor(self.error_handler, self.screenshot_folder).get_image_to_recognize_with_background(
                zone, resize_percent, contrast, background, brightness, invert, cache)
        else:
            img = ImageProcessor(self.error_handler, self.screenshot_folder).get_image_to_recognize(zone,
                                                                                                resize_percent,
                                                                                                contrast, invert,
                                                                                                brightness, change_mode,
                                                                                                self.window_area, cache)
        
        if int(resize) > 0:
            resize = int(resize)
            img = resize_img(img, resize)
            
        config = ""
        if lang:
            mydir = os.path.abspath(os.path.dirname(__file__))
            resdir = os.path.abspath(os.path.join(os.sep, mydir, tessdata_dir))
            config += ("--tessdata-dir %s -l %s " % (resdir, lang)).replace("\\", "//")
        config += "--psm 8 -c tessedit_char_whitelist=.,0123456789"
        
        txt = image_to_string(img, config=config)
        txt = float(txt)
        try:
            return txt
        except ValueError as e:
            msg = "Error while parsing number: " + str(e)
            ErrorHandler(self.screenshot_folder).report_error(msg, ("img", img))
            raise
    
    @utils.add_error_info
    def get_number_with_text_from_zone(self, zone=None, lang=None, resize_percent=0, resize=0, contrast=0,
                                       background=None, invert=False, brightness=0, change_mode=True, tessdata_dir=None,
                                       cache=False):
        """Returns only number from zone with text and number. For arguments details check `Get Number From Zone`
            Examples:
            | Get Number With Text From Zone | zone=[x  y  w  h] | lang=eng | resize_percent=15 | resize=0.95 | contrast=0.1 | background=${None} | invert=${False} |
            brightness=0 | change_mode=${True}
        """
        
        self.window_area = GUIProcess().get_window_area()
        
        if background is not None:
            img = ImageProcessor(self.error_handler, self.screenshot_folder).get_image_to_recognize_with_background(
                zone, resize_percent, contrast, background, invert, brightness, cache)
        else:
            img = ImageProcessor(self.error_handler, self.screenshot_folder).get_image_to_recognize(zone,
                                                                                                    resize_percent,
                                                                                                    contrast, invert,
                                                                                                    brightness,
                                                                                                    change_mode,
                                                                                                    self.window_area,
                                                                                                    cache)
        
        if int(resize) > 0:
            resize = int(resize)
            img = resize_img(img, resize)
        
        config = ""
        if lang:
            mydir = os.path.abspath(os.path.dirname(__file__))
            resdir = os.path.abspath(os.path.join(os.sep, mydir, tessdata_dir))
            config += ("--tessdata-dir %s -l %s " % (resdir, lang)).replace("\\", "//")
        config += "--psm 6"
        
        txt = image_to_string(img, config=config)
        
        num = re.compile('[0-9|.0-9]+')
        num = num.findall(txt)
        num = ''.join(num)
        
        try:
            return float(num)
        except ValueError as e:
            msg = "Error while parsing text:" + str(e)
            ErrorHandler(self.screenshot_folder).report_error(msg, ("img", img))
            raise
    
    @utils.add_error_info
    def get_text_from_zone(self, zone=None, lang=None, resize_percent=0, resize=0, contrast=0, invert=False, background=None,
                           brightness=0, change_mode=True, tessdata_dir=None, cache=False):
        """Returns text from zone with text. For arguments details check `Get Number From Zone`
            Examples:
            | Get Number With Text From Zone | zone=[x  y  w  h] | lang=eng | resize_percent=15 | resize=0.95 | contrast=0.1 | background=${None} | invert=${False} |
            brightness=0 | change_mode=${True}
        """
        
        self.window_area = GUIProcess().get_window_area()

        if background is not None:
            img = ImageProcessor(self.error_handler, self.screenshot_folder).get_image_to_recognize_with_background(
                zone, cache, resize_percent, contrast, background, invert, brightness)
        else:
            img = ImageProcessor(self.error_handler, self.screenshot_folder).get_image_to_recognize(zone,
                                                                                                resize_percent,
                                                                                                contrast, invert,
                                                                                                brightness, change_mode,
                                                                                                self.window_area, cache)
        if int(resize) > 0:
            resize = int(resize)
            img = resize_img(img, resize)
            
        config = ""
        if lang:
            mydir = os.path.abspath(os.path.dirname(__file__))
            resdir = os.path.abspath(os.path.join(os.sep, mydir, tessdata_dir))
            config += ("--tessdata-dir %s -l %s " % (resdir, lang)).replace("\\", "//")
        config += "--psm 6"
        
        txt = image_to_string(img, config=config)
        
        try:
            return txt
        except ValueError as e:
            msg = "Error while parsing text:" + str(e)
            ErrorHandler(self.screenshot_folder).report_error(msg, ("img", img))
            raise
    
    @utils.add_error_info
    def get_image_from_zone(self, zone=None):
        """Returns the image from zone. Saves image to the screenshot folder as image_from_zone.png.
            Examples:
            | Get Number With Text From Zone | zone=[x  y  w  h]

        """
        
        if zone is None:
            raise Exception('Search zone should be passed as argument.')
        else:
            scr = ImageProcessor(self.error_handler, self.screenshot_folder)._screenshot(zone)
            try:
                if not os.path.exists(self.screenshot_folder):
                    os.makedirs(self.screenshot_folder)
                result = os.path.join(self.screenshot_folder, 'image_from_zone.png')
                scr.save(result)
                return result
            except:
                LOGGER.warn('Could not get screenshot folder dir')
    
    @utils.add_error_info
    def get_template_position(self, template, threshold=0.99):
        """Returns template's coordinates after search. You can also specify the threshold value.
            Examples:
            | Get Template Position | template=img.png | threshold=${None}
        """
        
        threshold = float(threshold)
        screen = ImageProcessor(self.error_handler, self.screenshot_folder)._screenshot()
        return MatchObjects().match_and_return_coordinates(template, screen, threshold)
    
    @utils.add_error_info
    def save_zone_content_to_output(self, zone):
        '''FOR DEBUG: saves the content (screenshot) of the provided zone. Pass zone. Image is saved in the output folder in
                      current dir.
        '''
        
        screen_img = ImageProcessor(self.error_handler, self.screenshot_folder)._screenshot(zone)
        ErrorHandler(self.screenshot_folder).save_pictures([(screen_img, "zone")])



