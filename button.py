# -*- coding: utf-8 -*-

from __future__ import absolute_import
import pyautogui
from ImageLibrary.error_handler import ErrorHandler
from ImageLibrary.image_processor import ImageProcessor, DEFAULT_THRESHOLD
from ImageLibrary import utils
from ImageLibrary import GUIProcess

STATE_NORMAL = "normal"
STATE_HIGHLIGHTED = "highlighted"
STATE_DISABLED = "disabled"
POSSIBLE_STATES = [STATE_NORMAL, STATE_HIGHLIGHTED, STATE_DISABLED]
STATES_ACTIVE = [STATE_NORMAL, STATE_HIGHLIGHTED]
IMAGE_LABEL = "image"
THRESHOLD_LABEL = "threshold"
STATES_LABEL = "states"

def get_state_info(config, default_threshold):
    # config can contain simple filename
    # or filename and threshold
    # threshold there is prior to default
    if isinstance(config, basestring):
        return (ImageProcessor().load_image(config), default_threshold)
    elif isinstance(config, dict):
        filename = config[IMAGE_LABEL]
        threshold = config[THRESHOLD_LABEL] if THRESHOLD_LABEL in config else default_threshold
        return (ImageProcessor().load_image(filename), threshold)
    else:
        raise AssertionError("Lists are not supported in state block")

def get_button_info(config):
    '''Return list of states info'''
    states = {}
    # config can contain simple filename
    if isinstance(config, basestring):
        states[STATE_NORMAL] = (ImageProcessor().load_image(config), DEFAULT_THRESHOLD)

    elif isinstance(config, dict):
        # or filename and threshold
        # or list of states
        # or threshold and list of states
        default_threshold = config[THRESHOLD_LABEL] if THRESHOLD_LABEL in config else DEFAULT_THRESHOLD
    
        if IMAGE_LABEL in config:
            states[STATE_NORMAL] = (ImageProcessor().load_image(config[IMAGE_LABEL]), default_threshold)
        elif STATES_LABEL in config:
            states_config = config[STATES_LABEL]
            for state_label in POSSIBLE_STATES:
                if state_label in states_config:
                    states[state_label] = get_state_info(states_config[state_label], default_threshold)
                    
        else:
            raise AssertionError("image or states must be defined")
    else:
        raise AssertionError("Lists are not supported in button block")

    return states

def find_on_screen(states, screen=None):
    image_processor = ImageProcessor()
    screen = screen if screen is not None else image_processor.get_screenshot()
    images_to_find = list(states.itervalues())
    coords = image_processor.find_one_of(images_to_find, screen=screen)
    if coords is not None:
        return coords.get_pos()
    #try again
    ErrorHandler().report_warning("First try was unsuccesful")
    utils.sleep(0.020)
    coords = image_processor.find_one_of(images_to_find)
    if coords is not None:
        return coords.get_pos()

    #no one state is found
    images = []
    for state_name, state_info in states.iteritems():
        images.append((state_name, state_info[0]))
    msg = "Button not found on screen in all possible states"
    images.append(("screen", screen))
    ErrorHandler().report_error(msg, *images)
    raise RuntimeError(msg)

class Button(object):
    '''Button is something on screen that can be pressed
        Sometimes button really contains several regions on screen, that can be pressed, so index is needed
    '''
    def __init__(self, name):
        self.name = name
        self.rect = GUIProcess().get_window_area()

    def press_button(self, index=-1, times=1):
        raise AssertionError("Button::press_button called")

    def get_name(self):
        return self.name

    def find_on_screen(self, screen=None):
        '''It will be called on init of window'''
        pass

    def click(self, x, y, times):
        pyautogui.click(self.rect[0] + x, self.rect[1] + y, clicks=int(times), interval=0.1)

    def click_center(self, area, times):
        print(area, times)
        center = (area[0] + area[2]/2, area[1] + area[3]/2)
        self.click(center[0], center[1], times)

    def move_to_center(self, area):
        center = (area[0] + area[2]/2, area[1] + area[3]/2)
        pyautogui.moveTo(self.rect[0] + center[0], self.rect[1] + center[1])

    def drag_to_center(self, area, duration):
        duration = float(duration)
        center = (area[0] + area[2]/2, area[1] + area[3]/2)
        pyautogui.dragTo(self.rect[0] + center[0], self.rect[1] + center[1], duration)

class StatedButton(Button):
    '''Stated Button has several states: disabled, highlighted, normal
       "highlighted" and "normal" are active states
       stated button is something that can be pressed and has states.
       So you can check state, wait for them and whatever else
    '''
    def __init__(self, name, config):
        super(StatedButton, self).__init__(name)
        self.states = self._get_states_info(config)
        

    @utils.add_error_info
    def press_button(self, index=-1, times=1):
        coords = self._get_coordinates()
        #TODO: if debug mode
        if STATE_DISABLED in self.states:
            images_to_find = list(self.states.itervalues())
            found = ImageProcessor().find_one_of(images_to_find)

            if found is not None and self.states[STATE_DISABLED][0] is found.image:
                #ErrorHandler().report_warning(u"You are trying to press disabled button. But you are the boss, ok ¯\_(ツ)_/¯")
                raise ErrorHandler().report_error(u"You are pressing the disabled button. Seriously??")
        print coords, times

        self.click_center(coords, times)

    @utils.add_error_info
    def get_button_state(self, index):
        screen = ImageProcessor().get_screenshot()
        images_to_find = list(self.states.itervalues())
        coords = ImageProcessor().find_one_of(images_to_find, screen=screen)
        if coords is not None:
            for state_name, state_info in self.states:
                if state_info[0] is coords.image:
                    return state_name

        #no one state is found
        images = []
        for state_name, state_info in self.states.iteritems():
            images.append((state_name, state_info[0]))
        images.append(("screen", screen))
        msg = "Button {} not found on screen in all possible states".format(self.name)
        ErrorHandler().report_error(msg, *images)
        raise RuntimeError(msg)

    @utils.add_error_info
    def button_should_be_on_state(self, index, state):
        assert state in self.states, "State {} is not in list of possible states for button".format(state)
        state_info = self.states[state]
        ImageProcessor().image_should_be_on_screen(state_info[0], state_info[1])
 
    @utils.add_error_info
    def is_button_active(self, index):
        if STATE_NORMAL in self.states:
            state_info = self.states[STATE_NORMAL]
            result = ImageProcessor().is_image_on_screen(state_info[0], state_info[1])
            if result:
                return True
        
        if STATE_HIGHLIGHTED in self.states:
            state_info = self.states[STATE_HIGHLIGHTED]
            result = ImageProcessor().is_image_on_screen(state_info[0], state_info[1])
            if result:
                return True

        return False

    @utils.add_error_info
    def wait_for_button_state(self, index, state, timeout):
        assert state in self.states, "State {} is not in list of possible states for button".format(state)
        state_info = self.states[state]
        ImageProcessor().wait_for_image(state_info[0], state_info[1], timeout)

    @utils.add_error_info
    def wait_for_activate(self, index, timeout):
        states_to_wait = []
        for state in STATES_ACTIVE:
            if state in self.states:
                states_to_wait.append((self.states[state][0], self.states[state][1], True))

        assert bool(states_to_wait), "Button has not active states in list of possible states"

        result = ImageProcessor().wait_for_one_of(states_to_wait, timeout)
        if not result.found:
            #no need to add images there, they will be saved in image processor
            msg = "Button was not found on screen or is in unknown state"
            ErrorHandler().report_warning(msg)
            return False

        return True

    @utils.add_error_info
    def wait_for_activate_and_press(self, index, timeout):
        states_to_wait = []
        for state in STATES_ACTIVE:
            if state in self.states:
                states_to_wait.append((self.states[state][0], self.states[state][1], True))

        assert bool(states_to_wait), "Button has not active states in list of possible states"

        result = ImageProcessor().wait_for_one_of(states_to_wait, timeout)
        if not result.found:
            raise RuntimeError("Button was not found on screen or is in unknown state")

        self.click_center(result.get_pos(), 1)

    @utils.add_error_info
    def drag_button_to_position(self, index, position, duration):
        '''
            position: (x, y, h, w). Button will be dragged to center
        '''
        coords = self._get_coordinates()
        self.move_to_center(coords)
        self.drag_to_center(position, duration)
