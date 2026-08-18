import os
import shlex

from pathlib import Path

import yaml


class ConfigManager:

    def __init__(self):

        self.config_path = Path.home() / ".config" / "icloud-linux" / "config.yaml"
        self.env_path = Path.home() / ".config" / "icloud-linux" / "icloud.env"


    def get_mount_path(self):

        if not self.env_path.exists():
            return Path.home() / "iCloud"

        with open(self.env_path, "r", encoding="utf-8") as env_file:

            for line in env_file:

                if not line.startswith("ICLOUD_MOUNT="):
                    continue

                value = line.split("=", 1)[1].strip()
                parsed_value = shlex.split(value)

                if parsed_value:
                    return Path(parsed_value[0])

        return Path.home() / "iCloud"


    def get_root_folders(self):

        mount_path = self.get_mount_path()

        if not mount_path.exists():
            return []

        folders = []

        for item in mount_path.iterdir():

            if item.is_dir():
                folders.append(item.name)

        return sorted(folders, key=str.casefold)


    def get_sync_paths(self):

        if not self.config_path.exists():
            return []

        with open(self.config_path, "r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file) or {}

        sync_paths = config.get("sync_paths")

        if not sync_paths:
            return self.get_root_folders()

        return [path.removeprefix("/") for path in sync_paths]


    def set_sync_paths(self, folder_names):

        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file does not exist: {self.config_path}")

        if not isinstance(folder_names, list):
            raise TypeError("Folder selection must be a list.")

        if not folder_names:
            raise ValueError("At least one iCloud folder must be selected.")

        root_folders = set(self.get_root_folders())

        selected_folders = []

        for folder_name in folder_names:

            if not isinstance(folder_name, str):
                raise TypeError("Folder names must be strings.")

            if folder_name not in root_folders:
                raise ValueError(f"Folder is not an iCloud root directory: {folder_name}")

            if folder_name not in selected_folders:
                selected_folders.append(folder_name)

        with open(self.config_path, "r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file) or {}

        if set(selected_folders) == root_folders:
            config["sync_paths"] = None

        else:
            config["sync_paths"] = [f"/{folder_name}" for folder_name in selected_folders]

        temporary_path = self.config_path.with_suffix(".yaml.tmp")

        with open(temporary_path, "w", encoding="utf-8") as config_file:
            yaml.safe_dump(config, config_file, sort_keys=False)

        os.chmod(temporary_path, 0o600)

        os.replace(temporary_path, self.config_path)