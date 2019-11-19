# -*- coding: utf-8 -*-

import os
import pyautogui as ag
from robot.api import logger as LOGGER
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError

ag.FAILSAFE = False

if hasattr(ag, '_pyautogui_x11'):
    from . import _gui_x11 as _gui
elif hasattr(ag, '_pyautogui_win'):
    from . import _gui_win as _gui
else:
    raise NotImplementedError("GUIProcess not supported this platform!")


class GUIProcess(object):
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
            os.mkdir(output)
        self._screenshot_counter += 1

        return os.path.join(output,
                    "guiproc-screenshot-{}.png".format(self._screenshot_counter))

    def get_window_area(self):
        
        wnd = _gui.get_active_window()
        return _gui.get_window_client_rect(wnd)

