from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QProcess, QTimer
from pathlib import Path

from ui_utils import update_status
class SyncManager:
    def __init__(self, service_manager: ServiceManager, app_tray: QSystemTrayIcon, app_actions: TrayActions):
 
        self.sync_process = QProcess()
        self.app_actions = app_actions
        self.app_tray = app_tray
        self.sync_process.finished.connect(self.sync_finished)

    def run_sync(self):
        self.app_actions.sync.setEnabled(False) #stop muti sync Processes by disabling button after 1 press. 
        self.app_actions.status.setText("Status: Syncing...")
        self.app_tray.setToolTip("iCloud Linux — Syncing")

        REPO_DIR = Path(__file__).resolve().parent.parent
        ICLOUDCTL = REPO_DIR / "icloudctl"

        self.sync_process.setWorkingDirectory(str(REPO_DIR))

        self.sync_process.start(str(ICLOUDCTL), ["sync"], )

    def sync_finished(self, exit_code, exit_status):
        if exit_code == 0:
            self.app_tray.showMessage(
                "iCloud Linux",
                "Sync completed successfully.",
            )
        else:
            self.app_tray.showMessage(
                "iCloud Linux",
                f"Sync failed with exit code {exit_code}.",
            )

        update_status(self.app_actions, self.app_tray)


                