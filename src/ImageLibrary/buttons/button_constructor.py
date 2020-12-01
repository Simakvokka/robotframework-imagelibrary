from .buttons_panel import ButtonsPanel
from .static_button import StaticButton, StaticButtonList
from .dynamic_button import DynamicButton, DynamicButtonList
from .global_button import GlobalButtonDef, GlobalStaticButton, GlobalStaticButtonList, GlobalDynamicButton
from .multiple_button import MultipleButton, DynamicMultipleButton
from .button_coord import ButtonCoord, MultiButtonCoord
import operator

STATIC_BUTTON_LABEL = "buttons"
DYNAMIC_BUTTON_LABEL = "dynamic_buttons"
DYNAMIC_BUTTON_LIST_LABEL = "dynamic_buttons_list"
BUTTONS_PANELS_LABEL = "buttons_panels"
GLOBAL_BUTTON_DEFINATIONS_LABEL = "global_button_defs"
GLOBAL_BUTTONS_LABEL = "global_buttons"
GLOBAL_DYNAMIC_BUTTONS_LABEL = "global_dynamic_buttons"
MULTIPLE_BUTTONS_LABEL = "multiple_buttons"
DYNAMIC_MULTIPLE_BUTTONS_LABEL = "dynamic_multiple_buttons"
BUTTON_COORD_LABEL = "button_coord"
MULTI_BUTTON_COORD_LABEL = "multi_button_coord"

BUTTON_TYPES = [
    STATIC_BUTTON_LABEL, DYNAMIC_BUTTON_LABEL, BUTTONS_PANELS_LABEL, GLOBAL_BUTTONS_LABEL,
    GLOBAL_DYNAMIC_BUTTONS_LABEL, MULTIPLE_BUTTONS_LABEL, DYNAMIC_MULTIPLE_BUTTONS_LABEL, BUTTON_COORD_LABEL, MULTI_BUTTON_COORD_LABEL, DYNAMIC_BUTTON_LIST_LABEL
]

STATES = ['normal', 'disabled', 'highlighted']


class ButtonConstructor:
    """Creates the buttons object: buttons types with their infos (name, states, threshold, coords, etc).
        Buttons are created according to buttons sections in yaml config. Saves the button info and uses it during
        buttons related keywords calls."""
    def __init__(self):
        pass

    #def init_global_buttons(self, config):
    #    self.global_buttons_def = {}
    #    for button_name, button_config in config.iteritems():
    #        self.global_buttons_def[button_name] = GlobalButtonDef(button_name, button_config)

    def create_buttons(self, type, config):
        buttons = {}
        if type == BUTTONS_PANELS_LABEL:
            for button_name, button_config in sorted(config.items()):
                buttons[button_name] = ButtonsPanel(button_name, button_config)

        elif type == STATIC_BUTTON_LABEL:
            for button_name, button_config in sorted(config.items()):
                if isinstance(button_config, list):
                    buttons[button_name] = StaticButtonList(button_name, button_config)
                else:
                    buttons[button_name] = StaticButton(button_name, button_config)

        elif type == DYNAMIC_BUTTON_LABEL:
            for button_name, button_config in sorted(config.items()):
                if isinstance(button_config, list):
                    buttons[button_name] = DynamicButtonList(button_name, button_config)
                else:
                    buttons[button_name] = DynamicButton(button_name, button_config)

        elif type == GLOBAL_BUTTONS_LABEL:
            for button_name, button_config in sorted(config.items(), key=operator.itemgetter(0)):
                if isinstance(button_config, list) and isinstance(button_config[0], dict):
                    buttons[button_name] = GlobalStaticButtonList(button_name, button_config)
                else:
                    buttons[button_name] = GlobalStaticButton(button_name, button_config)

        elif type == GLOBAL_DYNAMIC_BUTTONS_LABEL:
            raise AssertionError("global dynamic buttons are not implemented yet")

        elif type == MULTIPLE_BUTTONS_LABEL:
            for button_name, button_config in sorted(config.items()):
                buttons[button_name] = MultipleButton(button_name, button_config)

        elif type == DYNAMIC_MULTIPLE_BUTTONS_LABEL:
            for button_name, button_config in sorted(config.items()):
                buttons[button_name] = DynamicMultipleButton(button_name, button_config)
                
        elif type == BUTTON_COORD_LABEL:
            for button_name, button_config in sorted(config.items()):
                buttons[button_name] = ButtonCoord(button_name, button_config)
                
        elif type == MULTI_BUTTON_COORD_LABEL:
            for button_name, button_config in sorted(config.items()):
                buttons[button_name] = MultiButtonCoord(button_name, button_config)
        
                # for button_name, button_config in config.iteritems():
            #     if isinstance(button_config, list):
            #         buttons[button_name] = ButtonCoordMulti(button_name, button_config)
            #     else:
            #         buttons[button_name] = ButtonCoordMulti(button_name, button_config)

        else:
            raise AssertionError("Unknown button type or not implemented yet: {}".format(type))

        return buttons
