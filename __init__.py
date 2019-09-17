#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import yaml
import os
import re

from ImageLibrary.template import Template, ComplexTemplate
from ImageLibrary.error_handler import ErrorHandler
from ImageLibrary.zone import Zone
from ImageLibrary.GUIProcess import GUIProcess
from ImageLibrary.image_processor import ImageProcessor
from ImageLibrary.button_constructor import ButtonConstructor
from ImageLibrary.static_button import StaticButton
from ImageLibrary import errors
from ImageLibrary import utils
from ImageLibrary.button_constructor import BUTTON_TYPES



__version__ = '0.1.0'
ROBOT_LIBRARY_SCOPE = 'GLOBAL'


def _get_images_from(node):
    '''_get_images_from(node) -> set(string)
        Gets all images from this node recursively
        Image is any value ends with ".png"
    '''
    images = set()
    if isinstance(node, basestring):
       if re.search('.*\.png$', node) is not None:
            images.add(node)

    elif isinstance(node, dict):
        for key, value in node.iteritems():
            images.update(_get_images_from(value))

    elif isinstance(node, list):
        for value in node:
            images.update(_get_images_from(value))

    return images

def _check_config(config, reference_folders):
    images = _get_images_from(config)
    not_found_folders = set()
    not_found = images.copy()
    for folder in reference_folders:
        if not os.path.isdir(folder):
            not_found_folders.add(folder)
            continue
        for image in images:
            if image in not_found and os.path.isfile(os.path.join(folder, image)):
                not_found.remove(image)

    out = ""
    if bool(not_found_folders):
        out += "Not found reference folders: " + ", ".join(not_found_folders)

    if bool(not_found):
        out += " and " if bool(not_found_folders) else "Not found "
        out += "images: " + ", ".join(not_found)
        out += " at folders:" + ", ".join(set(reference_folders).difference(not_found_folders))

    if bool(out):
        raise errors.InitError(out)

    return True


class ImageLibrary(Template, ComplexTemplate, GUIProcess, Zone, ImageProcessor, ErrorHandler, ButtonConstructor, StaticButton):
    
    def __init__(self, screenshot_folder=None):

        self.screenshot_folder = screenshot_folder
        self.error_handler = ErrorHandler(self.screenshot_folder)
        self.button_constructor = ButtonConstructor()

        super(ImageLibrary, self).__init__(self, screenshot_folder)

        Template.__init__(self, self.error_handler, self.screenshot_folder)
        ComplexTemplate.__init__(self, self.error_handler)
        GUIProcess.__init__(self)
        Zone.__init__(self, self.screenshot_folder, self.error_handler)
        ImageProcessor.__init__(self, self.error_handler, self.screenshot_folder)



    def init(self, settings_file, reference_folders):
        '''Init slotbot'''

        self.settings = {}

        if hasattr(settings_file, '__iter__'):
            for setting in settings_file:
                # old and deprecated: #config = yaml.load(file(setting, "r"))
                config = yaml.load(file(setting, "r"), Loader=yaml.FullLoader)
                self.settings.update(config)
        else:
            # old and deprecated: #config = yaml.load(file(settings_file, "r"))
            config = yaml.load(file(settings_file, "r"), Loader=yaml.FullLoader)
            self.settings.update(config)

        self.reference_folders = reference_folders
        _check_config(self.settings, self.reference_folders)
        
        self.init_buttons()
        

    ####    INIT  BUTTONS   ####
    @utils.add_error_info
    def init_buttons(self):
        self.config = self.settings
        self.buttons = {}

        # create all window elements
        for entry_type, entry_config in self.config.iteritems():
            if entry_type in BUTTON_TYPES:
                return self.buttons.update(self.button_constructor.create_buttons(entry_type, entry_config))


    # def save_state(self, level="INFO"):
    #     self.error_handler.save_state()

    def clear_screenshots_history(self):
        self.error_handler.clear_history()

    def dump_screenshots_to_output(self):
        self.error_handler.dump_screenshots()