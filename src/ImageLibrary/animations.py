import datetime
from ImageLibrary.error_handler import ErrorHandler
from ImageLibrary.image_processor import ImageProcessor
from ImageLibrary import utils

class Animations:
    def __init__(self):
        pass

    def wait_for_animation_stops(self, zone=None, timeout=15, threshold=0.99, step=0.5):
        #convert passed args to float values
        timeout = float(timeout)
        threshold = float(threshold)
        step = float(step)

        #gets the first screenshot from given zone (if zone is none, takes the whole active window)
        new_screen = ImageProcessor()._get_screen(False, zone)
        #saves the time starting point (when the first screenshot was taken)
        start_time = datetime.datetime.now()

        #In a loop compares the screenshot with previously taken from screen.
        #If images are identical returns True, else continue until timeout occurs - throws error and returns False.
        while True:
            utils.sleep(step)
            old_screen = new_screen
            new_screen = ImageProcessor()._get_screen(False, zone)

            result = ImageProcessor().find_image_result(new_screen, old_screen, threshold)
            if result.found:
                return True
            if (datetime.datetime.now() - start_time).seconds > timeout:
                break

        ErrorHandler().report_warning("Timeout exceeded while waiting for animation stops")
        return False

    def wait_for_animation_starts(self, zone=None, timeout=15, threshold=0.99, step=0.5):
        #convert passed args to float values
        timeout = float(timeout)
        threshold = float(threshold)
        step = float(step)
        # gets the first screenshot from given zone (if zone is none, takes the whole active window)
        new_screen = ImageProcessor()._get_screen(False, zone)
        # saves the time starting point (when the first screenshot was taken)
        start_time = datetime.datetime.now()

        #In a loop compares the screenshot with previously taken from screen.
        #If images are NOT identical returns True, else continue until timeout occurs - throws error and returns False.
        while True:
            utils.sleep(step)
            old_screen = new_screen
            new_screen = ImageProcessor()._get_screen(False, zone)

            result = ImageProcessor().find_image_result(new_screen, old_screen, threshold)
            if not result.found:
                return True
            if (datetime.datetime.now() - start_time).seconds > timeout:
                break

        ErrorHandler().report_warning("Timeout exceeded while waiting for animation starts")
        return False

    def is_animating(self, zone=None, threshold=0.99, step=0.5):
        # convert passed args to float values
        threshold = float(threshold)
        step = float(step)

        #gets the first screenshot than waits for 'step' time and gets the second screenshot
        old_screen = ImageProcessor()._get_screen(False, zone)
        utils.sleep(step)
        new_screen = ImageProcessor()._get_screen(False, zone)

        #compares the first and the second screenshots, returns result. If screenshots are identical - True.
        return not ImageProcessor().find_image_result(new_screen, old_screen, threshold).found