"""Record and display output signals.

Used in the Logic Simulator project to record and display specified output
signals.

Classes
-------
Monitors - records and displays specified output signals.

"""
import collections

from typing import List, Union
from names import Names
from devices import Devices
from network import Network


class Monitors:

    """Record and display output signals.

    This class contains functions for recording and displaying the signal state
    of outputs specified by their device and port IDs.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.

    Public methods
    --------------
    make_monitor(self, device_id, port_id): Sets a specified monitor on the
                                              specified output.

    remove_monitor_by_port(self, device_id, port_id): Removes a monitor from the
                                                specified output by its port.

    remove_monitor_by_identifier(self, device_id, identifier): Removes a monitor from the
                                                specified output by its identifier (alias).

    get_monitor_signal(self, device_id, port_id): Returns the signal level of
                                                    the specified monitor.

    record_signals(self): Records the current signal level of all monitors.

    get_signal_names(self): Returns two lists of signal names: monitored and
                            not monitored.

    reset_monitors(self): Clears the memory of all monitors.

    get_margin(self): Returns the length of the longest monitor's name.

    display_signals(self): Displays signal trace(s) in the text console.
    """

    def __init__(self, names: Names, devices: Devices, network: Network):
        """Initialise the monitors dictionary and monitor errors."""
        self.names = names
        self.network = network
        self.devices = devices

        # signals_dictionary stores
        # {(device_id, port_id): [signal_list]}
        self.signals_dictionary = dict()

        # identifier_to_port stores
        # {(device_id, port_id): {identifier}}
        self.port_to_identifier = collections.defaultdict(set)

        # port_to_identifier stores
        # {identifier: (device_id, port_id)}
        self.identifier_to_port = collections.OrderedDict()

        [self.NO_ERROR, self.MONITOR_IDENTIFIER_PRESENT, self.MONITOR_DEVICE_ABSENT, self.MONITOR_PORT_ABSENT] = (
            self.names.unique_error_codes(4))

    def make_monitor(self, device_id: int, port_id: Union[int, None],
                     identifier: str, cycles_completed: int = 0) -> int:
        """Add the specified signal to the monitors dictionary.

        Return NO_ERROR if successful, or the corresponding error if not.
        """
        monitor_device = self.devices.get_device(device_id)
        if monitor_device is None:
            return self.MONITOR_DEVICE_ABSENT
        elif port_id not in monitor_device.outputs and port_id not in monitor_device.inputs:
            return self.MONITOR_PORT_ABSENT
        elif identifier in self.identifier_to_port:
            return self.MONITOR_IDENTIFIER_PRESENT
        else:
            # If n simulation cycles have been completed before making this
            # monitor, then initialise the signal trace with an n-length list
            # of BLANK signals. Otherwise, initialise the trace with an empty
            # list.
            if (device_id, port_id) not in self.signals_dictionary:
                self.signals_dictionary[(device_id, port_id)] = [
                    self.devices.BLANK] * cycles_completed

            self.port_to_identifier[(device_id, port_id)].add(identifier)
            self.identifier_to_port[identifier] = (device_id, port_id)
            return self.NO_ERROR

    def remove_monitor_by_port(self, device_id: int, port_id: Union[int, None]) -> bool:
        """Remove the specified signal from the signals, identifier_to_port and port_to_identifier dictionary by port.

        Return True if successful.
        """
        if ((device_id, port_id) not in self.signals_dictionary
                or (device_id, port_id) not in self.port_to_identifier):
            return False
        else:
            del self.signals_dictionary[(device_id, port_id)]
            del self.port_to_identifier[(device_id, port_id)]
            for identifier, port in self.identifier_to_port.copy().items():
                if port == (device_id, port_id):
                    del self.identifier_to_port[identifier]
            return True

    def remove_monitor_by_identifier(self, identifier: str) -> bool:
        """Remove the specified signal from the signals, identifier_to_port and port_to_identifier dictionary by
        identifier.

        Return True if successful.
        """
        if identifier not in self.identifier_to_port:
            return False
        else:
            del self.identifier_to_port[identifier]
            for port, identifier_set in self.port_to_identifier.copy().items():
                if identifier in identifier_set:
                    if len(identifier_set) == 1:  # only one identifier associated to the port
                        del self.signals_dictionary[port]
                        del self.port_to_identifier[port]
                    else:
                        self.port_to_identifier[port].remove(identifier)
            return True

    def get_monitor_signal(self, device_id: int, port_id: int) -> Union[int, None]:
        """Return the signal level of the specified monitor.

        If the monitor does not exist, return None.
        """
        device = self.devices.get_device(device_id)
        if (device_id, port_id) in self.signals_dictionary:
            if port_id in device.outputs:  # if output
                return self.network.get_output_signal(device_id, port_id)
            else:  # if input
                return self.network.get_input_signal(device_id, port_id)
        else:
            return None

    def record_signals(self) -> None:
        """Record the current signal level for every monitor.

        This function is called at every simulation cycle.
        """
        for device_id, port_id in self.signals_dictionary:
            signal_level = self.get_monitor_signal(device_id, port_id)
            self.signals_dictionary[(device_id,
                                     port_id)].append(signal_level)

    def get_signal_names(self) -> List[List[int]]:
        """Return two signal name lists: monitored and not monitored."""
        non_monitored_signal_list = []
        monitored_signal_list = []
        for device_id, port_id in self.signals_dictionary:
            monitor_name = self.devices.get_signal_name(device_id, port_id)
            monitored_signal_list.append(monitor_name)

        for device_id in self.devices.find_devices():
            device = self.devices.get_device(device_id)
            for port_id in device.outputs:
                if (device_id, port_id) not in self.signals_dictionary:
                    signal_name = self.devices.get_signal_name(device_id,
                                                               port_id)
                    non_monitored_signal_list.append(signal_name)

        return [monitored_signal_list, non_monitored_signal_list]

    def reset_monitors(self) -> None:
        """Clear the memory of all the monitors.

        The list of stored signal levels for each monitor is deleted.
        """
        for device_id, port_id in self.signals_dictionary:
            self.signals_dictionary[(device_id, port_id)] = []

    def get_margin(self) -> Union[int, None]:
        """Return the length of the longest monitor's name.

        Return None if no signals are being monitored. This is useful for
        finding out how much space to leave after each monitor's name before
        starting to draw the signal trace.
        """
        length_list = []  # for storing name lengths
        for device_id, port_id in self.signals_dictionary:
            monitor_name_set = self.port_to_identifier[(device_id, port_id)]
            for monitor_name in monitor_name_set:
                name_length = len(monitor_name)
                length_list.append(name_length)
        if length_list:  # if the list is not empty
            return max(length_list)
        else:
            return None

    def display_signals(self) -> None:
        """Display the signal trace(s) in the text console."""
        margin = self.get_margin()

        for identifier, (device_id, port_id) in self.identifier_to_port.items():
            name_length = len(identifier)
            signal_list = self.signals_dictionary[(device_id, port_id)]
            print(identifier + (margin - name_length) * " ", end=": ")
            for signal in signal_list:
                if signal == self.devices.HIGH:
                    print("-", end="")
                if signal == self.devices.LOW:
                    print("_", end="")
                if signal == self.devices.RISING:
                    print("/", end="")
                if signal == self.devices.FALLING:
                    print("\\", end="")
                if signal == self.devices.BLANK:
                    print(" ", end="")
            print("\n", end="")

    def fetch_identifier_to_device_port_name(self) -> dict:
        """Fetch device name and port name from a given identifier."""
        # {identifier: (device_name, port_name)}
        identifier_to_device_port_name = {}
        for identifier, (device_id, port_id) in self.identifier_to_port.items():
            device_name = self.names.get_name_string(device_id) if device_id else None
            port_name = self.names.get_name_string(port_id) if port_id else None
            identifier_to_device_port_name[identifier] = (device_name, port_name)
        return identifier_to_device_port_name

    def get_all_monitor_signal(self) -> dict:
        """Fetch all the signal levels from all monitors."""
        return self.signals_dictionary

    def get_identifier(self, device_id: int, port_id: Union[int, None]) -> set:
        """Get identifier string from device id and port id"""
        return self.port_to_identifier[(device_id, port_id)]
    
    def get_all_identifiers(self) -> collections.OrderedDict.keys:
        """Fetch all identifiers"""
        return self.identifier_to_port.keys()
