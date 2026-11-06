import time
import pyautogui
import pygetwindow as gw

WINDOW_TITLE = 'WhatsApp'

def get_window():
    # Exact match, other windows (e.g. editors) can contain "WhatsApp" in their title
    for window in gw.getWindowsWithTitle(WINDOW_TITLE):
        if window.title == WINDOW_TITLE:
            return window
    return None

def is_focused():
    active = gw.getActiveWindow()
    return active is not None and active.title == WINDOW_TITLE

def focus_window(timeout=20, load_delay=4):
    deadline = time.time() + timeout
    waited_for_window = False

    while time.time() < deadline:
        window = get_window()
        if window is None:
            waited_for_window = True
            time.sleep(0.5)
            continue

        if waited_for_window:
            # Window was just created, give the UI time to load before typing
            time.sleep(load_delay)
            waited_for_window = False

        try:
            if window.isMinimized:
                window.restore()
            window.activate()
        except Exception:
            # Windows can block SetForegroundWindow, pressing alt releases the foreground lock
            pyautogui.press('alt')

        time.sleep(0.5)
        if is_focused():
            return True

    return False

def send_message(receiver, message):
    if not focus_window():
        print('WhatsApp window could not be focused, message not sent.')
        return False

    time.sleep(1)
    pyautogui.hotkey('ctrl', 'f')
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.write(receiver)
    time.sleep(0.7)
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('enter')
    time.sleep(1)
    lines = message.split('\n')
    for i, line in enumerate(lines):
        pyautogui.write(line)
        if i < len(lines) - 1:
            pyautogui.keyDown('shift')
            pyautogui.press('enter')
            pyautogui.keyUp('shift')
    pyautogui.press('enter')
    return True

def attach_image(path, message):
    time.sleep(3)
    pyautogui.keyDown('ctrl')
    pyautogui.keyDown('f')
    pyautogui.keyUp('ctrl')
    pyautogui.keyUp('f')
    pyautogui.write(receiver)
    pyautogui.press('tab')
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.write(message)
