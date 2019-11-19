# -*- coding: utf-8 -*-

from pyautogui._pyautogui_x11 import _display, X


NET_WM_PID = _display.intern_atom('_NET_WM_PID')


def _frame(wnd):
    root = _display.screen().root
    frame = wnd
    parent = frame.query_tree().parent
    while parent != root:
        frame = parent
        parent = frame.query_tree().parent

    return frame


def get_active_window():
    return _display.get_input_focus().focus


def get_window_client_rect(wnd):
    cg = wnd.get_geometry()
    fg = _frame(wnd).get_geometry()
    return fg.x + cg.x, fg.y + cg.y, cg.width, cg.height


def set_active_window(wnd):
    wnd.set_input_focus(X.RevertToParent, X.CurrentTime)
    # TODO: ???
    _display.screen().root.query_pointer()


def get_window_pid(wnd):
    wm_pid = wnd.get_property(NET_WM_PID, 6, 0, 32)
    return wm_pid.value.tolist()[0] if wm_pid else None
