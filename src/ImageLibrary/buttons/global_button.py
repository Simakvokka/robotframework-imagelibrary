from ImageLibrary.error_handler import ErrorHandler
from .button import Button, StatedButton, get_button_info, find_on_screen
from ImageLibrary.singleton import Singleton
from ImageLibrary import utils
from robot.api import logger as LOGGER

#global button def is not a button, it is a declaration of button, so it's not derived from Button
class GlobalButtonDef:
    """Declaration of global button. See GlobalButton for more info"""
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.states = None

    def get_states_info(self, states):
        if self.states is None:
            self.states = get_button_info(self.config)

        result = {}
        not_supported = []
        for state in states:
            if state == "all":
                if "normal" in self.states:
                    result["normal"] = self.states["normal"]
                if "highlighted" in self.states:
                    result["highlighted"] = self.states["highlighted"]
                if "disabled" in self.states:
                    result["disabled"] = self.states["disabled"]
            elif state == "active":
                if "normal" not in self.states and "highlighted" not in self.states:
                    not_supported.append("active")
                    continue

                if "normal" in self.states:
                    result["normal"] = self.states["normal"]
                if "highlighted" in self.states:
                    result["highlighted"] = self.states["highlighted"]

            else:
                if state not in self.states:
                    not_supported.append(state)
                    continue
                result[state] = self.states[state]

        return result, not_supported

class GlobalButtonRegistry(metaclass=Singleton):

    def __init__(self, hack):
        #hack is used to recreate singleton. Oh, fine, recreating singleton is bad, I know it
        self.buttons = {}
        self.merge_errors = []

    def _parse_config(self, config):
        assert isinstance(config, dict), "Button definitions must contain dict of buttons"
        buttons = {}
        for button_name, button_config in sorted(config.items()):
            buttons[button_name] = GlobalButtonDef(button_name, button_config)

        return buttons

    def update_info(self, config):
        buttons = self._parse_config(config)
        for button in buttons.keys():
            if button not in self.buttons:
                self.buttons[button] = buttons[button]
            else:
                self.merge_errors.append("Button {} was already defined in other config".format(button))

    def report_merge_errors(self):
        if self.merge_errors:
            ErrorHandler().report_error("Errors occurred while parsing configs:\n" + "\n".join(self.merge_errors))
            raise AssertionError("Config is malformed")

    def get_button_info(self, name):
        assert name in self.buttons, "Global button {} was not found".format(name)
        return self.buttons[name]

    def __getitem__(self, name):
        return self.get_button_info(name)

#object of this class is created for every window
class GlobalStaticButton(StatedButton):
    """ Global button takes two definitions:
        First - before all windows place a "global_buttons_defs" block with all buttons data (states, threshold, images)
        Second - in each window, where you want to use this button, place a block of global_buttons with listed states.

        yaml:
        global_buttons_defs:
            help: help.png
            l1: ... #with enabled and disabled state
            l2: ... #with enabled and disabled state
            l3: ... #with enabled and disabled state
            l4: ... #with enabled and disabled state
            l5: ... #with enabled and disabled state
            start:
                states:
                    disabled:
                        image: start_d.png
                        threshold: 0.99
                    normal:
                        image: start_n.png
                        threshold: 0.88
            gamble:
                states:
                    normal:
                        image: gamble_n.png
                    highlighted:
                        image: gamble_h.png

        win:
            global_buttons:
                start: normal       #start must be only in 'normal' state
                gamble: active      #gamble can be in active states - normal and highlighted
                whatever: all       #will be in all states, defined at defs

        bonus:
            lines:  #in this bonus l2 and l4 must be on normal and disabled states, and l1, l3, l5 always disabled
                - l1: disabled
                - l2: [ normal, disabled ]
                - l3: disabled
                - l4: [ normal, disabled ]
                - l5: disabled

            back_to_game:
                start: normal
    """

    @utils.add_error_info
    def __init__(self, name, config):
        super(GlobalStaticButton, self).__init__(name, config)
        self.coords = None

    @utils.add_error_info
    def _get_states_info(self, config):
        self.possible_states = []

        def get_possible_states(node):
            result = []
            if isinstance(node, (str, bytes)):
                result.append(node)
            elif isinstance(node, list):
                result.extend(node)
            else:
                raise AssertionError("Malformed possible states part")

            return result


        if isinstance(config, dict):
            assert len(config.keys()) == 1, LOGGER.error("Config malformed for button {}".format(self.name))
            self.global_name = list(config.keys())[0]
            possible_states = get_possible_states(list(config.values())[0])
            #todo:check
            #assert "name" in config, "Button name must be set"
            #self.global_name = config["name"]
            #
            #if "states" in config:
            #    possible_states = get_possible_states(config["states"])
            #else:
            #    possible_states = ["all"]
        else:
            self.global_name = self.name
            possible_states = get_possible_states(config)

        states, not_supported = GlobalButtonRegistry().get_button_info(self.global_name).get_states_info(possible_states)

        if not_supported:
            raise RuntimeError("States {} are not defined in global button declarations".format(", ".join(not_supported)))

        return states

    @utils.add_error_info
    def find_on_screen(self, screen=None):
        #one of state images should be on screen. Find it and save coordinates
        self.coords = find_on_screen(self.states, screen)
        if self.coords is not None:
            return

    @utils.add_error_info
    def _get_coordinates(self):
        if self.coords is None:
            self.find_on_screen()
        return self.coords

class GlobalStaticButtonList(Button):
    """just a list of buttons, reached by index:
            lines: [l1.png, l2.png, l3.png, l4.png, l5.png]
    """
    def __init__(self, name, config):
        super(GlobalStaticButtonList, self).__init__(name)
        assert isinstance(config, list), "config for list of static buttons is not a list 0_O"
        self.buttons = []
        for button in config:
            self.buttons.append(GlobalStaticButton(name, button))

    def find_on_screen(self, screen=None):
        for button in self.buttons:
            try:
                button.find_on_screen(screen)
            except RuntimeError:
                LOGGER.info(f"One of the global button states was not found found on screen")

    def _get_button_by_index(self, index):
        index = int(index)
        assert index != -1, "Button must be reached by index"
        # to start from 1 index. Old in case not to mix with programming languages logic where indexing starts from 0
        #assert index > 0, "Index must be more, than zero"
        assert index <= len(self.buttons), "Index is beyond the borders"
        return self.buttons[index-1]

    @utils.add_error_info
    def press_button(self, index, times):
        return self._get_button_by_index(index).press_button(None, times)

    @utils.add_error_info
    def button_should_be_on_state(self, index, state):
        return self._get_button_by_index(index).button_should_be_on_state(None, state)

    @utils.add_error_info
    def get_button_state(self, index):
        return self._get_button_by_index(index).get_button_state(None)

    @utils.add_error_info
    def wait_for_button_state(self, index, state, timeout):
        return self._get_button_by_index(index).wait_for_button_state(None, state, timeout)

    @utils.add_error_info
    def wait_for_activate_and_press(self, index, timeout):
        return self._get_button_by_index(index).wait_for_activate_and_press(None, timeout)

    @utils.add_error_info
    def wait_for_activate(self, index, timeout):
        return self._get_button_by_index(index).wait_for_activate(None, timeout)


class GlobalDynamicButton(StatedButton):
    #todo
    pass

