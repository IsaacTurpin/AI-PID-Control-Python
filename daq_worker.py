from PyQt5.QtCore import QThread, pyqtSignal
import nidaqmx
from nidaqmx.constants import TerminalConfiguration, AcquisitionType
import time

class DAQWorker(QThread):
    # Signal to send the measured voltage to the GUI
    voltage_measured = pyqtSignal(float)

    def __init__(self, input_channel: str, sampling_rate: int):
        super().__init__()
        self.input_channel = input_channel
        self.sampling_rate = sampling_rate
        self.running = False

    def run(self):
        """Main loop to read voltage from the DAQ device."""
        self.running = True

        # Configure the task for continuous sampling
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(self.input_channel, terminal_config=TerminalConfiguration.RSE)
            task.timing.cfg_samp_clk_timing(
                rate=self.sampling_rate,  # Set the sampling rate
                sample_mode=AcquisitionType.CONTINUOUS,  # Continuous sampling
                samps_per_chan=1024  # Buffer size
            )

            # Main loop for continuous reading
            while self.running:
                try:
                    # Read a single sample
                    voltage = task.read(number_of_samples_per_channel=1)
                    self.voltage_measured.emit(voltage[0])  # Emit the measured voltage
                except Exception as e:
                    print(f"Error reading from DAQ: {e}")
                    self.running = False

                # Sleep to respect the sampling rate
                time.sleep(1.0 / self.sampling_rate)

    def stop(self):
        """Stop the worker thread."""
        self.running = False