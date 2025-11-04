import pywhatkit
import time
import pyautogui

def send_message(receiver, message):
    time.sleep(3)
    pyautogui.keyDown('ctrl')
    pyautogui.keyDown('k')
    pyautogui.keyDown('o')
    pyautogui.keyUp('ctrl')
    pyautogui.keyUp('k')
    pyautogui.keyUp('o')
    pyautogui.write(receiver)
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.write(message)
    # pyautogui.press('enter')

def attach_image(path, message):
    time.sleep(3)
    pyautogui.keyDown('ctrl')
    pyautogui.keyDown('k')
    pyautogui.keyDown('o')
    pyautogui.keyUp('ctrl')
    pyautogui.keyUp('k')
    pyautogui.keyUp('o')
    pyautogui.write(receiver)
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.write(message)
    # pyautogui.press('enter')