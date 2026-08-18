from pathlib import Path

from PySide6.QtCore import QObject, QProcess, QTimer, Signal


class SyncManager(QObject):

    sync_state_changed = Signal(str)
    sync_command_finished = Signal(bool, str)

    def __init__(self):
        super().__init__()

        self.sync_process = QProcess()

        self.sync_process.finished.connect(self.sync_finished)
        self.sync_process.errorOccurred.connect(self.sync_process_error)
        self.cancel_requested = False
        self.cancel_timer = QTimer()
        self.cancel_timer.setSingleShot(True)
        self.cancel_timer.timeout.connect(self._force_cancel_sync)

    def is_busy(self):
        return(self.sync_process.state() != QProcess.ProcessState.NotRunning)


    def run_sync(self):

        print("SyncManager.run_sync() called")

        if self.is_busy():
            print("SyncManager is already busy")
            return

        self.cancel_requested = False
        self.cancel_timer.stop()

        print("Starting new sync")

        self.sync_state_changed.emit("Syncing...")

        REPO_DIR = Path(__file__).resolve().parent.parent
        ICLOUDCTL = REPO_DIR / "icloudctl"

        print(f"REPO_DIR: {REPO_DIR}")
        print(f"ICLOUDCTL: {ICLOUDCTL}")
        print(f"icloudctl exists: {ICLOUDCTL.exists()}")

        self.sync_process.setWorkingDirectory(str(REPO_DIR))
        self.sync_process.start(str(ICLOUDCTL), ["sync"])


    def cancel_sync(self):

        if not self.is_busy():
            print("No active sync to cancel")
            return

        self.cancel_requested = True

        print("Cancelling active sync...")

        self.sync_state_changed.emit("Cancelling...")
        self.sync_process.terminate()
        self.cancel_timer.start(2000)


    def _force_cancel_sync(self):

        if not self.is_busy():
            return

        print("Sync did not terminate normally. Killing it...")

        self.sync_process.kill()


    def sync_finished(self, exit_code, exit_status):

        self.cancel_timer.stop()

        if self.cancel_requested:
            success = False
            message = "Sync cancelled."

        elif exit_code == 0:
            success = True
            message = "Sync completed successfully."

        else:
            success = False

            error_text = self.sync_process.readAllStandardError().data().decode().strip()

            if error_text:
                message = error_text

            else:
                message = f"Sync failed with exit code {exit_code}."

        self.cancel_requested = False
        self.sync_command_finished.emit(success, message)


    def sync_process_error(self, error):

        if self.cancel_requested and error == QProcess.ProcessError.Crashed:
            return

        self.cancel_timer.stop()
        message = f"Sync failed to run. {self.sync_process.errorString()}"
        self.cancel_requested = False
        self.sync_command_finished.emit(False, message)


    def shutdown(self):

        self.cancel_timer.stop()

        if self.sync_process.state() != QProcess.ProcessState.NotRunning:

            self.sync_process.terminate()

            if not self.sync_process.waitForFinished(2000):

                self.sync_process.kill()
                self.sync_process.waitForFinished(1000)