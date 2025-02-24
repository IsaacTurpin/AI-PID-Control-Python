import nidaqmx
from nidaqmx.constants import TerminalConfiguration
from nidaqmx.system import System

class DAQInterface:
    def __init__(self):
        self.system: System = nidaqmx.system.System.local()

    def get_available_devices(self) -> list[str]:
        """Return a list of available DAQ devices."""
        return self.system.devices.device_names

    def get_available_channels(self, device_name: str, channel_type: str = "ai") -> list[str]:
        """Return a list of available channels for a given device."""
        if channel_type == "ai":
            # Get the physical channels for the device
            physical_chans = self.system.devices[device_name].ai_physical_chans
            # Construct channel names without prepending the device name again
            return [chan.name for chan in physical_chans]
        elif channel_type == "ao":
            # Get the physical channels for the device
            physical_chans = self.system.devices[device_name].ao_physical_chans
            # Construct channel names without prepending the device name again
            return [chan.name for chan in physical_chans]
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