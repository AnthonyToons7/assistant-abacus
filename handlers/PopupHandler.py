import os
import tkinter as tk
from PIL import Image, ImageTk

class Window:
    def __init__(self, master):
        self.root = master
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self.disable_event)

        self.label = tk.Label(self.root, text="Heyo", font=("Arial", 24))
        self.label.pack()

        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = screen_width - width + 20
        y = screen_height - height + 50
        self.root.geometry(f"+{x}+{y}")

    def disable_event(self):
        pass

    def hide(self):
        self.root.destroy()

class SpeakNowWindow:
    def __init__(self, master):
        self.root = master
        self.root.overrideredirect(True)      # remove title bar
        self.root.attributes("-topmost", True)  # always on top
        self.root.protocol("WM_DELETE_WINDOW", self.disable_event)

        # Display text
        self.label = tk.Label(self.root, text="Speak now!", font=("Arial", 18), bg="yellow")
        self.label.pack(padx=10, pady=5)

        # Bottom-right corner
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = screen_width - width - 20
        y = screen_height - height - 50
        self.root.geometry(f"+{x}+{y}")

    def disable_event(self):
        pass  # prevent closing manually

    def hide(self):
        self.root.destroy()
