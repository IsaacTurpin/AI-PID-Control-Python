from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel, QLineEdit, QPushButton, QComboBox
from PyQt5.QtCore import Qt
from daq_worker import DAQWorker
from daq_interface import DAQInterface

class PIDControllerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced PID Controller")
        self.setGeometry(100, 100, 600, 400)

        # Main layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Desired Voltage Slider
        self.desired_voltage_label = QLabel("Desired Voltage (V): 0.0")
        self.layout.addWidget(self.desired_voltage_label)
        self.desired_voltage_slider = QSlider(Qt.Horizontal)
        self.desired_voltage_slider.setRange(0, 10)  # 0V to 10V range
        self.desired_voltage_slider.valueChanged[int].connect(self.update_desired_voltage)
        self.layout.addWidget(self.desired_voltage_slider)

        # Sampling Rate Input
        self.sampling_rate_label = QLabel("Sampling Rate (Hz):")
        self.layout.addWidget(self.sampling_rate_label)
        self.sampling_rate_input = QLineEdit("100")  # Default sampling rate
        self.layout.addWidget(self.sampling_rate_input)

        # DAQ Device Selection
        self.daq_device_label = QLabel("Select DAQ Device:")
        self.layout.addWidget(self.daq_device_label)
        self.daq_device_dropdown = QComboBox()
        self.layout.addWidget(self.daq_device_dropdown)

        # Input/Output Channel Selection
        self.input_channel_label = QLabel("Select Input Channel:")
        self.layout.addWidget(self.input_channel_label)
        self.input_channel_dropdown = QComboBox()
        self.layout.addWidget(self.input_channel_dropdown)

        self.output_channel_label = QLabel("Select Output Channel:")
        self.layout.addWidget(self.output_channel_label)
        self.output_channel_dropdown = QComboBox()
        self.layout.addWidget(self.output_channel_dropdown)

        # Current Voltage Indicators
        self.current_input_voltage_label = QLabel("Current Input Voltage (V): 0.0")
        self.layout.addWidget(self.current_input_voltage_label)
        self.current_output_voltage_label = QLabel("Current Output Voltage (V): 0.0")
        self.layout.addWidget(self.current_output_voltage_label)

        # Start/Stop Buttons
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_daq)
        self.layout.addWidget(self.start_button)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_daq)
        self.layout.addWidget(self.stop_button)

        # DAQ Interface
        self.daq_interface = DAQInterface()

        # Initialize DAQ device and channel dropdowns
        self.populate_daq_devices()
        self.daq_device_dropdown.currentTextChanged.connect(self.update_channel_dropdowns)

        # DAQ Worker
        self.daq_worker = None

    def populate_daq_devices(self):
        """Populate the DAQ device dropdown with available devices."""
        devices = self.daq_interface.get_available_devices()
        self.daq_device_dropdown.clear()
        self.daq_device_dropdown.addItems(devices)
        if devices:
            self.update_channel_dropdowns(devices[0])  # Update channels for the first device

    def update_channel_dropdowns(self, device_name: str):
        """Update the input and output channel dropdowns for the selected device."""
        if device_name:
            # Update input channels
            input_channels = self.daq_interface.get_available_channels(device_name, "ai")
            self.input_channel_dropdown.clear()
            self.input_channel_dropdown.addItems(input_channels)

            # Update output channels
            output_channels = self.daq_interface.get_available_channels(device_name, "ao")
            self.output_channel_dropdown.clear()
            self.output_channel_dropdown.addItems(output_channels)

    def update_desired_voltage(self, value: int):
        """Slot for updating the desired voltage label."""
        desired_voltage = value  # No division needed since the slider range is already 0-10
        self.desired_voltage_label.setText(f"Desired Voltage (V): {desired_voltage:.1f}")

    def start_daq(self):
        """Start the DAQ worker thread."""
        if self.daq_worker is None or not self.daq_worker.isRunning():
            input_channel = self.input_channel_dropdown.currentText()
            sampling_rate = int(self.sampling_rate_input.text())
            if input_channel and sampling_rate > 0:
                self.daq_worker = DAQWorker(input_channel, sampling_rate)
                self.daq_worker.voltage_measured.connect(self.update_input_voltage)
                self.daq_worker.start()

    def stop_daq(self):
        """Stop the DAQ worker thread."""
        if self.daq_worker is not None and self.daq_worker.isRunning():
            self.daq_worker.stop()
            self.daq_worker.quit()
            self.daq_worker.wait()

    def update_input_voltage(self, voltage: float):
        """Update the current input voltage label."""
        self.current_input_voltage_label.setText(f"Current Input Voltage (V): {voltage:.3f}")

if __name__ == "__main__":
    app = QApplication([])
    window = PIDControllerGUI()
    window.show()
    app.exec_()