import subprocess

def update_status(service_manager: ServiceManager, app_actions: TrayActions, app_tray: QSystemTrayIcon):
    
    if _is_icloud_linux_running() and not service_manager.is_busy():
        app_actions.status.setText("Status: Running")
        app_tray.setToolTip("iCloud Linux — Running")

        app_actions.start.setEnabled(False)
        app_actions.stop.setEnabled(True)
        app_actions.restart.setEnabled(True)
        app_actions.sync.setEnabled(True)

    else:
        app_actions.status.setText(" ~ Status: Stopped ~")
        app_tray.setToolTip("iCloud Linux — Stopped")

        app_actions.start.setEnabled(True)
        app_actions.stop.setEnabled(False)
        app_actions.restart.setEnabled(False)
        app_actions.sync.setEnabled(False)

def _is_icloud_linux_running():
    # systemctl --user is-active icloud.service
    result = subprocess.run( ["systemctl", "--user", "is-active", "icloud.service"], capture_output=True, text=True)
    return result.stdout.strip() == "active"
