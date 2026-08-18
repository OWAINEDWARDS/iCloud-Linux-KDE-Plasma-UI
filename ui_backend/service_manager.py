import subprocess

from PySide6.QtCore import QObject, QProcess, Signal


class ServiceManager(QObject):

    service_state_changed = Signal(str)
    service_command_finished = Signal(str, bool, str)


    def __init__(self):
        super().__init__()

        self.service_process = QProcess()

        self.current_operation_state = None

        self.service_process.finished.connect(self._service_command_finished)
        self.service_process.errorOccurred.connect(self._service_process_error)


    def is_busy(self):
        return(self.service_process.state() != QProcess.ProcessState.NotRunning)


    def run_service_command(self, command):

        if self.is_busy():
            return

        self.current_operation_state = command

        self.tell_backend_state(command)

        self.service_process.start("systemctl", ["--user", command, "icloud.service"])


    def tell_backend_state(self, command):

        if command == "start":
            state = "Starting..."

        elif command == "stop":
            state = "Stopping..."

        elif command == "restart":
            state = "Restarting..."

        else:
            state = "Unknown"

        self.service_state_changed.emit(state)


    def get_service_status(self):

        result = subprocess.run(["systemctl", "--user", "is-active", "icloud.service"], capture_output=True, text=True)

        service_state = result.stdout.strip()

        if service_state == "active":
            return "Running"

        elif service_state == "inactive":
            return "Stopped"

        elif service_state == "activating":
            return "Starting..."

        elif service_state == "deactivating":
            return "Stopping..."

        elif service_state == "failed":
            return "Failed"

        else:
            return "Unknown"


    def _service_command_finished(self, exit_code, exit_status):

        operation = self.current_operation_state

        if exit_code == 0:
            success = True
            message = f"Service {operation} completed successfully."

        else:
            success = False

            error_text = self.service_process.readAllStandardError().data().decode().strip()

            if error_text:
                message = error_text

            else:
                message = f"Service {operation} failed with exit code {exit_code}."

        self.current_operation_state = None

        state = self.get_service_status()

        self.service_state_changed.emit(state)
        self.service_command_finished.emit(operation, success, message)


    def _service_process_error(self, error):

        operation = self.current_operation_state

        message = "Service command failed to run. " + self.service_process.errorString()

        self.current_operation_state = None

        state = self.get_service_status()

        self.service_state_changed.emit(state)
        self.service_command_finished.emit(operation, False, message)


    def shutdown(self):

        if self.service_process.state() != QProcess.ProcessState.NotRunning:

            self.service_process.terminate()

            if not self.service_process.waitForFinished(2000):

                self.service_process.kill()

                self.service_process.waitForFinished(1000)