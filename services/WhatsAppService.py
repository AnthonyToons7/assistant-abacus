import time
import pyautogui

def send_message(receiver, message):
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'f')
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.write(receiver)
    time.sleep(0.7)
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
    # pyautogui.press('enter')