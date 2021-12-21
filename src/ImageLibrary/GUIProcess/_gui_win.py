import ctypes
import ctypes.wintypes
from ctypes.wintypes import POINT


class RECT (ctypes.Structure):
    _fields_ = [("left", ctypes.wintypes.LONG),
                ("top",  ctypes.wintypes.LONG),
                ("right", ctypes.wintypes.LONG),
                ("bottom", ctypes.wintypes.LONG)]


def get_window_pid(hwnd):
    pid = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def get_active_window():
    return ctypes.windll.user32.GetForegroundWindow()


def get_window_client_rect(hwnd):
    rc = RECT()
    ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rc))

    pt = POINT()
    pt.x = rc.left
    pt.y = rc.top
    ctypes.windll.user32.ClientToScreen(hwnd, ctypes.byref(pt))

    return pt.x, pt.y, rc.right - rc.left, rc.bottom - rc.top


def set_active_window(hwnd):
    # ctypes.windll.user32.SetFocus(hwnd)
    ctypes.windll.user32.SetForegroundWindow(hwnd)
