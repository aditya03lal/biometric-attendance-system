# main.py
import tkinter as tk
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from gui import App
from db import initialize

def main():
    initialize()
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()