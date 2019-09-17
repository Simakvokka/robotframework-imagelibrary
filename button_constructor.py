from __future__ import absolute_import

from ImageLibrary.button import Button, StatedButton
from ImageLibrary.buttons_panel import ButtonsPanel
from ImageLibrary.static_button import StaticButton, StaticButtonList
from ImageLibrary.dynamic_button import DynamicButton, DynamicButtonList
from ImageLibrary.multiple_button import MultipleButton, DynamicMultipleButton
from ImageLibrary.button_coord import ButtonCoord, MultiButtonCoord

STATIC_BUTTON_LABEL = "buttons"
DYNAMIC_BUTTON_LABEL = "dynamic_buttons"
BUTTONS_PANELS_LABEL = "buttons_panels"
MULTIPLE_BUTTONS_LABEL = "multiple_buttons"
DYNAMIC_MULTIPLE_BUTTONS_LABEL = "dynamic_multiple_buttons"
BUTTON_COORD_LABEL = "button_coord"
MULTI_BUTTON_COORD_LABEL = "multi_button_coord"

BUTTON_TYPES = [
    STATIC_BUTTON_LABEL, DYNAMIC_BUTTON_LABEL, BUTTONS_PANELS_LABEL, MULTIPLE_BUTTONS_LABEL, DYNAMIC_MULTIPLE_BUTTONS_LABEL, BUTTON_COORD_LABEL, MULTI_BUTTON_COORD_LABEL
]


class ButtonConstructor(object):
    def __init__(self):
        pass

    def create_buttons(self, type, config):
        buttons = {}
        if type == BUTTONS_PANELS_LABEL:
            for button_name, button_config in config.iteritems():
                buttons[button_name] = ButtonsPanel(button_name, button_config)

        elif type == STATIC_BUTTON_LABEL:
            for button_name, button_config in config.iteritems():
                if isinstance(button_config, list):
                    buttons[button_name] = StaticButtonList(button_name, button_config)
                else:
                    buttons[button_name] = StaticButton(button_name, button_config)

        elif type == DYNAMIC_BUTTON_LABEL:
            for button_name, button_config in config.iteritems():
                if isinstance(button_config, list):
                    buttons[button_name] = DynamicButtonList(button_name, button_config)
                else:
                    buttons[button_name] = DynamicButton(button_name, button_config)

        elif type == MULTIPLE_BUTTONS_LABEL:
            for button_name, button_config in config.iteritems():
                buttons[button_name] = MultipleButton(button_name, button_config)

        elif type == DYNAMIC_MULTIPLE_BUTTONS_LABEL:
            for button_name, button_config in config.iteritems():
                buttons[button_name] = DynamicMultipleButton(button_name, button_config)
                
        elif type == BUTTON_COORD_LABEL:
            for button_name, button_config in config.iteritems():
                buttons[button_name] = ButtonCoord(button_name, button_config)
                
        elif type == MULTI_BUTTON_COORD_LABEL:
            for button_name, button_config in config.iteritems():
                buttons[button_name] = MultiButtonCoord(button_name, button_config)

        else:
            raise AssertionError("Unknown button type or not implemented yet: {}".format(type))
        return buttons
