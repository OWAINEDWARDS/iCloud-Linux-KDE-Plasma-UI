from PySide6.QtCore import QProcess, QTimer
from ui_utils import update_status

class ServiceManager:

    def __init__(self, app_tray, app_actions):
        self.app_tray = app_tray
        self.app_actions = app_actions

        self.service_process = QProcess()

        # None, "start", "stop", or "restart"
        self.current_operation_state = None


    def is_busy(self):
        return(self.service_process.state() != QProcess.ProcessState.NotRunning)
    
        
    def run_service_command(self, command):
        
        self.current_operation_state = command 

        self.service_process.start("systemctl", ["--user", command, "icloud.service"],)

        self.service_process.finished.connect(self._service_command_finished)

        self.service_process.errorOccurred.connect(self._service_process_error)

        self.tell_gui_state(command)

    def tell_gui_state(self, command):

        if command == "start":
            message = "starting..."
        elif command == "stop":
            message = "Stopping..."
        elif command == "restart":
            message = "restarting..."
        else:
            return

        self.app_actions.status.setText(f"Status: {message}")
        self.app_tray.setToolTip(f"iCloud Linux - {message}")

    def _service_command_finished(self, exit_code, exit_status): #exit_code is 0 on finish
        operation_state = self.current_operation_state
        if exit_code == 0: #if finished
            if operation_state == "start":
                message = "Started successfully."
            elif operation_state == "stop":
                message = "Stopped successfully."
            elif operation_state == "restart":
                message = "Restarted successfully."
            else:
                message = "Service command completed successfully."
        else:
            self.app_tray.showMessage("iCloud Linux", f"{operation_state} failed." f"with exit code {exit_code}")
        
        operation_state = None
        update_status(self, self.app_actions, self.app_tray)

    def _service_process_error():
        self.app_tray.showMessage("iCloud Linux", f"{self.current_operation_state} failed to run." )
        update_status(self.app_actions, self.app_tray)



        