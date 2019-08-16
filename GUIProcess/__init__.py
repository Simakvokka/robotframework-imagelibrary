#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import re

import pyautogui as ag
from pytesseract import image_to_string
from robot.api import logger as LOGGER
from robot.libraries import Process
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
from PIL import Image

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

    def _make_up_filename(self):
        try:
            output = BuiltIn().get_variable_value('${OUTPUT_DIR}')
        except RobotNotRunningError:
            LOGGER.info('Could not get output dir, using default - output')
            output = os.path.join(os.getcwd(), 'output')

        output = os.path.abspath(output);
        if not os.path.exists(output):
            os.mkdir(output);
        self._screenshot_counter += 1

        return os.path.join(output,
                    "guiproc-screenshot-%d.png" % (self._screenshot_counter));


    def start_gui_process(self, command, *args, **kwargs):
        handle = self.start_process(command, *args, **kwargs)
        proc = self.get_process_object(handle)

        max_time = time.time() + self.START_GUI_TIMEOUT
        while self.is_process_running(handle) and not hasattr(proc, 'wnd'):
            awnd = _gui.get_active_window()
            if awnd and proc.pid == _gui.get_window_pid(awnd):
                proc.wnd = awnd
                break

            if time.time() > max_time:
                self.terminate_process(handle, kill=True)
                raise RuntimeError("Failed to start GUI '%s', window not found!" % command)
            time.sleep(self.START_GUI_PERIOD)

        return handle

    def activate_gui_process(self, handle):
        if not self.is_process_running(handle):
            raise RuntimeError("No program running with handle='%s'" % handle)

        proc = self.get_process_object(handle)
        if not proc:
            raise RuntimeError("No program found by handle='%s'" % handle)

        if not hasattr(proc, 'wnd') or not proc.wnd:
            raise RuntimeError("Program with handle '%s' have no window!" % handle)

        _gui.set_active_window(proc.wnd)

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
    #     imgresize.save(imgFile);
    #
    #     LOGGER.info('Screenshot taken: {0}<br/><img src="{0}" '
    #                 'width="100%" />'.format(imgFile), html=True)
    #     return imgresize
    #
    # def get_text_from_region(self, top, left, width, height):
    #     img = self._get_screenshot(top, left, width, height)
    #
    #     txt = image_to_string(img, config="-psm 6")
    #     LOGGER.trace("Get text from region (%s, %s, %s, %s) = '%s'" %
    #                  (top, left, width, height, txt))
    #     return txt
    #
    #
    # def get_number_with_text_from_region(self, top, left, width, height, resize_percent=0):
    #     img = self._get_screenshot(top, left, width, height, resize_percent)
    #
    #     txt = image_to_string(img, config="-psm 6")
    #
    #     num = re.compile('[0-9]')
    #     num = num.findall(txt)
    #     num = ''.join(num)
    #
    #     LOGGER.trace("Get text from region (%s, %s, %s, %s) = '%s'" %
    #                  (top, left, width, height, txt))
    #     return num
    #
    #
    # def get_number_from_region(self, top, left, width, height, lang=None, resize_percent=0):
    #     img = self._get_screenshot(top, left, width, height, resize_percent)
    #
    #     mydir = os.path.abspath(os.path.dirname(__file__))
    #     resdir = os.path.abspath(os.path.join(os.sep, mydir, r"..\..\resources"))
    #
    #     config = ""
    #     if lang:
    #         config += ("--tessdata-dir %s -l %s " % (resdir, lang)).replace("\\", "//")
    #     config += "-psm 8 -c tessedit_char_whitelist=0123456789"
    #
    #     txt = image_to_string(img, config=config)
    #     LOGGER.trace("Get number from region (%s, %s, %s, %s) = '%s'" %
    #                  (top, left, width, height, txt))
    #     return txt

    def get_window_area(self):
        wnd = _gui.get_active_window()
        return _gui.get_window_client_rect(wnd)

