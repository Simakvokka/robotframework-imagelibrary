import yaml
import re
import os
import tkinter as tk
from robot.api import logger as LOGGER
from ImageLibrary.libcore.librarycomponent import LibraryComponent
from ImageLibrary.libcore.robotlibcore import keyword

from ImageLibrary.buttons.button_constructor import ButtonConstructor
from ImageLibrary.error_handler import ErrorHandler
from ImageLibrary.window import Window
from ImageLibrary.buttons.global_button import GlobalButtonRegistry
from ImageLibrary.image_processor import ImageProcessor
from ImageLibrary.main_window import MainWindow
from ImageLibrary.open_cv import OpenCV
from ImageLibrary import errors, utils
from ImageLibrary.window_function import window_function
from ImageLibrary.animations import Animations
from ImageLibrary.GUIProcess import GUIProcess


"""To create a Keywords Documentation in Robot style format run the libdoc with this file."""

def _get_images_from(node):
    """get_images_from(node) -> set(string)
        Gets all images from this node recursively
        Image is any value ends with ".png"
    """
    images = set()
    if isinstance(node, (str, bytes)):
        if re.search('.*\.png$', node) is not None:
            images.add(node)

    elif isinstance(node, dict):
        for key, value in sorted(node.items()):
            images.update(_get_images_from(value))

    elif isinstance(node, list):
        for value in node:
            images.update(_get_images_from(value))

    return images


def _check_config(config, reference_folders):
    images = _get_images_from(config)
    not_found_folders = set()
    not_found = images.copy()
    for folder in reference_folders:
        if not os.path.isdir(folder):
            not_found_folders.add(folder)
            continue
        for image in images:
            if image in not_found and os.path.isfile(os.path.join(folder, image)):
                not_found.remove(image)

    out = ""
    if bool(not_found_folders):
        out += "Not found reference folders: " + ", ".join(not_found_folders)

    if bool(not_found):
        out += " and " if bool(not_found_folders) else "Not found "
        out += "images: " + ", ".join(not_found)
        out += " at folders:" + ", ".join(set(reference_folders).difference(not_found_folders))

    if bool(out):
        raise errors.InitError(out)

    return True


class Keywords(LibraryComponent, Animations, GUIProcess):
    def __init__(self, screenshot_folder, state, debug=False):
        super().__init__(state)
        if screenshot_folder is None:
            self.screenshot_folder = os.path.join(os.getcwd())
        else:
            self.screenshot_folder = screenshot_folder
        #mv - main window
        self.mw = None
        self.debug = debug
        self.gui_process = GUIProcess()
    
    @keyword
    def init(self, settings_file, reference_folders, area=None):

        """Initializes ImageLibrary for current suite run.
            Pass as args:

            settings_file - path to .yaml configs as list
            reference_folders - path to screens folders as list
            area - window area taken with keyword Get Window Area
            log_type - if init Haxe tests pass 'browser'
            update_config - to change some options from .yaml config for current suite run pass a yaml dict like string with proper values
                Examples:
                    ${update_config}      {'main': {'multiple_buttons': {'minus': {'direction': 'horizontal',
                    ...                               'expected_count': '1',
                    ...                                'image': 'minus.png',
                    ...                                'threshold': '0.999'},
                    ...                    'minus_d': {'direction': 'horizontal',
                    ...                                 'expected_count': '1',
                    ...                                  'image': 'minus_d.png',
                    ...                                  'threshold': '0.999'},
                    ...                      'plus': {'direction': 'horizontal',
                    ...                               'expected_count': '1',
                    ...                               'image': 'plus.png',
                    ...                               'threshold': '0.999'},
                    ...                      'plus_d': {'direction': 'horizontal',
                    ...                                'expected_count': '1',
                    ...                                 'image': 'plus_d.png',
                    ...                                 'threshold': '0.999'}}}}

                    ${update_config}        {'main':{'buttons':{'start': 'take_d.png', 'bet': '-'}}}



            |  Init  =  |   ${Settings}   |  ${References}   |    ${windowArea}  |  update_config=${update_config}

        """
        
        #old, works from robot execution context
        #self.debug = utils.to_bool(BuiltIn().get_variable_value("${DEBUG_MODE}", False))
        
        #to work in unittests avoiding robot execution context
        # for i in sys.argv:
        #     if re.search('DEBUG_MODE:\w+', i):
        #         self.debug =  utils.to_bool(re.search('DEBUG_MODE:\w+', i).group(0)[11:])

        self.settings = {}
        self.button_registry = GlobalButtonRegistry('hack')

        if hasattr(settings_file, '__iter__'):
            for setting in settings_file:
                with open(setting, 'r') as f:
                    config = yaml.safe_load(f)

                if "global_buttons_defs" in config:
                    self.button_registry.update_info(config["global_buttons_defs"])
                    del config["global_buttons_defs"]

                self.settings.update(config)
        else:
            with open(settings_file) as f:
                config = yaml.safe_load(f)
   
        if "global_buttons_defs" in config:
            self.button_registry.update_info(config["global_buttons_defs"])
            del config["global_buttons_defs"]
        self.settings.update(config)

        # if self.debug: LOGGER.info('<font size="2"><b>UPDATED YAML CONFIG:</b></font>' + "\n" + "\n".join(
        #     "<table width='800'><tr><td><i>key</i></td><td><i>values</i></td></tr><tr></tr>"
        #     "<tr><td><b>{}</b></td><td style='width:1000px text-align:justify'>{}</td></tr></table>".format(k, v)
        #     for k, v in self.settings.items()), html=True)

        self.reference_folders = reference_folders
        _check_config(self.settings, self.reference_folders)

        if area is None:
            screen_width = tk.Tk().winfo_screenwidth()
            screen_height = tk.Tk().winfo_screenheight()
            self.area = (0, 0, screen_width, screen_height)
        else:
            self.area = area

        if "main" not in self.settings:
            raise errors.ConfigError('config must contain "main" section')

        self.error_handler = ErrorHandler(self.screenshot_folder, self.area)
        
        try:
            self.image_processor = ImageProcessor(self.area, OpenCV(), reference_folders, self.error_handler)
        except TypeError:
            LOGGER.info(
                "Something went wrong while the ImageLibrary library init process: it doesn't get the required params.\n"
                "Program may not be loaded.")

        self.button_registry.report_merge_errors()

        self.button_constructor = ButtonConstructor()

        # init all windows
        self.windows = {}
        for name, config in sorted(self.settings.items()):
            if name == 'main':
                self.mw = MainWindow(config, "main", self.button_constructor, self.debug)
            elif isinstance(config, dict):
                self.windows[name] = Window(config, name, self.button_constructor, self.debug)

            # window has multiple screens
            elif isinstance(config, list):
                self.windows[name] = []
                for index, screen in enumerate(config):
                    if not isinstance(screen, dict):
                        raise errors.ConfigError(
                            "screen {} of window {} not properly configured: dict expected".format(index + 1, name))

                    self.windows[name].append(Window(screen, name, self.button_constructor, self.debug))

    def _get_window(self, window, index=-1):
        if window is not None:
            return utils.get_element_by_name_and_index(self.windows, window, index)
            # todo:check
            #return self.windows[window]
        else:
            return self.mw
        
    @keyword
    def start_gui_process(self, command, *args, **kwargs):
        """Starts the given process using the standart Robot library Process, but also takes the programm window as
            the active window. Zones and screenshots will be taken related to the program coords."""
        return self.gui_process.start_gui_process(command, *args, **kwargs)


    ####    ERROR HANDLING      ####
    @keyword
    def save_state(self):
        """Saves the current state. Saves the screenshot of the currently active area."""
        self.error_handler.save_state()

    @keyword
    def show_build_quality(self):
        """Shows an image in html log."""
        self.error_handler.show_build_quality()

    @keyword
    def clear_screenshots_history(self):
        """Clears screenshots history: all the screenshots taken while test run will be removed from history."""
        self.error_handler.clear_history()

    @keyword
    def dump_screenshots_to_output(self):
        """Puts the screenshots taken while test to the specified folder."""
        self.error_handler.dump_screenshots()

    ####    CACHE   ####
    @keyword
    def take_cache_screenshot(self):
        self.image_processor.take_cache_screenshot()

    ####    FULL WINDOW     ####
    @keyword
    def window_should_be_on_screen(self, window=None, wind_index=-1):
        """Checks the presence of the given window on screen. Fails if not True.
        Pass the window name as _argument_. By default the _main window_ is used. So to check it you can pass no arguments

        Examples:
        |   _For main window_:
        |   Window Should Be On Screen
        |   _For other windows_:
        |   Window Should Be On Screen  | window=window_name
        """
        return self._get_window(window, wind_index).window_should_be_on_screen()

    @keyword
    @window_function
    def wait_for_show(self, window=None, timeout=15, wind_index=-1):
        """Waits until the given window occurs on the screen. If catches the part of the given template - considers the window to be there.
		_main window_ is used by default - you may not pass it as argument.
		*NB*: be careful with sliding windows (such windows takes some time to appear fully on screen).
		Use `Wait For Window To Stop` instead.
		Examples:
		|   Wait For Show | window=window_name
		"""
        return self._get_window(window, wind_index).wait_for_show(timeout)

    @keyword
    @window_function
    def wait_for_hide(self, window=None, timeout=15, wind_index=-1):
        """Waits until the given window fully disappears from the screen.
		Pass ``window`` name as argument. ``timeout`` is set to 15 by default. You can also increase it's value.
		_Main_ window is used by default - you may not pass it as argument.

		Examples:
		|   Wait For Hide | window=window_name
		"""
        return self._get_window(window, wind_index).wait_for_hide(timeout)

    # @keyword
    # def has_window(self, window=None, wind_index=-1):
    #     if window is not None:
    #         if window not in self.settings:
    #             return False
    #         if isinstance(self.settings[window], list):
    #             return 0 < wind_index <= len(self.settings[window])
    #
    #         return True
    #     else:
    #         return "main" in self.settings

    @keyword
    def is_window_on_screen(self, window=None, wind_index=-1):
        """Checks if the given window is on screen. Returns boolean.
		_Main_ window is used by default - you may not pass it as argument.

		Examples:
		|   ${window} = | Is Window On Screen | window=window_name
		"""
        return self._get_window(window, wind_index)._is_window_on_screen()[0]


    @keyword
    @window_function
    def wait_for_window_to_stop(self, window=None, timeout=15, move_threshold=0.99, step=0.1, wind_index=-1):
        """Waits for window to show and then waits for one of 'if' picture stops.
            Takes the first image from "exist":"if" section.
            Used for sliding windows.
            _Main_ window is used by default - you may not pass it as argument.
            Examples:
            |   Wait For Window To Stop | window=window_name
        """
        pass
    
    ####    IMAGES      ####
    @keyword
    @window_function
    def find_image(self, image, threshold=0.99, cache=False, zone=None):
        """Tries to locate the passed image on screen.
            If zone is passed, searches in this zone, else on the whole active window.
            Returns boolean.
        """
        pass

    @keyword
    @window_function
    def is_image_on_screen(self, image, threshold=0.99, cache=False, zone=None):
        """Validates the presence of passed image on screen.
            Searches in the provided zone or on the whole active window.
            Returns boolean.
        """
        pass

    @keyword
    @window_function
    def wait_for_image(self, image, threshold=0.99, timeout=15, zone=None):
        """Waits for given timeout for image to appear on screen.
            Searches in the provided zone or on the whole active window.
            Returns boolean. If False also throws warning.
        """
        pass

    @keyword
    @window_function
    def wait_for_image_to_stop(self, image, threshold=0.99, timeout=15, move_threshold=0.99, step=0.1):
        """Waits for given timeout until image stops moving on screen. Ex, if your image slides you need to wait until it fully appears on screen.
            Searches in the provided zone or on the whole active window.
            Returns boolean. If False also throws warning.
        """
        pass

    @keyword
    @window_function
    def image_should_be_on_screen(self, image, threshold=0.99, cache=False, zone=None):
        """Validates the image presence on screen.
            If image is not on screen keyword fails.
        """
        pass

    @keyword
    @window_function
    def image_should_not_be_on_screen(self, image, threshold=0.99, cache=False, zone=None):
        """Validates the image absence on screen.
            If image is on screen - keyword fails.
        """
        pass

    @keyword
    @window_function
    def wait_for_image_to_hide(self, image, threshold=0.99, timeout=15, zone=None):
        """Waits for given timeout until image disappears from screen.
            Returns boolean. Throws warning if False.
        """
        pass


    ####    TEMPLATES       ####
    @keyword
    @window_function
    def is_template_on_screen(self, template, index=-1, threshold=None, cache=False, zone=None, window=None, wind_index=-1):
        """Checks if the given template is present on screen. Returns boolean.
            Pass the _template_, _zone_, _threshold_ as arguments. All the parameters should be defined in config.

            Example:
            |   ${my_templ} = | Is Template On Screen | template=templ_name | zone=zone_coordinates | threshold=0.99
        """
        pass

    @keyword
    @window_function
    def wait_for_template(self, template, index=-1, threshold=None, timeout=15, zone=None, window=None, wind_index=-1):
        """Waits until the given template appears on the screen. Shows warning if template was not found
            during the timeout.
            Pass _template_, _threshold_, _timeout_, _zone_ as arguments. All are optional except ``template``.

            Examples:
            |   Wait For Template | template=templ_name | threshold=0.99 | timeout=15 | zone=zone_coordinates
        """
        pass

    @keyword
    @window_function
    def wait_for_template_to_hide(self, template, index=-1, threshold=None, timeout=15, zone=None, window=None,
                                  wind_index=-1):
        """Waits until the given template disappears from screen during the given timeout.
            Pass _template_, _threshold_, _timeout_, _zone_ as arguments. All are optional except ``template``.

            Examples:
            |   Wait For Template To Hide | template=templ_name | threshold=0.99 | timeout=15 | zone=zone_coordinates
        """
        pass

    @keyword
    @window_function
    def wait_for_template_to_stop(self, template, index=-1, threshold=None, timeout=15, move_threshold=0.99, step=0.1,
                                  window=None, wind_index=-1):
        """Waits until the given template fully stops on the screen. The same as `Wait For Window To Stop`
            Pass the _template_, _threshold_, _timeout_ as arguments. AllAll are optional except ``template``.

            Examples:
            |   Wait For Template To Stop | template=template_name | threshold=0.99 | timeout=15
        """
        pass

    @keyword
    @window_function
    def template_should_be_on_screen(self, template, index=-1, threshold=None, cache=False, zone=None, window=None,
                                     wind_index=-1):
        """Checks that the given template is on screen. Returns boolean.
            Pass the _template_, _threshold_, _timeout_, _zone_ as arguments. All are optional except ``template``.

            Examples:
            |   ${on_screen} = | Template Should Be On Screen | template=template_name | threshold=0.99 | zone=zone_coordinates
        """
        pass

    @keyword
    @window_function
    def template_should_not_be_on_screen(self, template, index=1, threshold=None, cache=False, zone=None, window=None,
                                         wind_index=-1):
        """Checks that the given template is not on screen. Returns boolean.
            Pass the _template_, _threshold_, _timeout_, _zone_ as arguments. All are optional except ``template``.

            Examples:
            |   ${not_on_screen} = | Template Should Not Be On Screen | template=template_name | threshold=0.99 | zone=zone_coordinates
        """
        pass

    @keyword
    @window_function
    def get_templates_count(self, template, index=-1, threshold=None, cache=False, zone=None, window=None, wind_index=-1):
        """Counts the number of given template on screen. Returns amount.
            Pass the _template_, _threshold_, _timeout_, _zone_ as arguments. All are optional except ``template``.

            Examples:
            |   ${templ_amount} = | Get Templates Count | template=template_name | threshold=0.99 | zone=zone_coordinates
        """
        pass

    @keyword
    @window_function
    def is_complex_template_on_screen(self, template, threshold=None, cache=False, zone=None, window=None, wind_index=-1):
        """Checks if all the templates from the given set (as list) are on screen. Returns boolean. Templates should be defined in config as a list values in ``complex_templates``.
            Pass the _template_, _threshold_, _timeout_, _zone_ as arguments. All are optional except ``template``.

            Examples:
            |   ${template} = | Is Complex Template On Screen | template=template_name | threshold=0.99 | zone=zone_coordinates
        """
        pass

    @keyword
    @window_function
    def is_any_part_of_complex_template_on_screen(self, template, threshold=None, cache=False, zone=None, window=None,
                                                  wind_index=-1):
        """Checks if one or more of the given templates set (as list) is on screen. Returns boolean. Templates should be defined in config as a list values in ``complex_templates``.
            Pass the _template_, _threshold_, _timeout_, _zone_ as arguments. All are optional except ``template``.

            Examples:
            |   ${complex_templ} = | Is Any Part Of Complex Template On Screen | template=template_name | threshold=0.99 | zone=zone_coordinates
        """
        pass

    @keyword
    @window_function
    def wait_for_complex_template(self, template, threshold=None, timeout=15, zone=None):
        """Waits until all the elements from the given templates set (as list) appears on screen. Templates should be defined in config as a list values in ``complex_templates``.
            Pass the _template_, _threshold_, _timeout_, _zone_ as arguments. All are optional except ``template``.

            Examples:
            |   Wait For Complex Template | template=template_name | threshold=0.99 | zone=zone_coordinates """
        pass

    @keyword
    @window_function
    def wait_for_complex_template_to_hide(self, template, threshold=None, timeout=15, zone=None):
        """Waits until all the elements from the given templates set (as list) disappears from screen. Templates should be defined in config as a list values in ``complex_templates``.
            Pass the _template_, _threshold_, _timeout_, _zone_ as arguments. All are optional except ``template``.

            Examples:
            |   Wait For Complex Template To Hide | template=template_name | threshold=0.99 | zone=zone_coordinates
        """
        pass
    
    ###    BUTTONS     ####
    @keyword
    @window_function
    def press_button(self, button, index=-1, times=1, window=None, wind_index=-1):
        """Presses the given button.
            Buttons should be defined in config according to the buttons types.
            Pass the _button_ and optionally the _times_ to press (one press == 1).

            Examples:
            |   Press Button | start (or button=start) | times=5
        """
        pass
    
    #todo
    # @keyword
    # @window_function
    # def get_button_state(self, button, index=-1, window=None, wind_index=-1):
    #     """Gets the button state: disabled, normal, highlighted. Button and its states should be defined in config
    #         in ``global_buttons`` section.
    #
    #         Examples:
    #         |   ${state} = | Get Button State | start (or button=start)
    #      """
    #     pass

    @keyword
    @window_function
    def button_should_be_on_state(self, button, index=-1, state="normal", window=None, wind_index=-1):
        """Checks if button is in the given state: disabled, normal, highlighted. Fails if not.
            Button and its states should be defined in config in ``global_buttons`` section.
            By default ``state=normal``

            Examples:
            |   Button Should Be On State | start (or button=start) | state=normal
         """
        pass

    @keyword
    @window_function
    def wait_for_button_state(self, button, index=-1, state="normal", timeout=15, window=None, wind_index=-1):
        """Waits until the given button reaches the given state: disabled, normal, highlighted.
            Warns if the state is not reached in the given time period.
            Button and its states should be defined in config in ``global_buttons`` section.
            Pass _button_, _state_, _timeout_ as arguments. All except _button_ are optional.

            Examples:
            |   Wait For Button State | start (or button=start) | state=normal | timeout=15
        """
        pass

    @keyword
    @window_function
    def is_button_active(self, button, index=-1, window=None, wind_index=-1):
        """Checks if button is active: in _normal_ or _highlighted_ state. Returns boolean.
            Button and its states should be defined in ``global_buttons`` section in config and have states: normal/highlighted versus disabled.

            Examples:
            |   ${is_active} = | Is Button Active | start (or button=start)
        """
        pass

    @keyword
    @window_function
    def wait_for_button_activate(self, button, index=-1, timeout=15, window=None, wind_index=-1, step=0.5):
        """Waits until the button has an active stateюю Button and its states should be defined in ``global_buttons`` section in configю
            Pass _button_ and _timeout_ as arguments. Timeout is optional and by default = 15.

            Examples:
            |   Wait For Button Activate | start (or button=start) | timeout=15
        """
        pass

    @keyword
    @window_function
    def wait_for_activate_and_press(self, button, index=-1, timeout=15, window=None, wind_index=-1, step=0.5):
        """Same as `Wait For Button Activate`, after button is active presses it.
        """
        pass

    @keyword
    @window_function
    def wait_for_dynamic_button(self, button, index=-1, timeout=15, window=None, wind_index=-1, threshold=0.99):
        """Wait until dynamic buttons appears on screen for the given timeout. If timeout is over shows warning.
            Button should be defined in config in ``dynamic_buttons`` section.

            Examples:
            |   Wait For Dynamic Button | start (or button=start)
        """
        pass

    @keyword
    @window_function
    def is_dynamic_button_on_screen(self, button, index=-1, window=None, wind_index=-1):
        """Checks if button with dynamic state is on screen. Returns boolean.
            Button should be defined in config in ``dynamic_buttons`` section.

            Examples:
            |   ${dynamic} = | Is Dynamic Button On Screen | start (or button=start)
        """
        pass

    @keyword
    @window_function
    def drag_button_to_template(self, button, btn_index=-1, template=None, tmpl_index=-1, duration=0.1, cache=False,
                                window=None, wind_index=-1):
        """Clicks on the given button and moves it to the given template.
            Define buttons and templates in config.

            Examples:
            |   Drag Button To Template | button=button_name | template=template_name
        """
        pass


    ###    ANIMATIONS      ####
    @keyword
    @window_function
    def wait_for_animation_stops(self, zone=None, timeout=15, threshold=0.9, step=0.1, window=None, wind_index=-1):
        """S.wait_for_animation_stops(self, zone, timeout, threshold, window, wind_index) -> bool
            Waits while animation in selected zone will be over and return True if success or False if timeout exceeded
            zone - name of zone, where to find animation or None for whole window
            timeout - time to wait for animation stops
            threshold - how different can be animation frames:
                1.0 - images are identical
                0.98 - images are slightly different
                0.9 looks like nice threshold when you need to check animation stops (self, calibration needed)
                ...
                0 - all images pixels are different (self, black and white screen)
            step - how often to make screenshots. If animation is fast, probably you should pass 0

            Examples:
            |   Wait For Animation Stops | zone=zone_coordinates | timeout=15 | threshold=0.99 | step=0.1
        """
        pass

    @keyword
    @window_function
    def wait_for_animation_starts(self, zone=None, timeout=15, threshold=0.9, step=0.1, window=None, wind_index=-1):
        """Same as `Wait For Animation Stops` but on the contrary."""
        pass

    @keyword
    @window_function
    def is_zone_animating(self, zone=None, threshold=0.9, step=0.1, window=None, wind_index=-1):
        """Checks if the given zone is animating. Returns boolean.
            Pass _zone_, _threshold_, _step_ as arguments. All are optional. If zone is not provided
                the while active area is taken.

            Examples:
            |   ${is_animating} = | Is Zone Animating | zone=zone | threshold=0.9 | step=0.1
        """
        pass

    ####    IMAGE RECOGNIZION   ####
    @keyword
    @window_function
    def get_number_from_zone(self, zone, lang=None, resize_percent=0,  brightness=0, resize=0, contrast=0, cache=False,
                             contour=False, invert=False, window=None, wind_index=-1):
        """Returns the recognized number from the given zone.

            All arguments except _zone_ are optional. _cache_ is False and must not be changed.

            Examples:
            |   ${win} = | Get Number From Zone | zone=win | lang=lang_name | resize_pecent=30 or resize=30 | contrast=1 | background=zone_background | contour=${False} | invert=${False} | brightness=1
        """
        pass

    @keyword
    @window_function
    def get_float_number_from_zone(self, zone, lang=None, resize_percent=0,  brightness=0, resize=0, contrast=0, cache=False, window=None,
                                   wind_index=-1, invert=False):
        """Same as `Get Number From Zone` but returns float number.
        """
        pass

    @keyword
    @window_function
    def get_number_with_text_from_zone(self, zone, lang=None, resize_percent=0, resize=0, contrast=0, cache=False,
                                       contour=False, invert=False, brightness=0, change_mode=True):
        """Same as `Get Number From Zone` but also recognizes text if there are numbers with text in the given zone.
        After processing text is deleted, only number is returned. We use it for win fields: 10 Won.
        """
        pass

    @keyword
    @window_function
    def get_text_from_zone(self, zone, lang=None, resize_percent=0, resize=0, contrast=0, cache=False,
                                       contour=False, invert=False, brightness=0, change_mode=True):
        """Returns the recognized text from zone, if there is only text. Arguments logic is the same as for `Get Number From Zone`
        """
        pass

    @keyword
    @window_function
    def get_image_from_zone(self, zone, image_name=None):
        """Saves the screenshot from the given zone to the provided 'output' folder or the test root folder as 'image_name.png', or 'image_from_zone.png' if
            name argument is not passed
        """
        pass
    #todo:
    # @keyword
    # @window_function
    # def is_template_in_zone(self, template, zone):
    #     """Checks if the given template is present in the provided zone, using knn algorythms. Returns boolean.
    #
    #         Examples:
    #         |   ${is_on_screen} = | Is Template In Zone | template=templ_name.png | zone=zone_coordinates
    #     """
    #     pass
    
    # @keyword
    # @window_function
    # def match_template_in_zone(self, template, zone):
    #     """Checks if the given template is present in the provided zone. Returns boolean.
    #
    #         Examples:
    #         |   ${is_on_screen} = | Match Template On Screen | template=templ_name | zone=zone_coordinates
    #     """
    #     pass

    # @keyword
    # @window_function
    # def get_template_position(self, template, zone):
    #     """Returns the found template coordinates from the provided zone.
    #
    #         Examples:
    #         |   ${pos} = | Get Template Position | template=templ_name | zone=zone_coordinates
    #     """
    #     pass
    
    ###    VALUES      ####
    @keyword
    @window_function
    def get_value_from_config(self, value, index=None, window=None, wind_index=-1):
        """Gets the value from config.
            Pass the name of value from ``values`` section and index.

            Examples:
            |   ${value} = | Get Value From Config | bets[1]
        """
        pass

    @keyword
    @window_function
    def get_last_value_from_config(self, value, window=None, wind_index=-1):
        """Gets the last value from config.
            Pass the name of value from ``values`` section
        """
        pass

    @keyword
    @window_function
    def iterate_all_values(self, value, reverse=False, window=None, wind_index=-1):
        """Iterates through all values in the given value from ``values`` section.
            Pass ``reverse=True`` if you need the reversed order. By default is 'False'
        """
        pass

    @keyword
    @window_function
    def get_values_from_config(self, value, window=None, wind_index=-1):
        """Gets all given values from config. As list.
            Pass the name of value from ``values`` section.

            Examples:
            |   ${value} = | Get Values From Config | bets
        """
        pass

    @keyword
    def get_value_and_increase_iterator(self, iterator):
        try:
            return iterator.__next__()
        except StopIteration:
            return None

    @keyword
    def get_count_for_iterator(self, iterator):
        return len(iterator)

    @keyword
    @window_function
    def compare_images(self, image, screen):
        """Compares two given images. Returns boolean.
            Pass the template image and screened image.

            Examples:
            |   Compare Images  image1 | image2
        """
        pass

    
    ####    OTHER       ####
    @keyword
    @window_function
    def save_zone_content_to_output(self, zone, window=None, wind_index=-1):
        """FOR DEBUG: saves the content (screenshot) of the provided zone. Pass zone. Image is saved to the 'output' folder or the test root folder.
        """
        pass


