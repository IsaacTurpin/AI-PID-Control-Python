from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel, QLineEdit, QPushButton, QComboBox
from PyQt5.QtCore import Qt, pyqtSignal

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
        self.desired_voltage_slider.valueChanged[int].connect(self.update_desired_voltage)  # Explicitly specify signal type
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
        self.layout.addWidget(self.start_button)
        self.stop_button = QPushButton("Stop")
        self.layout.addWidget(self.stop_button)

    def update_desired_voltage(self, value: int):
        """Slot for updating the desired voltage label."""
        # Scale the slider value (0-10) to the desired voltage range (0.0V to 10.0V)
        desired_voltage = value  # No division needed since the slider range is already 0-10
        self.desired_voltage_label.setText(f"Desired Voltage (V): {desired_voltage:.1f}")

if __name__ == "__main__":
    app = QApplication([])
    window = PIDControllerGUI()
    window.show()
    app.exec_()