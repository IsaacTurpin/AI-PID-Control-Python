from PyQt5.QtCore import QThread, pyqtSignal
import nidaqmx
from nidaqmx.constants import TerminalConfiguration, AcquisitionType
import time

class DAQWorker(QThread):
    # Signal to send the measured voltage to the GUI
    voltage_measured = pyqtSignal(float)

    def __init__(self, input_channel: str, output_channel: str, sampling_rate: int):
        super().__init__()
        self.input_channel = input_channel
        self.output_channel = output_channel
        self.sampling_rate = sampling_rate
        self.running = False
        self.output_voltage = 0.0  # Initial output voltage
        self.output_min_voltage = 0.0  # Minimum output voltage
        self.output_max_voltage = 5.0  # Maximum output voltage (adjust based on your DAQ device)

    def run(self):
        """Main loop to read input voltage and write output voltage."""
        self.running = True

        # Create tasks for AI and AO
        with nidaqmx.Task() as input_task, nidaqmx.Task() as output_task:
            try:
                # Configure AI task
                input_task.ai_channels.add_ai_voltage_chan(
                    self.input_channel,
                    terminal_config=TerminalConfiguration.RSE  # Set to RSE
                )
                input_task.timing.cfg_samp_clk_timing(
                    rate=self.sampling_rate,  # Set the sampling rate
                    sample_mode=AcquisitionType.CONTINUOUS,  # Continuous sampling
                    samps_per_chan=1000  # Buffer size
                )

                # Configure AO task
                output_task.ao_channels.add_ao_voltage_chan(
                    self.output_channel,
                    min_val=self.output_min_voltage,  # Set minimum output voltage
                    max_val=self.output_max_voltage  # Set maximum output voltage
                )
                # AO task uses on-demand timing (no timing configuration needed)

                # Start tasks
                input_task.start()
                output_task.start()

                # Main loop for continuous reading and writing
                while self.running:
                    try:
                        # Read a single sample from the AI task
                        input_voltage = input_task.read(number_of_samples_per_channel=1)
                        self.voltage_measured.emit(input_voltage[0])  # Emit the measured voltage

                        # Debug: Print the clamped output voltage
                        print(f"Writing output voltage: {self.output_voltage:.3f}V")

                        # Write the output voltage to the AO task (on-demand)
                        output_task.write(self.output_voltage)
                    except Exception as e:
                        print(f"Error in DAQ operation: {e}")
                        self.running = False

                    # Sleep to respect the sampling rate
                    time.sleep(1.0 / self.sampling_rate)

            finally:
                # Stop and clear tasks
                input_task.stop()
                output_task.stop()

    def set_output_voltage(self, voltage: float):
        """Set the output voltage (clamped to the valid range)."""
        self.output_voltage = max(self.output_min_voltage, min(voltage, self.output_max_voltage))
        print(f"Output voltage set to: {self.output_voltage:.3f}V")  # Debug statement

    def stop(self):
        """Stop the worker thread."""
        self.running = False