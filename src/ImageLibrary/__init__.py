import os.path
from robot.api import logger as LOGGER
import pyautogui

from ImageLibrary.image_processor import ImageProcessor
from ImageLibrary.keywords import Keywords
from ImageLibrary.libcore.robotlibcore import DynamicCore
from ImageLibrary.libcore.robotlibcore import keyword


__version__ = '1.0.0'

class ImageLibrary(DynamicCore):
    """ImageLibrary library provides methods to work with active windows and screenshots.
        Mostly all the keywords related work with images.

        Add library to RobotFramework tests:
        
        args: screenshot_folder (optional)

        Examples:
		|   Librariy        ImageLibrary    screenshot_folder=${EXECDIR}${/}output
    """

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    ####    INIT    ####
    def __init__(self, screenshot_folder=None):

        self.screenshot_folder = screenshot_folder
        # main window
        self.screenshot_counter = 0

        self.libraries = [Keywords(screenshot_folder, self)]
        DynamicCore.__init__(self, self.libraries)

    @keyword
    def take_screenshot(self):
        if self.screenshot_folder is None:
            self.screenshot_folder = os.path.join(os.getcwd())
        else:
            if not os.path.exists(self.screenshot_folder):
                os.mkdir(self.screenshot_folder)
                
        screenshot_name = "Screenshot-{}.png".format(self.screenshot_counter)
        self.screenshot_counter += 1

        screen_img = pyautogui.screenshot()
        try:
            os.remove(os.path.join(self.screenshot_folder, screenshot_name))
        except OSError:
            pass
        i = screen_img.convert('RGB')
        i.save(os.path.join(self.screenshot_folder, screenshot_name), "JPEG", quality=10)

        LOGGER.info('Screenshot taken: {0}<br/><img src="{0}" />'.format(screenshot_name), html=True)

    @keyword
    def hide_cursor(self):
        return ImageProcessor().hide_cursor()



# import unittest
# todo: tests
