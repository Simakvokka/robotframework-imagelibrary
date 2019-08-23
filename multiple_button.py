from __future__ import absolute_import

from ImageLibrary.button import Button
from ImageLibrary.image_processor import ImageProcessor, get_image_from_config
from ImageLibrary.error_handler import ErrorHandler
from ImageLibrary import utils
from ImageLibrary import errors

#static
class MultipleButton(Button):
    ''' Static set of buttons. One image for many buttons on screen. They will be reached by index.
        Order of buttons can be set by direction (horizontal or vertical).
        If direction is horizontal, button[0] is the most left button, and if vertical... you get the idea.

        yaml:
        multiple_buttons:
            plus:
                image: plus.png    #or all the stuff with states
                threshold: 0.42
                direction: horizontal
                expected_count: 2   #optional
    '''
    @utils.add_error_info
    def __init__(self, name, config):
        super(MultipleButton, self).__init__(name)
        self.image_info = get_image_from_config(config)
        self.buttons = None
        if "direction" not in config or config["direction"] == "horizontal":
            self.direction = 0
        elif config["direction"] == "vertical":
            self.direction = 1
        else:
            raise errors.ConfigError("Unknown direction, only horizontal and vertical are supported, {} recieved".format(config["direction"]))

        self.expected = config["expected_count"] if "expected_count" in config else None

    @utils.add_error_info
    def find_on_screen(self, screen = None):
        found = ImageProcessor().find_multiple_images(self.image_info[0], self.image_info[1], screen=screen)
        if self.expected is not None:
            if self.expected != len(found):
                images = [("button", self.image_info[0])]
                if len(found) > 0:
                    images.append(("screen", found[0].screen))
                elif screen is not None:
                    images.append(("screen", screen))

                msg = "Found {} buttons, but only {} expected".format(len(found), self.expected)
                ErrorHandler().report_error(msg, *images)
                raise RuntimeError(msg)

        ErrorHandler().report_info("Found {} buttons {} on screen".format(len(found), self.name))
        #sort in horizontal or vertical direction
        sorted_found = sorted(found, key=lambda res: res.x if self.direction == 0 else res.y)
        #save pos for every button
        self.buttons = [entry.get_pos() for entry in sorted_found]

    @utils.add_error_info
    def press_button(self, index, times):
        if self.buttons is None:
            self.find_on_screen()
        index = int(index)
        assert 0 < index <= len(self.buttons), "Index is out of borders"
        self.click_center(self.buttons[index-1], times)

    @utils.add_error_info
    def get_buttons_count(self, index):
        if self.buttons is None:
            self.find_on_screen()
        return len(self.buttons)

class DynamicMultipleButton(Button):
    ''' You have set of buttons, that appears on screen on random places on screen with unknown count and have one image for all of them? Oh boy, you came to right place '''
    def __init__(self, name, config):
        super(DynamicMultipleButton, self).__init__(name)
        self.image_info = get_image_from_config(config)
        self.buttons = None
        if "direction" not in config or config["direction"] == "horizontal":
            self.direction = 0
        elif config["direction"] == "vertical":
            self.direction = 1
        else:
            raise errors.ConfigError("Unknown direction, only horizontal and vertical are supported, {} recieved".format(config["direction"]))

    @utils.add_error_info
    def _get_buttons(self):
        found = ImageProcessor().find_multiple_images(self.image_info[0], self.image_info[1])

        ErrorHandler().report_info("Found {} buttons {} on screen".format(len(found), self.name))
        #sort in horizontal or vertical direction
        sorted_found = sorted(found, key=lambda res: res.x if self.direction == 0 else res.y)
        #save pos for every button
        return [entry.get_pos() for entry in sorted_found]

    @utils.add_error_info
    def find_on_screen(self, screen = None):
        pass

    @utils.add_error_info
    def press_button(self, index, times):
        buttons = self._get_buttons()
        index = int(index)
        assert 0 < index <= len(buttons), "Index is out of borders"
        self.click_center(buttons[index-1], times)

    @utils.add_error_info
    def get_buttons_count(self, index):
        return len(self._get_buttons())
