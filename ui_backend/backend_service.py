import sys
from .service_manager import ServiceManager
from PySide6.QtCore import (
    QCoreApplication,
    QObject,
    Signal,
    Slot,
    ClassInfo,
)

from PySide6.QtDBus import QDBusConnection

from .service_manager import ServiceManager
from .sync_manager import SyncManager
from .gui_log_feeder import LogFeeder
from .config_manager import ConfigManager

SERVICE_NAME = "org.iCloudLinux"
OBJECT_PATH = "/Backend"
INTERFACE_NAME = "org.iCloudLinux.Backend"

@ClassInfo({"D-Bus Interface": INTERFACE_NAME})
class BackendService(QObject):
    state_changed = Signal(str, bool, str, str)
    folders_changed = Signal("QStringList", "QStringList")
    
    def __init__(self):
        super().__init__()

        self.service_manager = ServiceManager()
        self.sync_manager = SyncManager()
        self.gui_log_feeder = LogFeeder()
        self.config_manager = ConfigManager()

        self._status = (self.service_manager.get_service_status())

        self._sync_phase = "Idle"
        self._syncing = False
        self._current_file = "—"

        self.service_manager.service_state_changed.connect(self._service_state_changed)
        self.service_manager.service_command_finished.connect(self._service_command_finished)

        self.sync_manager.sync_state_changed.connect(self._sync_state_changed)
        self.sync_manager.sync_command_finished.connect(self._sync_command_finished)

        self.gui_log_feeder.current_file_changed.connect(self._current_file_changed)
        self.gui_log_feeder.sync_phase_changed.connect(self._sync_phase_changed)

    @Slot(result=str)
    def Ping(self):
        return "pong"

    @Slot(result=str)
    def GetStatus(self):
        self._status = (self.service_manager.get_service_status())
        return self._status

    @Slot(result=bool)
    def IsSyncing(self):
        return self._syncing

    @Slot(result=str)
    def GetCurrentFile(self):
        return self._current_file

    @Slot()
    def Start(self):
        self.service_manager.run_service_command("start")

    @Slot()
    def Stop(self):

        if self.sync_manager.is_busy():
            self.sync_manager.cancel_sync()

        self.service_manager.run_service_command("stop")

    @Slot()
    def Restart(self):

        if self.sync_manager.is_busy():
            self.sync_manager.cancel_sync()

        self.service_manager.run_service_command("restart")

    @Slot()
    def Sync(self):
        print("BackendService.Sync() called")
        self.sync_manager.run_sync()

    @Slot(result=str)
    def GetSyncPhase(self):
        return self._sync_phase

    @Slot(result="QStringList")
    def GetRootFolders(self):

        return self.config_manager.get_root_folders()


    @Slot(result="QStringList")
    def GetSyncPaths(self):

        return self.config_manager.get_sync_paths()


    @Slot()
    def RefreshFolders(self):

        self._emit_folders()


    @Slot("QStringList", result=str)
    def SetSyncPaths(self, folder_names):

        if self.sync_manager.is_busy():
            return "ERROR: Cannot change sync folders while a sync is running."

        if self.service_manager.is_busy():
            return "ERROR: The iCloud service is currently changing state."

        try:
            self.config_manager.set_sync_paths(folder_names)

        except Exception as error:
            return f"ERROR: {error}"

        self._emit_folders()

        if self.service_manager.get_service_status() == "Running":
            self.service_manager.run_service_command("restart")

            return "Saved. Restarting iCloud service..."

        return "Saved. Changes will apply when the service starts."

    def _emit_folders(self):

        root_folders = self.config_manager.get_root_folders()
        sync_folders = self.config_manager.get_sync_paths()

        self.folders_changed.emit(root_folders, sync_folders)

        print(f"Folders changed: available={root_folders}, selected={sync_folders}")

    def _service_state_changed(self, state):

        self._status = state
        self._emit_state()


    def _service_command_finished(self, operation, success, message):

        self._status = self.service_manager.get_service_status()

        print(message)
        print(f"Service command finished: operation={operation}, success={success}, status={self._status}")

        self._emit_state()

    def _current_file_changed(self, current_file):

        self._current_file = current_file

        print(f"Current sync file: {current_file}")

        self._emit_state()

    def shutdown(self):

        print("Shutting down iCloud Linux backend...")

        self.gui_log_feeder.shutdown()
        self.sync_manager.shutdown()
        self.service_manager.shutdown()

    def _sync_state_changed(self, state):

        if state == "Syncing...":
            self._syncing = True
            self._sync_phase = "Starting..."
            self._current_file = "—"

        elif state == "Cancelling...":
            self._sync_phase = "Cancelling..."

        print(f"Sync state: {state}")

        self._emit_state()

    def _sync_phase_changed(self, phase):

        self._sync_phase = phase

        print(f"Sync phase: {phase}")

        self._emit_state()

    def _sync_command_finished(self, success, message):

        self._syncing = False
        self._sync_phase = "Idle"
        self._current_file = "—"

        print(message)

        self._emit_state()

    def _sync_command_finished(self, success, message):

        self._syncing = False
        self._current_file = "—"

        print(message)

        self._emit_state()

    def _emit_state(self):

        self.state_changed.emit(self._status, self._syncing, self._current_file, self._sync_phase)

        print(f"State changed: status={self._status}, syncing={self._syncing}, file={self._current_file}, phase={self._sync_phase}")
            

def main():
    app = QCoreApplication(sys.argv)

    bus = QDBusConnection.sessionBus()

    if not bus.isConnected():
        raise RuntimeError("Could not connect to the D-Bus session bus.")

    if not bus.registerService(SERVICE_NAME):
        raise RuntimeError("Could not register D-Bus service: " + bus.lastError().message())

    backend = BackendService()
    app.aboutToQuit.connect(backend.shutdown)

    options = (
        QDBusConnection.RegisterOption.ExportAllSlots
        | QDBusConnection.RegisterOption.ExportAllSignals
    )

    if not bus.registerObject(OBJECT_PATH, backend, options,):
        raise RuntimeError("Could not register D-Bus object: " + bus.lastError().message())

    print("iCloud Linux backend running")
    print(f"Service:   {SERVICE_NAME}")
    print(f"Object:    {OBJECT_PATH}")
    print(f"Interface: {INTERFACE_NAME}")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()