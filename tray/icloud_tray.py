import subprocess
import sys

from PySide6.QtCore import QProcess, QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from pathlib import Path
from tray_app import TrayApp

tray_app_gui = TrayApp()
tray_app_gui.start()





