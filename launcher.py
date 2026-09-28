"""
launcher.py - Entry point cho Mini Desktop Launcher của Aura AI Logo Generator.
"""
import os
import sys
import multiprocessing
import tkinter as tk

from launcher_core.single_instance import ensure_single_instance
from launcher_core.server_runner import wait_for_server
from launcher_core.launcher_gui import AuraLauncherApp

multiprocessing.freeze_support()
_app_mutex = ensure_single_instance()

if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(APP_DIR)


def main():
    app_root = tk.Tk()
    app = AuraLauncherApp(app_root, APP_DIR)
    app_root.mainloop()


if __name__ == "__main__":
    main()
