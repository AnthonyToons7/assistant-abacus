import pywhatkit
import time
import pyautogui

def send_message(receiver, message):
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