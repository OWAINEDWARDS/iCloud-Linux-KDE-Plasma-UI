import sys
from dataclasses import dataclass
from PySide6.QtCore import QProcess, QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from pathlib import Path
from ui_utils import update_status
from service_manager import ServiceManager
from sync_manager import SyncManager


@dataclass
class TrayActions:
    start: QAction
    sync: QAction
    restart: QAction
    stop: QAction
    status: QAction


class TrayApp:
    def __init__(self):

        #initialise basic UI
        self.app_gui_setup()

        self.app_actions = TrayActions(
            start = self.start_action,
            sync = self.sync_action,
            restart = self.restart_action,
            stop = self.stop_action,
            status = self.status_action
        )

        self.set_action_trigger_connections()

    def start(self):

        self.tray.setContextMenu(self.menu)

        self.status_timer = QTimer()
        self.status_timer.timeout.connect(lambda: update_status(self.app_service_manager, self.app_actions, self.tray))
        self.status_timer.start(5000)#5s

        self.tray.show()
        update_status(self.app_service_manager, self.app_actions, self.tray) #initial update to test run on start. 

        sys.exit(self.app.exec())

    def app_gui_setup(self):
        #initialise basic UI
        self.app = QApplication(sys.argv)

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon.fromTheme("folder-cloud"))
        self.tray.setToolTip("iCloud Linux")

        self.menu = QMenu()

        self.status_action = QAction("Status: Checking...")
        self.status_action.setEnabled(False) # set not click-able

        self.start_action = QAction("Start Service")
        self.stop_action = QAction("Stop Service")

        self.restart_action = QAction("restart Service")
        self.sync_action = QAction("↻ Sync Now")

        self.quit_action = QAction("Quit Icloud-linux")
        self.menu.addAction(self.status_action)
        self.menu.addSeparator()

        self.menu.addAction(self.start_action)
        self.menu.addAction(self.stop_action)
        self.menu.addSeparator()

        self.menu.addAction(self.restart_action)
        self.menu.addAction(self.sync_action)
        self.menu.addSeparator()

        self.menu.addAction(self.quit_action)

       
    def set_action_trigger_connections(self):

        self.quit_action.triggered.connect(self.app.quit)

        self.app_service_manager = ServiceManager(self.tray, self.app_actions)
        self.start_action.triggered.connect(
            lambda: self.app_service_manager.run_service_command("start")
        )

        self.restart_action.triggered.connect(
            lambda: self.app_service_manager.run_service_command("restart")
        )

        self.app_sync_manager = SyncManager(self.app_service_manager, self.tray, self.app_actions)
        self.sync_action.triggered.connect(self.app_sync_manager.run_sync)

        self.stop_action.triggered.connect(
            lambda: self.app_service_manager.run_service_command("stop")
        
        )
        

