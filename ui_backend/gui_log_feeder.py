from pathlib import Path

from PySide6.QtCore import QObject, QTimer, Signal
import re


class LogFeeder(QObject):

    current_file_changed = Signal(str)
    sync_phase_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.current_phase = None

        self.log_path = (
            Path.home()
            / ".local"
            / "state"
            / "icloud-linux"
            / "icloud.log"
        )

        self.file_position = 0

        if self.log_path.exists():
            self.file_position = (self.log_path.stat().st_size)

        self.log_timer = QTimer()

        self.log_timer.timeout.connect(self.check_log)

        self.log_timer.start(500)


    def check_log(self):

        if not self.log_path.exists():
            return

        current_size = (self.log_path.stat().st_size)

        # Log was cleared or recreated
        if current_size < self.file_position:
            self.file_position = 0

        with open(self.log_path, "rb") as log_file:

            log_file.seek(self.file_position)

            new_data = log_file.read()

            self.file_position = (log_file.tell())

        if not new_data:
            return

        new_text = new_data.decode("utf-8", errors="replace")

        for line in new_text.splitlines():

            sync_phase = self.extract_sync_phase(line)

            if sync_phase is not None and sync_phase != self.current_phase:
                self.current_phase = sync_phase
                self.sync_phase_changed.emit(sync_phase)

            current_file = self.extract_sync_file(line)

            if current_file is not None:
                self.current_file_changed.emit(current_file)

    def extract_sync_phase(self, line):

        if "Remote metadata crawl progress:" in line:

            match = re.search(r"Remote metadata crawl progress:\s*(\d+)\s+folders scanned", line)

            if match:
                folders_scanned = match.group(1)

                return f"Scanning iCloud... {folders_scanned} folders scanned"

            return "Scanning iCloud..."

        if "hydrate-start" in line:
            return "Hydrating..."

        if "file-sync-start" in line:
            return "Syncing..."

        return None

    def extract_sync_file(self, line):

        if "file-sync-start" not in line and "hydrate-start" not in line:
            return None

        path_marker = "path='"

        if path_marker not in line:
            return None

        path_section = line.split(path_marker, 1)[1]

        file_path = path_section.split("'", 1)[0]

        file_path = file_path.removeprefix("/")

        return file_path

    def shutdown(self):

        if self.log_timer.isActive():
            self.log_timer.stop()