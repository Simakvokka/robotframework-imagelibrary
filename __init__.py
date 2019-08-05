#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os.path

from .image_processor import ImageProcessor
from .zone import Zone
from .compare_img import ImageComparison
from ImageLibrary import error_handler
from GUIProcess import GUIProcess

__version__ = '0.1.0'
ROBOT_LIBRARY_SCOPE = 'GLOBAL'


#

class ImageLibrary(ImageProcessor, ImageComparison, GUIProcess):
    """TODO: doc
    """

    ####    INIT    ####
    def __init__(self, screenshot_folder=None):
        super(ImageProcessor, self).__init__()
        super(GUIProcess, self).__init__()
        self.screenshot_folder = screenshot_folder
        #main game window
        #self.mgw = None

        self.rect = GUIProcess().get_window_area()

    # def init(self, settings_file, reference_folders, area, log_type=None,
    #          keyword_on_failure='SlotBot.Take A Screenshot'):
    #     '''Init slotbot'''
    #     self.debug = utils.to_bool(BuiltIn().get_variable_value("${DEBUG_MODE}", False))
    #
    #     self.settings = {}
    #     self.button_registry = GlobalButtonRegistry('hack')
    #
    #     if hasattr(settings_file, '__iter__'):
    #         for setting in settings_file:
    #             #old and deprecated: #config = yaml.load(file(setting, "r"))
    #             config = yaml.load(file(setting, "r"), Loader=yaml.FullLoader)
    #             if "global_buttons_defs" in config:
    #                 self.button_registry.update_info(config["global_buttons_defs"])
    #                 del config["global_buttons_defs"]
    #
    #             self.settings.update(config)
    #     else:
    #         #old and deprecated: #config = yaml.load(file(settings_file, "r"))
    #         config = yaml.load(file(settings_file, "r"), Loader=yaml.FullLoader)
    #         if "global_buttons_defs" in config:
    #             self.button_registry.update_info(config["global_buttons_defs"])
    #             del config["global_buttons_defs"]
    #         self.settings.update(config)
    #
    #     self.reference_folders = reference_folders
    #     _check_config(self.settings, self.reference_folders)
    #
    #     self.area = area
    #
    #     if "main" not in self.settings:
    #         raise errors.ConfigError('config must contain "main" section')
    #
    #     self.game_id = self.settings["game_id"] if "game_id" in self.settings else None
    #     self.game_name = self.settings["game_name"] if "game_name" in self.settings else None
    #
    #     self.error_handler = ErrorHandler(self.game_id, self.game_name, self.screenshot_folder, self.area, self.debug)
    #     self.image_processor = ImageProcessor(area, OpenCV(), reference_folders, self.error_handler)
    #     self.button_registry.report_merge_errors()
    #
    #     self.button_constructor = ButtonConstructor()
    #
    #     #init all windows
    #     self.windows = {}
    #     for name, config in self.settings.iteritems():
    #         if name == "main" and log_type is None:
    #             llp = BuiltIn().run_keyword("Get Launcher Log Parser")
    #             self.mgw = MainGameWindow(config, "main", self.button_constructor, self.debug, llp)
    #
    #         if name == "main" and log_type == "browser":
    #             #llp = BuiltIn().run_keyword("Get Browser Log Parser")
    #             llp = None
    #             self.mgw = MainGameWindow(config, "main", self.button_constructor, self.debug, llp)
    #
    #         elif isinstance(config, dict):
    #             self.windows[name] = GameWindow(config, name, self.button_constructor, self.debug)
    #
    #         #window has multiple screens
    #         elif isinstance(config, list):
    #             self.windows[name] = []
    #             for index, screen in enumerate(config):
    #                 if not isinstance(screen, dict):
    #                     raise errors.ConfigError("screen {} of window {} not properly configured: dict expected".format(index + 1, name))
    #
    #                 self.windows[name].append(GameWindow(screen, name, self.button_constructor, self.debug))

    ####    ERROR HANDLING      ####
    def save_state(self):
        self.error_handler.save_state()

    # def show_build_quality(self):
    #     self.error_handler.show_build_quality()

    def clear_screenshots_history(self):
        self.error_handler.clear_history()

    def dump_screenshots_to_output(self):
        self.error_handler.dump_screenshots()

    # ####    ANIMATIONS      ####
    #
    # def wait_for_animation_stops(self, zone=None, timeout=15, threshold=0.9, step=0.1, window=None, wind_index=-1):
    #     '''S.wait_for_animation_stops(zone, timeout, threshold, window, wind_index) -> bool
    #         Waits while animation in selected zone will be over and return True if success or False if timeout exceeded
    #         zone - name of zone, where to find animation or None for whole window
    #         timeout - time to wait for animation stops
    #         threshold - how different can be animation frames:
    #             1.0 - images are identical
    #             0.98 - images are slightly different
    #             0.9 looks like nice threshold when you need to check animation stops (calibration needed)
    #             ...
    #             0 - all images pixels are different (black and white screen)
    #         step - how often to make screenshots. If animation is fast, probably you should pass 0
    #     '''
    #     pass
    #
    #
    # def wait_for_animation_starts(self, zone=None, timeout=15, threshold=0.9, step=0.1, window=None, wind_index=-1):
    #     '''Old wait_for_changes'''
    #     pass
    #
    #
    # def is_zone_animating(self, zone=None, threshold=0.9, step=0.1, window=None, wind_index=-1):
    #     pass
    #
    # ####    CACHE   ####
    # def take_cache_screenshot(self):
    #     ImageProcessor().take_cache_screenshot()
    #
    # ####    IMAGE RECOGNIZION   ####
    #
    # def get_number_from_zone(self, zone, lang=None, resize_percent=0, resize=0, contrast=0, cache=False, background=None, contour=False, invert=False, window=None, wind_index=-1, brightness=0):
    #     pass
    #
    #
    # def get_float_number_from_zone(self, zone, lang=None, resize_percent=0, resize=0, cache=False, window=None, wind_index=-1, invert=False, brightness=0):
    #     pass
    #
    #
    # def get_number_with_text_from_zone(self, zone, lang=None, resize_percent=0, resize=0, contrast=0, cache=False, background=None, contour=False, invert=False, brightness=0):
    #     pass
    #
    #
    # def get_text_from_zone(self, zone, lang=None, resize_percent=0, contrast=0, cache=False, contour=False, invert=False, brightness=0):
    #     pass
    #
    #
    # def get_image_from_zone(self, zone):
    #     pass
    #
    #
    # def is_template_in_zone(self, template, zone):
    #     pass
    #
    #
    # def match_template_in_zone(self, template, zone):
    #     pass
    #
    #
    # def get_template_position(self, template, zone):
    #     pass
    #
    #
    # ####    OTHER       ####
    #
    # def save_zone_content_to_output(self, zone, window=None, wind_index=-1):
    #     pass

    # def hide_cursor(self):
    #     return ImageProcessor().hide_cursor()

    def compare_images(self, id, image, screen):

        dir = os.path.abspath(os.path.dirname(__file__))
        imdir = os.path.abspath(os.path.join(os.sep, dir, '..\\..\\launcher\\l_screens\\haxe\\haxe_mobile'))
        image = imdir + '\\' + id + '\\' + image
        print(image)
        return ImageComparison().return_comparison_result(image, screen)

