from PyQt5.QtCore import QThread, pyqtSignal
import nidaqmx
from nidaqmx.constants import TerminalConfiguration, AcquisitionType
import time
from pid_controller import PIDController

class DAQWorker(QThread):
    # Signal to send the measured voltage to the GUI
    voltage_measured = pyqtSignal(float)
    # Signal to send the output voltage to the GUI
    output_voltage_updated = pyqtSignal(float)

    def __init__(self, input_channel: str, output_channel: str, sampling_rate: int):
        super().__init__()
        self.input_channel = input_channel
        self.output_channel = output_channel
        self.sampling_rate = sampling_rate
        self.running = False
        self.output_voltage = 0.0  # Initial output voltage
        self.output_min_voltage = 0.0  # Minimum output voltage
        self.output_max_voltage = 5.0  # Maximum output voltage
        self.pid_controller = PIDController()  # PID controller

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
                        # Read 1000 samples from the AI task
                        input_voltage = input_task.read(number_of_samples_per_channel=1000)
                        if input_voltage:  # Ensure data is not empty
                            # Use the last sample for PID control
                            last_sample = input_voltage[-1]
                            self.voltage_measured.emit(last_sample)  # Emit the measured voltage
                            print(f"Writing input voltage: {last_sample:.3f}V")

                            # Compute the PID output
                            output_voltage = self.pid_controller.compute(last_sample)

                            # Clamp the output voltage to the valid range
                            clamped_voltage = max(self.output_min_voltage, min(output_voltage, self.output_max_voltage))

                            # Debug: Print the clamped output voltage
                            print(f"Writing output voltage: {clamped_voltage:.3f}V")

                            # Emit the output voltage to the GUI
                            self.output_voltage_updated.emit(clamped_voltage)

                            # Write the output voltage to the AO task (on-demand)
                            output_task.write(clamped_voltage)
                    except nidaqmx.DaqError as e:
                        if e.error_code == -200279:  # Buffer overflow error
                            print("Buffer overflow detected. Reducing sampling rate or increasing buffer size.")
                            self.sampling_rate = max(10, self.sampling_rate // 2)  # Reduce sampling rate by half
                            print(f"New sampling rate: {self.sampling_rate} Hz")
                        else:
                            print(f"Error in DAQ operation: {e}")
                            self.running = False
                    except Exception as e:
                        print(f"Error in DAQ operation: {e}")
                        self.running = False

                    # Sleep to respect the sampling rate
                    time.sleep(1.0 / self.sampling_rate)

            except Exception as e:
                print(f"Error in task configuration: {e}")  # Debug statement
                self.running = False

            finally:
                print("Stopping tasks...")  # Debug statement
                input_task.stop()
                output_task.stop()

    def set_setpoint(self, setpoint: float):
        """Set the desired voltage (setpoint) for the PID controller."""
        self.pid_controller.setpoint = setpoint

    def stop(self):
        """Stop the worker thread."""
        self.running = False