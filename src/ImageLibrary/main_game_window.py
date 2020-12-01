# -*- coding: utf-8 -*-
import pyautogui

from ImageLibrary.open_cv import OpenCV
from ImageLibrary.game_window import GameWindow
from ImageLibrary import errors

pyautogui.FAILSAFE = False

class MainGameWindow(GameWindow):
    """
    Main game window
    Contains all game window methods and also some reels and symbols processing stuff
    """
    def __init__(self, settings, window_name, button_constructor, debug = False):
        """Make screenshot and find game zones on screen"""
        super(MainGameWindow, self).__init__(settings, window_name, button_constructor, debug)

        self.x = None
        self.y = None
        if "game_matrix" in self.config:
            try:
                self.x = int(self.config["game_matrix"]["x"])
                self.y = int(self.config["game_matrix"]["y"])
                #init
                #ReelsProcessor(self.x, self.y)
            except KeyError:
                raise errors.ConfigError('In game_matrix "x" and "y" must be defined')
            except ValueError as e:
                raise errors.ConfigError('Cannot convert x or y to int in game_matrix ' + str(e))

        self.cv = OpenCV()