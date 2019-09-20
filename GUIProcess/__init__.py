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

        output = os.path.abspath(output)
        if not os.path.exists(output):
            os.mkdir(output);
        self._screenshot_counter += 1

        return os.path.join(output,
                    "guiproc-screenshot-%d.png" % (self._screenshot_counter))


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


    def get_window_area(self):
        wnd = _gui.get_active_window()
        return _gui.get_window_client_rect(wnd)

