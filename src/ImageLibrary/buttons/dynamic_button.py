from .button import Button, StatedButton, get_button_info, STATE_DISABLED
from ImageLibrary.error_handler import ErrorHandler
from ImageLibrary.image_processor import ImageProcessor
from ImageLibrary import utils

class DynamicButton(StatedButton):
    """Dynamic button can be on screen. And can not be on screen. And can move on screen.
        So before pressing it - ImageLibrary will try to find it's image on screen and press actual coordinates.
        Button will be pressed even in disabled state, but warning will be written to log.
  
        dynamic_buttons: 
           double: double.png
           whatever:
               states:
                   ...
    """
    def __init__(self, name, config):
        super(DynamicButton, self).__init__(name, config)

    @utils.add_error_info
    def _get_states_info(self, config):
        return get_button_info(config)

    def _is_on_screen(self):
        """any state"""
        screen = ImageProcessor().get_screenshot()
        images_to_find = self.states.values()
        coords = ImageProcessor().find_one_of(images_to_find, screen=screen)
        return coords is not None

    @utils.add_error_info
    def _get_coordinates(self):
        screen = ImageProcessor().get_screenshot()
        images_to_find = self.states.values()
        coords = ImageProcessor().find_one_of(images_to_find, screen=screen)
        if coords is not None:
            if STATE_DISABLED in self.states and self.states[STATE_DISABLED][0] is coords.image:
                image_info = ("disabled", coords.image)
                screen_info = ("screen", coords.screen)
                ErrorHandler().report_warning("Trying to press disabled button!", image_info, screen_info)
            return coords.get_pos()

        #no one state is found
        images = []
        images.append(("screen", screen))
        for state_name, state_info in sorted(self.states.items()):
            images.append((state_name, state_info[0]))

        msg = "Button not found on screen in all possible states"
        ErrorHandler().report_error(msg, *images)
        raise RuntimeError(msg)

    #exclusive dynamic button method
    @utils.add_error_info
    def is_dynamic_button_on_screen(self, index):
        return self._is_on_screen()

    @utils.add_error_info
    def wait_for_dynamic_button(self, index, timeout, threshold):
        """Any state"""
        images_to_find = []
        for state in sorted(self.states.values()):
            images_to_find.append((state[0], state[1], True))

        return ImageProcessor().wait_for_one_of(images_to_find, timeout)

    @utils.add_error_info
    def wait_for_dynamic_button_to_stop(self, index, state, timeout, move_threshold, step):
        """Show on screen and stops. Any state"""
        #TODO
        raise AssertionError("Not implemented yet")

class DynamicButtonList(Button):
    """just a list of buttons, reached by index:
            lines: [l1.png, l2.png, l3.png, l4.png, l5.png]
    """
    def __init__(self, name, config):
        super(DynamicButtonList, self).__init__(name)
        assert isinstance(config, list), "config for list of static buttons is not a list o_O"
        self.buttons = []
        for button in config:
            self.buttons.append(DynamicButton(name, button))

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
        return self._get_button_by_index(index).press_button(None, state)

    @utils.add_error_info
    def get_button_state(self, index):
        return self._get_button_by_index(index).get_button_state(None)

    @utils.add_error_info
    def wait_for_button_state(self, index, state, timeout, step=0.5):
        return self._get_button_by_index(index).wait_for_button_state(None, state, timeout, step)

    @utils.add_error_info
    def wait_for_activate_and_press(self, index, timeout, step=0.5):
        return self._get_button_by_index(index).wait_for_activate_and_press(None, timeout, step)

    #exclusive dynamic button method
    @utils.add_error_info
    def is_dynamic_button_on_screen(self, index=-1):
        return self._get_button_by_index(index).is_dynamic_button_on_screen(None)

    @utils.add_error_info
    def wait_for_dynamic_button(self, index, timeout, threshold):
        """Any state"""
        return self._get_button_by_index(index).wait_for_dynamic_button(None, timeout, threshold)

    @utils.add_error_info
    def wait_for_dynamic_button_to_stop(self, index, timeout, move_threshold, step):
        """Show on screen and stops. Any state"""
        return self._get_button_by_index(index).wait_for_dynamic_button_to_stop(None, timeout, move_threshold, step)

    @utils.add_error_info
    def drag_button_to_position(self, index, position, duration):
        return self._get_button_by_index(index).drag_button_to_position(None, position, duration)
