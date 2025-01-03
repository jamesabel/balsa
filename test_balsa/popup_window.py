from typing import List
import win32gui


def _dialog_enum_callback(hwnd: int, dialogs: List[int]) -> None:
    """
    Callback used by EnumWindows. Checks if the given window is a visible
    dialog (#32770) and contains an "OK" button among its children.
    """
    if win32gui.IsWindowVisible(hwnd):
        class_name = win32gui.GetClassName(hwnd)
        # #32770 is the class name for standard dialog boxes in Windows
        if class_name == "#32770":
            # Look for a child window with the text "OK"
            ok_button_hwnd = win32gui.FindWindowEx(hwnd, 0, None, "OK")
            if ok_button_hwnd:
                dialogs.append(hwnd)


def is_popup_dialog_with_ok() -> bool:
    """
    Returns True if there is at least one visible dialog (#32770)
    on the screen that has an "OK" button, otherwise False.
    """
    dialog_hwnds: List[int] = []
    # Enumerate all top-level windows, passing the callback and a list to store matches
    win32gui.EnumWindows(_dialog_enum_callback, dialog_hwnds)
    dialog_exists = len(dialog_hwnds) > 0
    return dialog_exists
