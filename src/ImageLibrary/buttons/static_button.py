from .button import Button, StatedButton, get_button_info, find_on_screen
from ImageLibrary import utils

class StaticButton(StatedButton):
    """ Simple button. It's coordinates will be saved at check window or pressing one button of window
        Assumes, that it is in one of states, listed in config
        After than it wouldn't use finding button image on screen before use, unless you checking states

        yaml:
        buttons:
            help: help.png
            lines: [l1.png, l2.png, l3.png, l4.png, l5.png]
            is_it_really_needed:
                - states:
                    disabled: whatever_d.png
                    normal:
                        image: whatever.png
                        thershold: 0.42
                - second.png
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
                    normal: gamble_n.png
                    highlighted: gamble_h.png
                threshold: 0.99 #for all states
            whatever:
              image: whaterver.png
              threshold: 0.71
    """
    def __init__(self, name, config):
        super(StaticButton, self).__init__(name, config)
        self.coords = None

    @utils.add_error_info
    def _get_states_info(self, config):
        return get_button_info(config)

    @utils.add_error_info
    def find_on_screen(self, screen=None):
        #one of state images should be on screen. Find it and save coordinates
        if self.coords is not None:
            return

        self.coords = find_on_screen(self.states, screen)

    @utils.add_error_info
    def _get_coordinates(self):
        if self.coords is None:
            self.find_on_screen()
        return self.coords

#todo: python magic: list of button
class StaticButtonList(Button):
    """just a list of buttons, reached by index:
            lines: [l1.png, l2.png, l3.png, l4.png, l5.png]
    """
    def __init__(self, name, config):
        super(StaticButtonList, self).__init__(name)
        assert isinstance(config, list), "config for list of static buttons is not a list o_O"
        self.buttons = []
        for button in config:
            self.buttons.append(StaticButton(name, button))

    def find_on_screen(self, screen=None):
        for button in self.buttons:
            button.find_on_screen(screen)

    def _get_button_by_index(self, index):
        index = int(index)
        assert index != -1, "Button must be reached by index"
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
