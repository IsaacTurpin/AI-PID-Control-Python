import sys
from PyQt5.QtWidgets import QApplication
from gui import PIDControllerGUI
from daq_interface import DAQInterface

class PIDControllerApp:
    def __init__(self):
        self.gui = PIDControllerGUI()
        self.daq = DAQInterface()

        # Populate DAQ device and channel dropdowns
        self.populate_daq_options()

    def populate_daq_options(self):
        devices = self.daq.get_available_devices()
        self.gui.daq_device_dropdown.addItems(devices)
        if devices:
            self.update_channel_options(devices[0])

    def update_channel_options(self, device_name):
        input_channels = self.daq.get_available_channels(device_name, "ai")
        output_channels = self.daq.get_available_channels(device_name, "ao")
        self.gui.input_channel_dropdown.clear()
        self.gui.output_channel_dropdown.clear()
        self.gui.input_channel_dropdown.addItems(input_channels)
        self.gui.output_channel_dropdown.addItems(output_channels)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pid_app = PIDControllerApp()
    pid_app.gui.show()
    sys.exit(app.exec_())
