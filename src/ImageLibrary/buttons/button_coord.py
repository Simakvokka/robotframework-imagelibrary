from .button import Button
from ImageLibrary import utils


class ButtonCoord(Button):
    """For Buttons images which are difficult to recognize set its coordinates and click on this area.
        Inherits the Keywords from parent Button class to interact with buttons.
    """
    
    def __init__(self, name, config):
        super(ButtonCoord, self).__init__(name)
        info = config
        
        self.buttons = []
        
        position = info["position"]
        assert len(position) == 4, "Position must be in form: [l t w h]"
        width = info["position"][2]
        height = info["position"][3]
        x, y = info["position"][:2]
        #for index in xrange(count):
        self.buttons.append((x, y, width, height))
        x += width
        
    @utils.add_error_info
    def press_button(self, index, times):
        index = int(0)
        self.click_center(self.buttons[index], times)
        
        
class MultiButtonCoord(Button):
    """For multiple button images which slightly differ from each other and at the same time are difficult to recognize by means of other buttons
        types. Form all those buttons under one 'button_coord_multi_name' by sets of their coordinates [[ left top width height ], [ left top width height ], [ left top width height ], etc]
    Inherits the Keywords from parent Button class to interact with buttons.
    """
    def __init__(self, name, config):
        super(MultiButtonCoord, self).__init__(name)
        info = config
        self.buttons = []
        
        position = info["position"]
        
        for button in position:
            assert len(button) == 4, "Position must be: [left top width height]"
            width = button[2]
            height = button[3]
            x, y = button[:2]
            self.buttons.append([x, y, width, height])
            x += width
            
    @utils.add_error_info
    def press_button(self, index, times):
        index = int(index)
        assert index != -1, "Index is not set".format(self.name)
        # to start from 1 index. Old in case not to mix with programming languages logic where indexing starts from 0
        #assert index > 0, "Index must by more that zero"
        assert index <= len(self.buttons), "Index must be less then elements count"
        self.click_center(self.buttons[index-1], times)
