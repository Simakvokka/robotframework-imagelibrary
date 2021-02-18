import pyautogui

from ImageLibrary.open_cv import OpenCV
from ImageLibrary.window import Window

pyautogui.FAILSAFE = False

class MainWindow(Window):
    """
    Main window
    Contains all window methods.
    """
    def __init__(self, settings, window_name, button_constructor, debug = False):
        """Make screenshot and find zones on screen"""
        super(MainWindow, self).__init__(settings, window_name, button_constructor, debug)

        self.x = None
        self.y = None
        self.cv = OpenCV()