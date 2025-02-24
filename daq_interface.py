import nidaqmx
from nidaqmx.constants import TerminalConfiguration
from nidaqmx.system import System

class DAQInterface:
    def __init__(self):
        self.system: System = nidaqmx.system.System.local()  # Explicitly declare type

    def get_available_devices(self) -> list[str]:
        """Return a list of available DAQ devices."""
        return self.system.devices.device_names

    def get_available_channels(self, device_name: str, channel_type: str = "ai") -> list[str]:
        """Return a list of available channels for a given device."""
        if channel_type == "ai":
            return [f"{device_name}/{chan.name}" for chan in self.system.devices[device_name].ai_physical_chans]
        elif channel_type == "ao":
            return [f"{device_name}/{chan.name}" for chan in self.system.devices[device_name].ao_physical_chans]
        else:
            raise ValueError("Invalid channel type. Use 'ai' or 'ao'.")

    def read_voltage(self, channel: str) -> float:
        """Read voltage from an analog input channel."""
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(channel, terminal_config=TerminalConfiguration.RSE)
            return task.read()

    def write_voltage(self, channel: str, voltage: float) -> None:
        """Write voltage to an analog output channel."""
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(channel)
            task.write(voltage)