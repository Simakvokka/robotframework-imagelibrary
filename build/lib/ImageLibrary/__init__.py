# -*- coding: utf-8 -*-
from __future__ import absolute_import

from ImageLibrary.GUIProcess import GUIProcess
from ImageLibrary.animations import Animations
from ImageLibrary.image_processor import ImageProcessor
from ImageLibrary.error_handler import ErrorHandler
from ImageLibrary.template import Template, ComplexTemplate
from ImageLibrary.zone import Zone

__version__ = '0.1.0'
ROBOT_LIBRARY_SCOPE = 'GLOBAL'


class ImageLibrary(Template, ComplexTemplate, GUIProcess, Zone, Animations, ImageProcessor):
    def __init__(self, screenshot_folder=None):
        self.screenshot_folder = screenshot_folder
        
        self.error_handler = ErrorHandler(self.screenshot_folder)
        
        Template.__init__(self, self.error_handler, self.screenshot_folder)
        ComplexTemplate.__init__(self, self.error_handler, self.screenshot_folder)
        GUIProcess.__init__(self)
        Zone.__init__(self, self.screenshot_folder, self.error_handler)
        ImageProcessor.__init__(self, self.error_handler, self.screenshot_folder)
        Animations.__init__(self, self.error_handler, self.screenshot_folder)
    
    def save_state(self):
        self.error_handler.save_state()
    
    def clear_screenshots_history(self):
        self.error_handler.clear_history()
    
    def dump_screenshots_to_output(self):
        self.error_handler.dump_screenshots()
