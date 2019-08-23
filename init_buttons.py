#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from ImageLibrary import utils
from ImageLibrary.button_constructor import BUTTON_TYPES


class InitButtons(object):
    ####    INIT  BUTTONS   ####
    @utils.add_error_info
    def __init__(self, config, button_constructor):
        self.button_constructor = button_constructor
        self.config = config

        self.buttons = {}

        #create all window elements
        for entry_type, entry_config in config.iteritems():
            if entry_type in BUTTON_TYPES:
                self.buttons.update(self.button_constructor.create_buttons(entry_type, entry_config))