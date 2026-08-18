from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QCursor, QGuiApplication
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

class TrayMainPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("iCloud Linux")

        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setFixedWidth(320)

        self.status_label = QLabel("Status: Checking...")
        self.current_file_label = QLabel("Current: —")

        self.sync_button = QPushButton("Sync Now")
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.restart_button = QPushButton("Restart")

        service_buttons = QHBoxLayout()
        service_buttons.addWidget(self.start_button)
        service_buttons.addWidget(self.stop_button)
        service_buttons.addWidget(self.restart_button)

        content_layout = QVBoxLayout()
        content_layout.addWidget(self.status_label)
        content_layout.addWidget(self.current_file_label)
        content_layout.addWidget(self.sync_button)
        content_layout.addLayout(service_buttons)

        self.card = QFrame()
        self.card.setObjectName("popoverCard")
        self.card.setLayout(content_layout)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.card)

        self.setStyleSheet("""
            QFrame#popoverCard {
                background-color: palette(window);
                border: 1px solid palette(mid);
                border-radius: 12px;
                padding: 10px;
            }
        """)

    def show_near_cursor(self):
        self.adjustSize()

        cursor_position = QCursor.pos()

        screen = QGuiApplication.screenAt(cursor_position)

        if screen is None:
            screen = QGuiApplication.primaryScreen()

        screen_area = screen.availableGeometry()

        x = cursor_position.x() - self.width() // 2
        y = cursor_position.y() - self.height() - 12

        if y < screen_area.top():
            y = cursor_position.y() + 12

        x = max(
            screen_area.left() + 8,
            min(
                x,
                screen_area.right() - self.width() - 8,
            ),
        )

        y = max(
            screen_area.top() + 8,
            min(
                y,
                screen_area.bottom() - self.height() - 8,
            ),
        )

        self.move(x, y)

        self.show()
        self.raise_()
        self.activateWindow()

    def event(self, event):
        if event.type() == QEvent.Type.WindowDeactivate:
            self.hide()

        return super().event(event)