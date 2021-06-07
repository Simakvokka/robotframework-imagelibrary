import time
import pyautogui as ag
from robot.api import logger as LOGGER
from robot.libraries import Process
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
from PIL import Image
import pyautogui
import os
from ImageLibrary.errors import CanNotOpenImageException, ImageNotFoundException
from ImageLibrary.image_processor import FindResult
from ImageLibrary.open_cv import OpenCV
from ImageLibrary.libcore.robotlibcore import keyword

ag.FAILSAFE = False

if hasattr(ag, '_pyautogui_x11'):
    from . import _gui_x11 as _gui
elif hasattr(ag, '_pyautogui_win'):
    from . import _gui_win as _gui
else:
    raise NotImplementedError("GUIProcess not supported this platform!")


class GUIProcess(Process.Process):
    START_GUI_TIMEOUT = 60
    START_GUI_PERIOD = 0.1
    _screenshot_counter = 0

    def __init__(self):
        super().__init__()
        self.screenshot_counter = 0

    def _find_image_result(self, img, screen_img, threshold):
        result = OpenCV().find_template(img, screen_img, threshold)
        if result is not None:
            return FindResult(*result, image=img, screen=screen_img, found=True)
        else:
            return FindResult(None, None, None, None, None, image=img, screen=screen_img, found=False)

    def _load_image(self, image):
        """Loads image from reference folders"""
        if isinstance(image, Image.Image):
            return image
        try:
            return Image.open(image)
        except IOError:
            pass
        LOGGER.write("Not opened image {}".format(image, html=True))
        raise CanNotOpenImageException(image)

    def _report_message(self, message, *images):
        """Shows the image info: name and image itself in html log."""
        #image is tuple(name, PIL image)
        msg = message
        for image in images:
            image_filename = "{}.png".format(image[0])
            self._save_to_disk(image[1], image_filename)
            msg += '<br/>{}: <img src="{}"/>'.format(image[0], image_filename)
        LOGGER.write(msg, html=True)

    def _save_to_disk(self, img, name):
        """Saves the screenshots taken in the process of tests executions to the
            'output' folder in the executing directory."""

        screenshot_folder = os.path.join(os.getcwd(), 'output')
        try:
            os.remove(os.path.join(screenshot_folder, name))
        except OSError:
            pass
        i = img.convert('RGB')
        i.save(os.path.join(screenshot_folder, name), "JPEG", quality=10)

    def _make_up_filename(self):
        """Makes a screenshot-file and saves it to the output folder: guiproc-screenshot-1.png"""
        try:
            output = BuiltIn().get_variable_value('${OUTPUT_DIR}')
        except RobotNotRunningError:
            LOGGER.info('Could not get output dir, using default - output')
            output = os.path.join(os.getcwd(), 'output')
        output = os.path.abspath(output)
        if not os.path.exists(output):
            os.mkdir(output)
            self._screenshot_counter += 1
    
        return os.path.join(output,
                    "guiproc-screenshot-{}.png".format(self._screenshot_counter))

    def _locate(self, reference_image, threshold):
        """Tries to locate the given image with threshold on screen.
            Returns location or throws exception"""
        ref_image =self._load_image(reference_image)
        result = self._find_image_result(ref_image, pyautogui.screenshot(region=self.get_window_area()), threshold)
        if result.found:
            location = None
            try:
                location = ag.locateCenterOnScreen(ref_image)
                return location
            except ImageNotFoundException:
                pass
            if location is not None:
                LOGGER.info(f'Image "{reference_image}" found at {location}')
                return location
        else:
            msg = "Image with threshold {} was not found on screen".format(threshold)
            image_info = ("image", result.image)
            screen_info = ("screen", result.screen)
            self._report_message(msg, image_info, screen_info)
            raise ImageNotFoundException(reference_image)
        
    # @keyword
    # def start_gui_process(self, command, *args, **kwargs):
    #     handle = self.start_process(command, *args, **kwargs)
    #     proc = self.get_process_object(handle)
    #
    #     max_time = time.time() + self.START_GUI_TIMEOUT
    #     while self.is_process_running(handle) and not hasattr(proc, 'wnd'):
    #         awnd = _gui.get_active_window()
    #         if awnd and proc.pid == _gui.get_window_pid(awnd):
    #             proc.wnd = awnd
    #             break
    #
    #         if time.time() > max_time:
    #             self.terminate_process(handle, kill=True)
    #             raise RuntimeError(f"Failed to start GUI '{command}', window not found!")
    #         time.sleep(self.START_GUI_PERIOD)
    #
    #     return handle
    #
    #@keyword
    #todo: keyword might be useless
    # def activate_gui_process(self, handle):
    #     if not self.is_process_running(handle):
    #         raise RuntimeError(f"No program running with handle='{handle}'")
    #
    #     proc = self.get_process_object(handle)
    #     if not proc:
    #         raise RuntimeError(f"No program found by handle='{handle}'")
    #
    #     if not hasattr(proc, 'wnd') or not proc.wnd:
    #         raise RuntimeError(f"Program with handle '{handle}' have no window!")
    #
    #     _gui.set_active_window(proc.wnd)

    # def _get_screenshot(self, x, y, w, h, resize_percent=0):
    #     wnd = _gui.get_active_window()
    #     rc = _gui.get_window_client_rect(wnd)
    #     img = ag.screenshot(region=(rc[0] + int(x), rc[1] + int(y), int(w), int(h)))
    #
    #     imgFile = self._make_up_filename()
    #     img.save(imgFile)
    #
    #     imgresize = Image.open(imgFile)
    #     width, height = imgresize.size
    #     width_resize = width * int(resize_percent) / width + width
    #     height_resize = height * int(resize_percent) / height + height
    #     imgresize = imgresize.resize((int(round(width_resize)), int(round(height_resize))), Image.ANTIALIAS)
    #     imgresize.save(imgFile)
    #
    #     LOGGER.info('Screenshot taken: {0}<br/><img src="{0}" '
    #                 'width="100%" />'.format(imgFile), html=True)
    #     return imgresize
    
    
    def _get_window(self):
        wnd = _gui.get_window()
        return _gui.get_window_client_rect(wnd)

    @keyword
    def get_window_area(self):
        wnd = _gui.get_active_window()
        return _gui.get_window_client_rect(wnd)

        
    @keyword
    def type(self, key):
        """Type text and keyboard keys.
          
           Used for quick operations with keyboard and not like full _Type   key_ keyword from ImageHorizon Library. Use carefully
         
        Examples:
        | Type | enter
        """
        pyautogui.press(key)