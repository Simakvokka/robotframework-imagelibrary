# -*- coding: utf-8 -*-

#python
import datetime
import os
#ImageLibrary
from ImageLibrary import errors
from ImageLibrary.buttons.button_constructor import BUTTON_TYPES
from ImageLibrary.template import Template, ComplexTemplate
from ImageLibrary.zone import Zone
from ImageLibrary.values_iterator import Value
from ImageLibrary.image_processor import ImageProcessor, get_image_from_config
from ImageLibrary.error_handler import ErrorHandler
from ImageLibrary.animations import Animations
from ImageLibrary import utils
from ImageLibrary.compare_img import ImageComparison

from ImageLibrary.libcore.librarycomponent import LibraryComponent

from robot.api import logger as LOGGER

class GameWindow(LibraryComponent):
    ####    INIT    ####
    def __init__(self, config, window_name, button_constructor, state, debug=False):
        #super().__init__(state)
        self.name = window_name
        self.debug = debug  #TODO: delete?
        self.button_constructor = button_constructor
        self.config = config

        self.buttons = {}
        self.templates = {}
        self.complex_templates = {}
        self.zones = {}
        self.values = {}

        self.screenshot_counter = 0

        #create all window elements
        #reads the config file and creates window dict variables with its types: buttons, templates, zones, values

        #if self.config != 'None':

        for entry_type, entry_config in sorted(self.config.items()):
            if entry_type in BUTTON_TYPES:
                self.buttons.update(self.button_constructor.create_buttons(entry_type, entry_config))
            elif entry_type == "templates":
                for template_name, template_config in sorted(entry_config.items()):
                    self.templates[template_name] = Template(template_name, template_config)
            elif entry_type == "complex_templates":
                for template_name, template_config in sorted(entry_config.items()):
                    self.complex_templates[template_name] = ComplexTemplate(template_name, template_config)
            elif entry_type == "zones":
                for zone_name, zone_config in sorted(entry_config.items()):
                    self.zones[zone_name] = Zone(zone_name, zone_config)
            elif entry_type == "values":
                for value_name, value_config in sorted(entry_config.items()):
                    self.values[value_name] = Value(value_name, value_config)

    @utils.add_error_info
    def _init_static_elements(self, screen=None):
        """Init position of static elements of window. Assumes that window is on screen or error will be raised
        """
        #init buttons
        for button in self.buttons.values():
            button.find_on_screen(screen)
        screen = ImageProcessor().get_screenshot() if screen is None else screen
        #check window
        if "check" in self.config:
            images_to_check = []
            if isinstance(self.config["check"], list):
                for img_name in self.config["check"]:
                    images_to_check.append(get_image_from_config(img_name))
                if type(images_to_check[0]) == list:
                    for image in images_to_check[0]:
                        res = ImageProcessor().is_image_on_screen(image, screen=screen)
                        if not res:
                            msg = "Image {} was not found at screen".format(image)
                            ErrorHandler().report_error(msg)
                            raise RuntimeError(msg)
                elif type(images_to_check) == list:
                    for image in images_to_check:
                        try:
                            ImageProcessor().image_should_be_on_screen(image[0], image[1], screen=screen)
                        except RuntimeError as e:
                            pass
            else:
                images_to_check.append(get_image_from_config(self.config["check"]))
                for image in images_to_check:
                    ImageProcessor().image_should_be_on_screen(image[0], image[1], screen=screen)

    ####    FULL WINDOW     ####
    @utils.add_error_info
    def window_should_be_on_screen(self):
        """Check window elements - check section, buttons, maybe smth more in future"""
        screen = ImageProcessor().get_screenshot()
        self._init_static_elements(screen)
        if "exist" in self.config:
            if not self._is_window_on_screen(screen)[0]:
                ErrorHandler().report_warning('First try was unsuccessful')
                utils.sleep(0.050)
                if not self._is_window_on_screen()[0]:
                    ErrorHandler().report_error("Window {} is not on screen:".format(self.name), ("screen", screen))
                    raise RuntimeError("Window {} is not on screen (checked by exist section). Image {} not found".format(self.name, self._is_window_on_screen()[1]))
        else:
            raise errors.ConfigError("Is Window On Screen can't work if exists section is not defined; in window " + self.name)

    @utils.add_error_info
    def _is_window_on_screen(self, screen=None):
        def check_if_section(config, screen_img):
            out = []
            res = []
            if isinstance(config, list):
                result = False
                for subnode in config:
                    if isinstance(subnode, list):
                        subresult = True
                        for image_entry in subnode:
                            image = get_image_from_config(image_entry)
                            midresult = ImageProcessor().is_image_on_screen(image[0], image[1], screen=screen_img)
                            subresult &= ImageProcessor().is_image_on_screen(image[0], image[1], screen=screen_img)
                            if midresult is False:
                                out.append(image_entry)
                        result |= subresult
                    else:
                        image = get_image_from_config(subnode)
                        midresult = ImageProcessor().is_image_on_screen(image[0], image[1], screen=screen_img)
                        result |= ImageProcessor().is_image_on_screen(image[0], image[1], screen=screen_img)
                        if midresult is False:
                            out.append(subnode)
            else:
                image = get_image_from_config(config)
                midresult = ImageProcessor().is_image_on_screen(image[0], image[1], screen=screen_img)
                result = ImageProcessor().is_image_on_screen(image[0], image[1], screen=screen_img)
                if midresult is False:
                    out.append(config)

            res.append(result)
            res.append(out)
            return res

        def check_unless_section(config, screen_img):
            unless_lst = []
            assert isinstance(config, (str, bytes)), "Conditions and lists in unless section are temporary not implemented"
            a = not ImageProcessor().is_image_on_screen(config, screen=screen_img)
            unless_lst.append(a)
            return unless_lst

        if "exist" not in self.config:
            raise errors.ConfigError("Is Window On Screen can't work if exists section is not defined; in window " + self.name)
        if not (bool("if" in self.config["exist"]) ^ bool("unless" in self.config["exist"])):
            raise errors.ConfigError('"exist" section is not properly configured, "if" or "unless" needed; in window ' + self.name)

        screen_img = ImageProcessor().get_screenshot() if screen is None else screen

        if "if" in self.config["exist"]:
            return check_if_section(self.config["exist"]["if"], screen_img)
        else:
            return check_unless_section(self.config["exist"]["unless"], screen_img)

    @utils.add_error_info
    def _wait_for_window_state(self, state, timeout):
        #state argument is boolean value.
        #loops for passed timeout trying to locate window on screen
        timeout = float(timeout)
        start_time = datetime.datetime.now()
        state_name = "shows" if state else "hides"
        while True:
            if self._is_window_on_screen()[0] == state:
                ErrorHandler().report_info("Successfully waited for {} {}".format(self.name, state_name))
                return True
            utils.sleep(0)
            if (datetime.datetime.now() - start_time).seconds > timeout:
                ErrorHandler().report_warning("Timeout exceeded while trying to wait {} {}".format(self.name, state_name))
                break

        return False

    @utils.add_error_info
    def wait_for_show(self, timeout=15):
        return self._wait_for_window_state(True, timeout)

    @utils.add_error_info
    def wait_for_hide(self, timeout=15):
        return self._wait_for_window_state(False, timeout)

    @utils.add_error_info
    def wait_for_window_to_stop(self, timeout=15, move_threshold=0.99, step=0.1):
        if not "exist" in self.config or not "if" in self.config["exist"]:
            raise AssertionError('Section "exist":"if" must be defined in config')

        node = self.config["exist"]["if"]
        while isinstance(node, list):
            node = node[0]

        image_info = get_image_from_config(node)

        return ImageProcessor().wait_for_image_to_stop(image_info[0], image_info[1], timeout=timeout, move_threshold=move_threshold, step=step)


    ####    IMAGES      ####

    @utils.add_error_info
    def find_image(self, image, threshold=0.99, cache=False, zone=None):
        #gets zone value
        zone = self.zones[zone].get_area() if zone is not None else None
        #searches for image on screen
        result = ImageProcessor().find_image(image, threshold, cache, zone)
        if result.found:
            return True
        else:
            return False


    @utils.add_error_info
    def is_image_on_screen(self, image, threshold=0.99, cache=False, zone=None):
        # gets zone value
        zone = self.zones[zone].get_area() if zone is not None else None
        # searches for image on screen
        return ImageProcessor().is_image_on_screen(image, threshold, cache, zone)


    @utils.add_error_info
    def wait_for_image(self, image, threshold=0.99, timeout=15, zone=None):
        #gets zone value
        zone = self.zones[zone].get_area() if zone is not None else None
        # tries to find image for timeout
        return ImageProcessor().wait_for_image(image, threshold, timeout, zone)


    @utils.add_error_info
    def wait_for_image_to_stop(self, image, timeout=15, threshold=0.99, move_threshold=0.99, step=0.1):
        return ImageProcessor().wait_for_image_to_stop(image, threshold, timeout, move_threshold, step)


    @utils.add_error_info
    def image_should_be_on_screen(self, image, threshold=0.99, cache=False, zone=None):
        zone = self.zones[zone].get_area() if zone is not None else None
        return ImageProcessor().image_should_be_on_screen(image, threshold, cache, zone)


    @utils.add_error_info
    def image_should_not_be_on_screen(self, image, threshold=0.99, cache=False, zone=None):
        zone = self.zones[zone].get_area() if zone is not None else None
        return ImageProcessor().image_should_not_be_on_screen(image, threshold, cache, zone)


    @utils.add_error_info
    def wait_for_image_to_hide(self, image, threshold=0.99, timeout=15, zone=None):
        zone = self.zones[zone].get_area() if zone is not None else None
        return ImageProcessor().wait_for_image_to_hide(image, threshold, timeout, zone)

    ####    TEMPLATES   ####

    @utils.add_error_info
    def is_template_on_screen(self, template, index=-1, threshold=None, cache=False, zone=None):
        template, index = utils.split_to_name_and_index(template, index)
        if zone is not None:
            zone, zindex = utils.split_to_name_and_index(zone, None)
            zone = self.zones[zone].get_area(zindex) if zone is not None else None
        return self.templates[template].is_template_on_screen(index, threshold, cache, zone)


    @utils.add_error_info
    def wait_for_template(self, template, index=-1, threshold=None, timeout=15, zone=None):
        template, index = utils.split_to_name_and_index(template, index)
        zone = self.zones[zone].get_area() if zone is not None else None
        return self.templates[template].wait_for_template(index, threshold, timeout, zone)


    @utils.add_error_info
    def wait_for_template_to_hide(self, template, index=-1, threshold=None, timeout=15, zone=None):
        template, index = utils.split_to_name_and_index(template, index)
        zone = self.zones[zone].get_area() if zone is not None else None
        return self.templates[template].wait_for_template_to_hide(index, threshold, timeout, zone)


    @utils.add_error_info
    def wait_for_template_to_stop(self, template, index=-1, threshold=None, timeout=15, move_threshold=0.99, step=0.1):
        template, index = utils.split_to_name_and_index(template, index)
        return self.templates[template].wait_for_template_to_stop(index, threshold, timeout, move_threshold, step)


    @utils.add_error_info
    def template_should_be_on_screen(self, template, index=-1, threshold=None, cache=False, zone=None):
        template, index = utils.split_to_name_and_index(template, index)
        zone = self.zones[zone].get_area() if zone is not None else None
        return self.templates[template].template_should_be_on_screen(index, threshold, cache, zone)


    @utils.add_error_info
    def template_should_not_be_on_screen(self, template, index=1, threshold=None, cache=False, zone=None):
        template, index = utils.split_to_name_and_index(template, index)
        zone = self.zones[zone].get_area() if zone is not None else None
        return self.templates[template].template_should_not_be_on_screen(index, threshold, cache, zone)


    @utils.add_error_info
    def get_templates_count(self, template, index=-1, threshold=None, cache=False, zone=None, window=None, wind_index=-1):
        template, index = utils.split_to_name_and_index(template, index)
        zone = self.zones[zone].get_area() if zone is not None else None
        return self.templates[template].get_templates_count(index, threshold, cache, zone)


    @utils.add_error_info
    def is_complex_template_on_screen(self, template, threshold=None, cache=False, zone=None, window=None, wind_index=-1):
        zone = self.zones[zone].get_area() if zone is not None else None
        return self.complex_templates[template].is_complex_template_on_screen(threshold, cache, zone)


    @utils.add_error_info
    def is_any_part_of_complex_template_on_screen(self, template, threshold=None, cache=False, zone=None):
        zone = self.zones[zone].get_area() if zone is not None else None
        return self.complex_templates[template].is_any_part_of_complex_template_on_screen(threshold, cache, zone)

    @utils.add_error_info
    def wait_for_complex_template(self, template, threshold=None, timeout=15, zone=None):
        zone = self.zones[zone].get_area() if zone is not None else None
        return self.complex_templates[template].wait_for_complex_template(threshold, timeout, zone)

    @utils.add_error_info
    def wait_for_complex_template_to_hide(self, template, threshold=None, timeout=15, zone=None):
        zone = self.zones[zone].get_area() if zone is not None else None
        return self.complex_templates[template].wait_for_complex_template_to_hide(threshold, timeout, zone)

    ####    BUTTONS     ####
    @utils.add_error_info
    def press_button(self, button, index=-1, times=1):
        button, index = utils.split_to_name_and_index(button, index)
        return self.buttons[button].press_button(index, times)


    @utils.add_error_info
    def get_button_state(self, button, index=-1):
        button, index = utils.split_to_name_and_index(button, index)
        return self.buttons[button].get_button_state(index)


    @utils.add_error_info
    def button_should_be_on_state(self, button, index=-1, state="normal"):
        button, index = utils.split_to_name_and_index(button, index)
        return self.buttons[button].button_should_be_on_state(index, state)


    @utils.add_error_info
    def wait_for_button_state(self, button, index=-1, state="normal", timeout=15):
        button, index = utils.split_to_name_and_index(button, index)
        return self.buttons[button].wait_for_button_state(index, state, timeout)


    @utils.add_error_info
    def is_button_active(self, button, index=-1):
        button, index = utils.split_to_name_and_index(button, index)
        return self.buttons[button].is_button_active(index)


    @utils.add_error_info
    def wait_for_button_activate(self, button, index=-1, timeout=15):
        button, index = utils.split_to_name_and_index(button, index)
        return self.buttons[button].wait_for_activate(index, timeout)


    @utils.add_error_info
    def wait_for_activate_and_press(self, button, index=-1, times=1, timeout=15):
        button, index = utils.split_to_name_and_index(button, index)
        return self.buttons[button].wait_for_activate_and_press(index, timeout)


    @utils.add_error_info
    def is_dynamic_button_on_screen(self, button, index=-1):
        button, index = utils.split_to_name_and_index(button, index)
        return self.buttons[button].is_dynamic_button_on_screen(index)


    @utils.add_error_info
    def wait_for_dynamic_button(self, button, index=-1, timeout=15, threshold=0.99):
        button, index = utils.split_to_name_and_index(button, index)
        return self.buttons[button].wait_for_dynamic_button(index, timeout, threshold)


    @utils.add_error_info
    def drag_button_to_template(self, button, btn_index=-1, template=None, tmpl_index=-1, threshold=0.7, duration=0.1, cache=False):
        template, tmpl_index = utils.split_to_name_and_index(template, tmpl_index)
        template_pos = self.templates[template].find_template(tmpl_index, threshold, cache)
        if not template_pos.found:
            #todo: save images and stuff
            raise RuntimeError("Template {} not found on screen".format(template))

        button, btn_index = utils.split_to_name_and_index(button, btn_index)
        return self.buttons[button].drag_button_to_position(btn_index, template_pos.get_pos(), duration)

    ####    ANIMATIONS      ####

    @utils.add_error_info
    def wait_for_animation_stops(self, zone=None, timeout=15, threshold=0.9, step=0.1, window=None, wind_index=-1):
        zone = self.zones[zone].get_area() if zone is not None else None
        return Animations().wait_for_animation_stops(zone, timeout, threshold, step)


    @utils.add_error_info
    def wait_for_animation_starts(self, zone=None, timeout=15, threshold=0.9, step=0.1, window=None, wind_index=-1):
        zone = self.zones[zone].get_area() if zone is not None else None
        return Animations().wait_for_animation_starts(zone, timeout, threshold, step)


    @utils.add_error_info
    def is_zone_animating(self, zone=None, threshold=0.9, step=0.1):
        zone = self.zones[zone].get_area() if zone is not None else None
        return Animations().is_animating(zone, threshold, step)

    ####    IMAGE RECOGNIZION   ####

    @utils.add_error_info
    def get_number_from_zone(self, zone, lang=None, resize_percent=0, resize=0, contrast=0, cache=False, contour=False, invert=False, brightness=0, change_mode=True):
        return self.zones[zone].get_number_from_zone(lang, resize_percent, resize, contrast, cache, contour, invert, brightness, change_mode)


    @utils.add_error_info
    def get_float_number_from_zone(self, zone, lang=None, resize_percent=0, resize=0, contrast=0, cache=False, contour=False, invert=False, brightness=0, change_mode=True):
        return self.zones[zone].get_float_number_from_zone(lang, resize_percent, resize, contrast, cache, contour, invert, brightness, change_mode)


    @utils.add_error_info
    def get_number_with_text_from_zone(self, zone, lang=None, resize_percent=0, resize=0, contrast=0, cache=False, contour=False, invert=False, brightness=0, change_mode=True):
        return self.zones[zone].get_number_with_text_from_zone(lang, resize_percent, resize, contrast, cache, contour, invert, brightness, change_mode)


    @utils.add_error_info
    def get_text_from_zone(self, zone, lang=None, resize_percent=0, resize=0, contrast=0, cache=False, contour=False, invert=False, brightness=0, change_mode=True):
        return self.zones[zone].get_text_from_zone(lang, resize_percent, resize, contrast, cache, contour, invert, brightness, change_mode)


    @utils.add_error_info
    def get_image_from_zone(self, zone, image_name=None):
        return self.zones[zone].get_image_from_zone(zone, image_name)


    # @utils.add_error_info
    # def is_template_in_zone(self, template, zone):
    #     return self.zones[zone].is_template_in_zone(zone, template)


    # @utils.add_error_info
    # def match_template_in_zone(self, template, zone):
    #     return self.zones[zone].is_template_in_zone(template, zone)

    #
    # @utils.add_error_info
    # def get_template_position(self, template, zone):
    #     return self.zones[zone].get_template_position(template, zone)

    ####    VALUES      ####

    #@game_window_function
    @utils.add_error_info
    def get_value_from_config(self, value, index=None):
        value, index = utils.split_to_name_and_index(value, index)
        assert index is not None, "Index must be set"
        return self.values[value].get_value_from_config(index)


    #@game_window_function
    @utils.add_error_info
    def get_last_value_from_config(self, value):
        return self.values[value].get_last_value_from_config()


    #@game_window_function
    @utils.add_error_info
    def iterate_all_values(self, value, reverse=False):
        return self.values[value].iterate_all_values(reverse)


    #@game_window_function
    @utils.add_error_info
    def get_values_from_config(self, value):
        return self.values[value].get_values_from_config()

    ####    OTHER       ####
    #debug only, maybe rework

    #@utils.debug_only
    def save_zone_content_to_output(self, zone):
        zone = self.zones[zone].get_area()
        screen_img = ImageProcessor()._get_screenshot(area=zone)
        ErrorHandler().save_pictures([(screen_img, "zone")])


    # def compare_images(self, id, image, screen, type=None):
    #     if type is None:
    #         assert IOError('Product type parameter should be passed as "type" argument: haxe or launcher')
    #
    #     dir = os.path.abspath(os.path.dirname(__file__))
    #     if type == 'haxe':
    #         imdir = os.path.abspath(os.path.join(os.sep, dir, '..\\..\\launcher\\l_screens\\haxe\\haxe_mobile'))
    #         image = imdir + '\\' + id + '\\' + image
    #     if type == 'launcher':
    #         imdir = os.path.abspath(os.path.join(os.sep, dir, '..\\..\\launcher\\l_screens\\games'))
    #         image = imdir + '\\' + id + '\\' + image
    #
    #     return ImageComparison().return_comparison_result(image, screen)


import unittest
##Unittests are deprecated and not working now. Sorry!

class GameWindowTests(unittest.TestCase):
   pass

if __name__ == '__main__':
    unittest.main()
