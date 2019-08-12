#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from ImageLibrary.template import Template, ComplexTemplate
from ImageLibrary.error_handler import ErrorHandler
from ImageLibrary.zone import Zone
from GUIProcess import GUIProcess


__version__ = '0.1.0'
ROBOT_LIBRARY_SCOPE = 'GLOBAL'

class ImageLibrary(Template, ComplexTemplate, GUIProcess, Zone):
    """TODO: doc
    """

    def __init__(self, screenshot_folder=None):

        self.screenshot_folder = screenshot_folder

        self.error_handler = ErrorHandler(self.screenshot_folder)

        Template.__init__(self, self.error_handler)
        ComplexTemplate.__init__(self, self.error_handler)
        Zone.__init__(self, self.screenshot_folder)
        GUIProcess.__init__(self)



    ####    ERROR HANDLING      ####
    def save_state(self):
        self.error_handler.save_state()

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

