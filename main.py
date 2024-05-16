import sys
import subprocess
import serial.tools.list_ports
import time
from PySide6.QtCore import QRegularExpression, QUrl, QTimer
from PySide6.QtGui import QRegularExpressionValidator, QColor, QDesktopServices
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLineEdit, QComboBox, QLabel, QHBoxLayout, QTextEdit
from PySide6.QtGui import QIcon


meshTw_url = "https://meshtastic.org/e/#CgUSAQEoAQo3EiCKwOEes2kk-UZfcYEkFfqSO4rspA2nhnQzs5MOmdfk3hoGTWVzaFRXJQEAAAAoATABOgIIEAo2EiDLUdyJWCmXkfOHTkolR7-6ZZQfxeEbdSNHWu9kd9QcVRoKU2lnbmFsVGVzdCgBMAE6AgggCjYSIMto53_On06X_-ABQH_pgsG80aMaQldD_dHaiaNPsP0mGgpFbWVyZ2VuY3khKAEwAToCCCASDggBOAhAA0gBUBFYEGgB"

class MeshtasticConfigurator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

class MeshtasticConfigurator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Meshtastic OneShot Configurator')
        self.setGeometry(100, 100, 320, 400)
        widget = QWidget()
        layout = QVBoxLayout()

        port_layout = QHBoxLayout()
        self.combo_ports = QComboBox()
        port_layout.addWidget(QLabel("Select COM Port:"))
        port_layout.addWidget(self.combo_ports)
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.refresh_ports)
        port_layout.addWidget(btn_refresh)
        layout.addLayout(port_layout)

        # 載入圖標並設置
        self.setWindowIcon(QIcon('./icon.ico'))

        # Connect the signal to check_version
        self.combo_ports.currentIndexChanged.connect(self.check_version)

        self.refresh_ports()

        self.long_name_input = QLineEdit("OneShot Configurator")
        self.short_name_input = QLineEdit("BCMI")
        layout.addWidget(QLabel("Enter Long Name:"))
        layout.addWidget(self.long_name_input)
        layout.addWidget(QLabel("Enter Short Name:"))
        layout.addWidget(self.short_name_input)

        self.short_name_input.setMaxLength(4)
        regex = QRegularExpression("[A-Za-z]{0,4}")
        validator = QRegularExpressionValidator(regex)
        self.short_name_input.setValidator(validator)

        btn_set = QPushButton("Set")
        btn_set.clicked.connect(self.set_config)
        btn_default = QPushButton("Default")
        btn_default.clicked.connect(self.load_default)
        layout.addWidget(btn_set)
        layout.addWidget(btn_default)

        link = QLabel('<a href="https://github.com/Oliver0804">Visit GitHub</a>')
        link.setOpenExternalLinks(True)
        layout.addWidget(link)

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        layout.addWidget(QLabel("Device Status:"))
        layout.addWidget(self.status_text)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def refresh_ports(self):
        self.combo_ports.clear()
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        self.combo_ports.addItems(port_list)
        if not port_list:
            self.combo_ports.addItem("No available ports")

    def set_config(self):
        long_name = self.long_name_input.text()
        short_name = self.short_name_input.text()
        selected_port = self.combo_ports.currentText()
        command = [
            'meshtastic',
            '--set-owner', long_name,
            '--set-owner-short', short_name,
            '--set-ham', short_name,
            '--set', 'lora.region', 'TW',
            '--set', 'mqtt.enabled', 'true',
            '--set', 'mqtt.proxy_to_client_enabled', 'true',
            '--set', 'mqtt.map_reporting_enabled', 'true',
            '--port', selected_port,
            '--set', 'lora.txPower', '20',
            '--seturl', meshTw_url

        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            self.status_text.setTextColor(QColor("green"))
            self.status_text.setText(f"Successfully set names and port: {long_name}, {short_name}, {selected_port}\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            self.status_text.setTextColor(QColor("red"))
            self.status_text.setText(f"An error occurred: {e}\nFailed command: {' '.join(command)}")
        time.sleep(3)
        command = [
            'meshtastic',
            '--port', selected_port,
            '--seturl', meshTw_url
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            self.status_text.setTextColor(QColor("green"))
            self.status_text.setText(f"Successfully set names and port: {long_name}, {short_name}, {selected_port}\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            self.status_text.setTextColor(QColor("red"))
            self.status_text.setText(f"An error occurred: {e}\nFailed command: {' '.join(command)}")


    def load_default(self):
        self.long_name_input.setText("OneShot Configurator")
        self.short_name_input.setText("BCMI")
        print("Loaded default configuration.")

    def check_version(self):
        selected_port = self.combo_ports.currentText()
        command = ['meshtastic', '--port', selected_port, '--ver']
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=0.2)
            self.status_text.setTextColor(QColor("green"))
            self.status_text.setText(result.stdout)
        except subprocess.TimeoutExpired:
            self.status_text.setTextColor(QColor("red"))
            self.status_text.setText("No response from device")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./icon.png'))  # Optionally set the app icon

    ex = MeshtasticConfigurator()
    ex.show()
    sys.exit(app.exec())
