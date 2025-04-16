import cv2
import os
import socket
import struct
import pickle
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLineEdit, QFrame, QDockWidget,
    QRadioButton, QButtonGroup, QComboBox, QLabel, QToolBar
)
from PySide6.QtGui import QAction, QIcon, QPixmap, QImage
from PySide6.QtCore import Qt, QSize, QTimer


class StreamingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Streaming App with Toolbar")
        self.setMinimumSize(800, 600)

        # Track streaming state for local and remote
        self.is_local_streaming = False
        self.is_remote_streaming = False
        self.is_recording = False

        # Network variables
        self.network_stream_socket = None
        self.capture = None
        self.frame_counter = 0
        self.out = None  # VideoWriter object for recording

        # Create dock widgets for local and remote streams
        self.create_local_stream_dock()
        self.create_remote_stream_dock()

        # Add a toolbar on the left for general functionalities
        self.create_toolbar()

    def create_local_stream_dock(self):
        """Creates a dock widget for the local video stream and controls."""
        local_widget = QWidget()
        local_layout = QVBoxLayout(local_widget)
        local_layout.setContentsMargins(5, 5, 5, 5)
        local_layout.setSpacing(5)

        # Local video display
        self.local_video_label = QLabel()
        self.local_video_label.setStyleSheet("background-color: black;")
        self.local_video_label.setMinimumSize(320, 240)
        self.local_video_label.setScaledContents(True)

        # USB Device dropdown
        usb_label = QLabel("USB Devices:")
        self.usb_dropdown = QComboBox()
        self.usb_dropdown.addItems(["Device 0", "Device 1", "Device 2"])

        # Local stream toggle button
        self.local_stream_btn = QPushButton("Start Stream")
        self.local_stream_btn.clicked.connect(self.toggle_local_stream)

        # Layout for USB controls
        usb_layout = QHBoxLayout()
        usb_layout.addWidget(usb_label)
        usb_layout.addWidget(self.usb_dropdown)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.local_stream_btn)

        # Add all components to the local layout
        local_layout.addWidget(self.local_video_label)
        local_layout.addLayout(usb_layout)
        local_layout.addLayout(controls_layout)

        # Create the dock widget
        local_dock = QDockWidget("Local Stream", self)
        local_dock.setWidget(local_widget)
        local_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)
        self.addDockWidget(Qt.TopDockWidgetArea, local_dock)

    def create_remote_stream_dock(self):
        """Creates a dock widget for the remote video stream and controls."""
        remote_widget = QWidget()
        remote_layout = QVBoxLayout(remote_widget)
        remote_layout.setContentsMargins(5, 5, 5, 5)
        remote_layout.setSpacing(5)

        # Remote video display
        self.remote_video_label = QLabel()
        self.remote_video_label.setStyleSheet("background-color: black;")
        self.remote_video_label.setMinimumSize(320, 240)
        self.remote_video_label.setScaledContents(True)

        # Network IP Address input
        ip_label = QLabel("IP Address:")
        self.remote_ip_input = QLineEdit()
        self.remote_ip_input.setPlaceholderText("Enter server IP")

        # Remote stream toggle button
        self.remote_stream_btn = QPushButton("Start Stream")
        self.remote_stream_btn.clicked.connect(self.toggle_remote_stream)

        # Layout for Network controls
        network_layout = QHBoxLayout()
        network_layout.addWidget(ip_label)
        network_layout.addWidget(self.remote_ip_input)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.remote_stream_btn)

        # Add all components to the remote layout
        remote_layout.addWidget(self.remote_video_label)
        remote_layout.addLayout(network_layout)
        remote_layout.addLayout(controls_layout)

        # Create the dock widget
        remote_dock = QDockWidget("Remote Stream", self)
        remote_dock.setWidget(remote_widget)
        remote_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)
        self.addDockWidget(Qt.TopDockWidgetArea, remote_dock)

    def create_toolbar(self):
        """Creates a toolbar on the left side for general functionalities."""
        toolbar = QToolBar("General Controls")
        toolbar.setOrientation(Qt.Vertical)  # Make it vertical
        toolbar.setIconSize(QSize(24, 24))

        self.addToolBar(Qt.LeftToolBarArea, toolbar)

        # Add capture action
        capture_action = QAction(QIcon.fromTheme("camera-photo"), "Capture", self)
        capture_action.setToolTip("Capture a still image")
        capture_action.triggered.connect(self.capture_image)

        # Add recording toggle button
        self.record_action = QAction(QIcon.fromTheme("media-record"), "Start Recording", self)
        self.record_action.setToolTip("Start or stop recording the stream")
        self.record_action.triggered.connect(self.toggle_recording)

        # Add actions to the toolbar
        toolbar.addAction(capture_action)
        toolbar.addAction(self.record_action)

    def toggle_local_stream(self):
        """Toggles the local streaming state."""
        if self.is_local_streaming:
            self.stop_local_stream()
        else:
            self.start_usb_stream()

    def start_usb_stream(self):
        """Starts the USB stream."""
        device_index = self.usb_dropdown.currentIndex()
        self.capture = cv2.VideoCapture(device_index)

        if not self.capture.isOpened():
            print("Failed to open USB device.")
            return

        print("USB stream started")
        self.is_local_streaming = True
        self.local_stream_btn.setText("Stop Stream")

        # Start timer to update frames
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_local_frame)
        self.timer.start(30)

    def update_local_frame(self):
        """Updates the frame from the USB stream."""
        if self.capture:
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.local_video_label.setPixmap(QPixmap.fromImage(qt_image))

                # If recording, write the frame to the video file
                if self.is_recording and hasattr(self, 'out'):
                    self.out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def stop_local_stream(self):
        """Stops the local stream."""
        print("Local stream stopped")
        self.is_local_streaming = False
        self.local_stream_btn.setText("Start Stream")

        if self.capture:
            self.capture.release()
            self.capture = None

        if hasattr(self, "timer"):
            self.timer.stop()

        self.local_video_label.clear()

    def toggle_remote_stream(self):
        """Toggles the remote streaming state."""
        if self.is_remote_streaming:
            self.stop_remote_stream()
        else:
            self.start_remote_stream()

    def start_remote_stream(self):
        """Starts the remote stream."""
        ip_address = self.remote_ip_input.text().strip()
        if not ip_address:
            print("Please enter a valid IP address.")
            return

        self.network_stream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.network_stream_socket.connect((ip_address, 9999))
            print("Remote stream started")
            self.is_remote_streaming = True
            self.remote_stream_btn.setText("Stop Stream")

            # Start timer to update frames
            self.remote_timer = QTimer(self)
            self.remote_timer.timeout.connect(self.update_remote_frame)
            self.remote_timer.start(30)
        except Exception as e:
            print(f"Failed to connect to server: {e}")

    def update_remote_frame(self):
        """Updates the frame from the network stream on the remote side."""
        try:
            data = b""
            while len(data) < struct.calcsize("Q"):
                packet = self.network_stream_socket.recv(4 * 1024)
                if not packet:
                    return
                data += packet

            packed_msg_size = data[:struct.calcsize("Q")]
            data = data[struct.calcsize("Q"):]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                data += self.network_stream_socket.recv(4 * 1024)

            frame_data = data[:msg_size]
            frame = pickle.loads(frame_data)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.remote_video_label.setPixmap(QPixmap.fromImage(qt_image))
        except Exception as e:
            print(f"Error receiving remote frame: {e}")

    def stop_remote_stream(self):
        """Stops the remote stream."""
        print("Remote stream stopped")
        self.is_remote_streaming = False
        self.remote_stream_btn.setText("Start Stream")

        if self.network_stream_socket:
            self.network_stream_socket.close()
            self.network_stream_socket = None

        if hasattr(self, "remote_timer"):
            self.remote_timer.stop()

        self.remote_video_label.clear()

    def capture_image(self):
        """Captures a still image from the local video stream."""
        if self.capture and self.is_local_streaming:
            ret, frame = self.capture.read()
            if ret:
                os.makedirs("captures", exist_ok=True)
                filename = f"captures/capture_{self.frame_counter}.png"
                cv2.imwrite(filename, frame)
                print(f"Image saved: {filename}")
                self.frame_counter += 1

    def toggle_recording(self):
        """Toggles between start and stop recording."""
        if self.is_recording:
            # Stop recording
            self.is_recording = False
            self.record_action.setText("Start Recording")
            if hasattr(self, 'out'):
                self.out.release()
                print(f"Recording saved: recordings/recording_{self.frame_counter}.avi")
                self.frame_counter += 1  # Increment frame counter for the next recording
        else:
            # Start recording
            if self.capture and self.capture.isOpened():
                # Ensure the recordings directory exists
                os.makedirs("recordings", exist_ok=True)

                # Define the filename for the recording
                filename = f"recordings/recording_{self.frame_counter}.avi"

                # Initialize the VideoWriter
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                frame_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
                frame_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
                self.out = cv2.VideoWriter(filename, fourcc, 20.0, (frame_width, frame_height))

                self.record_action.setText("Stop Recording")
                self.is_recording = True
                print(f"Started recording: {filename}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StreamingApp()
    window.show()
    sys.exit(app.exec())