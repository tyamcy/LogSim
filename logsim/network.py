"""Build and execute the network.

Used in the Logic Simulator project to add and connect devices together.

Classes
--------
Network - builds and executes the network.
"""
from typing import Optional, Tuple

from devices import Devices
from names import Names


class Network:

    """Build and execute the network.

    This class contains many functions required for connecting devices together
    in the network, getting information about connections, and executing all
    the devices in the network.

    Parameters
    ----------
    devices - instance of the devices.Devices() class.

    Public methods
    --------------
    get_connected_output(self, device_id, output_id): Returns the device and
                                              port id of the connected output.

    get_input_signal(self, device_id, input_id): Returns the signal level at
                                     the output connected to the given input.

    get_output_signal(self, device_id, output_id): Returns the signal level at
                                                   the given output.

    make_connection(self, first_device_id, first_port_id, second_device_id,
                    second_port_id): Connects the first device to the second
                                     device.

    check_network(self): Checks if all inputs in the network are connected.

    update_signal(self, signal, target): Updates the signal in the direction of
                                         the target.

    invert_signal(self, signal): Returns the inverse of the signal if the
                                 signal is HIGH or LOW.

    execute_switch(self, device_id): Simulates a switch press.

    execute_gate(self, device_id, x=None, y=None): Simulates a logic gate and
                                              updates its output signal value.

    execute_d_type(self, device_id): Simulates a D-type device and updates its
                                     output signal value.

    execute_clock(self, device_id): Simulates a clock and updates its output
                                    signal value.

    update_clocks(self): If it is time to do so, sets clock signals to RISING
                         or FALLING.

    execute_network(self): Executes all the devices in the network for one
                           simulation cycle.
    """

    def __init__(self, names: Names, devices: Devices):
        """Initialise network errors and the steady_state variable."""
        self.names = names
        self.devices = devices

        [self.NO_ERROR, self.INPUT_CONNECTED, self.INPUT_PORT_ABSENT, self.OUTPUT_PORT_ABSENT,
         self.INPUT_DEVICE_ABSENT, self.OUTPUT_DEVICE_ABSENT] = (
            self.names.unique_error_codes(6))
        self.steady_state = True  # for checking if signals have settled

    def get_connected_output(self, device_id: int, input_id: int) -> Optional[Tuple[int, Optional[int]]]:
        """Return the output connected to the given input.

        Return None if either of the specified IDs is invalid or the input is
        unconnected. The output is of the form (device ID, port ID).
        """
        device = self.devices.get_device(device_id)
        if device is not None:
            if input_id in device.inputs:
                connected_output = device.inputs[input_id]
                return connected_output
        return None

    def get_input_signal(self, device_id: int, input_id: int) -> Optional[int]:
        """Return the signal level at the output connected to the given input.

        Return None if the input is unconnected or the specified IDs are
        invalid.
        """
        connected_output = self.get_connected_output(device_id, input_id)
        if connected_output is None:  # invalid IDs or unconnected input
            return None
        else:
            (output_device_id, output_port_id) = connected_output
            return self.get_output_signal(output_device_id, output_port_id)

    def get_output_signal(self, device_id: int, output_id: Optional[int]) -> Optional[int]:
        """Return the signal level at the given output.

        Return None if either of the specified IDs is invalid.
        """
        device = self.devices.get_device(device_id)
        if device is not None:
            if output_id in device.outputs:
                return device.outputs[output_id]
        return None

    def make_connection(self, output_device_id: int, output_port_id: Optional[int], input_device_id: int,
                        input_port_id: int) -> int:
        """Connect the output device to the input device.

        Return self.NO_ERROR if successful, or the corresponding error if not.
        """
        output_device = self.devices.get_device(output_device_id)
        input_device = self.devices.get_device(input_device_id)
        if output_device is None:
            error_type = self.OUTPUT_DEVICE_ABSENT
        elif input_device is None:
            error_type = self.INPUT_DEVICE_ABSENT
        elif output_port_id in output_device.outputs:
            if input_port_id in input_device.inputs:
                if input_device.inputs[input_port_id] is not None:
                    # Input is already in a connection
                    error_type = self.INPUT_CONNECTED
                else:
                    input_device.inputs[input_port_id] = (output_device_id, output_port_id)
                    error_type = self.NO_ERROR
            else:
                error_type = self.INPUT_PORT_ABSENT

        else:  # first_port_id not a valid input or output port
            error_type = self.OUTPUT_PORT_ABSENT

        return error_type

    def check_network(self) -> bool:
        """Return True if all inputs in the network are connected."""
        for device_id in self.devices.find_devices():
            device = self.devices.get_device(device_id)
            for input_id in device.inputs:
                if self.get_connected_output(device_id, input_id) is None:
                    return False
        return True

    def update_signal(self, signal: int, target: int) -> Optional[int]:
        """Update the signal in the direction of the target.

        Return updated signal, and set steady_state to false if the new signal
        is different from the old signal.
        """
        if signal in [self.devices.LOW, self.devices.FALLING]:
            if target == self.devices.LOW:
                new_signal = self.devices.LOW
            else:
                new_signal = self.devices.RISING
        elif signal in [self.devices.HIGH, self.devices.RISING]:
            if target == self.devices.LOW:
                new_signal = self.devices.FALLING
            else:
                new_signal = self.devices.HIGH
        else:
            return None
        if signal != new_signal:
            self.steady_state = False
        return new_signal

    def invert_signal(self, signal: int) -> Optional[int]:
        """Return the inverse of the signal if the signal is HIGH or LOW.

        Return None if the signal is not HIGH or LOW.
        """
        if signal == self.devices.HIGH:
            return self.devices.LOW
        elif signal == self.devices.LOW:
            return self.devices.HIGH
        else:
            return None

    def execute_switch(self, device_id: int) -> bool:
        """Simulate a switch.

        The output signal is updated to the switch_state target. Return True
        if successful.
        """
        device = self.devices.get_device(device_id)
        target = device.switch_state
        signal = self.get_output_signal(device_id, output_id=None)
        # Update and store the updated signal
        updated_signal = self.update_signal(signal, target)
        if updated_signal is None:  # signal update is unsuccessful
            return False
        else:
            device.outputs[None] = updated_signal
            return True

    def execute_gate(self, device_id: int, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """Simulate a logic gate and update its output signal value.

        The rule is: if all its inputs are x, then its output is y, else its
        output is the inverse of y.
        Note: (x,y) pairs for AND, OR, NOR, NAND, XOR are: (HIGH, HIGH), (LOW,
        LOW), (LOW, HIGH), (HIGH, LOW), (None, None).
        Return True if successful.
        """
        device = self.devices.get_device(device_id)
        for input_id in device.inputs:
            input_signal = self.get_input_signal(device_id, input_id)
            if input_signal is None:  # this input is unconnected
                return False

        input_signal_list = []
        for input_id in device.inputs:
            input_signal = self.get_input_signal(device_id, input_id)
            input_signal_list.append(input_signal)
            if device.device_kind != self.devices.XOR:
                if input_signal != x:
                    output_signal = self.invert_signal(y)
                    break
                output_signal = y

        if device.device_kind == self.devices.XOR:
            # Output is high only if both inputs are different
            if input_signal_list[0] == input_signal_list[1]:  # assume two inputs
                output_signal = self.devices.LOW
            else:
                output_signal = self.devices.HIGH

        # Update and store the new signal
        signal = self.get_output_signal(device_id, None)
        target = output_signal
        updated_signal = self.update_signal(signal, target)
        if updated_signal is None:  # if the update is unsuccessful
            return False
        device.outputs[None] = updated_signal
        return True

    def execute_d_type(self, device_id: int) -> bool:
        """Simulate a D-type device and update its output signal value.

        Return True if successful.
        """
        device = self.devices.get_device(device_id)

        for input_id in device.inputs:
            input_signal = self.get_input_signal(device_id, input_id)
            if input_signal is None:  # if the input is unconnected
                return False
            if input_id == self.devices.CLK_ID:
                clock_signal = input_signal
            elif input_id == self.devices.DATA_ID:
                data_signal = input_signal
            elif input_id == self.devices.CLEAR_ID:
                clear_signal = input_signal
            elif input_id == self.devices.SET_ID:
                set_signal = input_signal

        # Set D-type memory depending on the input signal
        if clock_signal == self.devices.RISING:
            if data_signal in [self.devices.HIGH, self.devices.FALLING]:
                device.dtype_memory = self.devices.HIGH
            elif data_signal in [self.devices.LOW, self.devices.RISING]:
                device.dtype_memory = self.devices.LOW
        if set_signal == self.devices.HIGH:
            device.dtype_memory = self.devices.HIGH
        if clear_signal == self.devices.HIGH:
            device.dtype_memory = self.devices.LOW

        if self.devices.Q_ID not in device.outputs:
            if self.devices.QBAR_ID not in device.outputs:
                return False
        Q_signal = device.outputs[self.devices.Q_ID]
        QBAR_signal = device.outputs[self.devices.QBAR_ID]

        # Update the output towards its memory
        new_Q = self.update_signal(Q_signal, device.dtype_memory)
        new_QBAR = self.update_signal(QBAR_signal,
                                      self.invert_signal(device.dtype_memory))
        if new_Q is None or new_QBAR is None:  # if the update is unsuccessful
            return False
        device.outputs[self.devices.Q_ID] = new_Q
        device.outputs[self.devices.QBAR_ID] = new_QBAR

        return True

    def execute_clock(self, device_id: int) -> bool:
        """Simulate a clock and update its output signal value.

        Return True if successful.
        """
        device = self.devices.get_device(device_id)
        output_signal = device.outputs[None]  # output ID is None

        if output_signal == self.devices.RISING:
            new_signal = self.update_signal(output_signal, self.devices.HIGH)
            if new_signal is None:  # update is unsuccessful
                return False
            device.outputs[None] = new_signal
            return True

        elif output_signal == self.devices.FALLING:
            new_signal = self.update_signal(output_signal, self.devices.LOW)
            if new_signal is None:  # update is unsuccessful
                return False
            device.outputs[None] = new_signal
            return True

        elif output_signal in [self.devices.HIGH, self.devices.LOW]:
            return True

        else:
            return False

    def update_clocks(self) -> None:
        """If it is time to do so, set clock signals to RISING or FALLING."""
        clock_devices = self.devices.find_devices(self.devices.CLOCK)
        for device_id in clock_devices:
            device = self.devices.get_device(device_id)
            if device.clock_counter == device.clock_half_period:
                device.clock_counter = 0
                output_signal = self.get_output_signal(device_id,
                                                       output_id=None)
                if output_signal == self.devices.HIGH:
                    device.outputs[None] = self.devices.FALLING
                elif output_signal == self.devices.LOW:
                    device.outputs[None] = self.devices.RISING
            device.clock_counter += 1

    def execute_network(self) -> bool:
        """Execute all the devices in the network for one simulation cycle.

        Return True if successful and the network does not oscillate.
        """
        clock_devices = self.devices.find_devices(self.devices.CLOCK)
        switch_devices = self.devices.find_devices(self.devices.SWITCH)
        d_type_devices = self.devices.find_devices(self.devices.D_TYPE)
        and_devices = self.devices.find_devices(self.devices.AND)
        or_devices = self.devices.find_devices(self.devices.OR)
        nand_devices = self.devices.find_devices(self.devices.NAND)
        nor_devices = self.devices.find_devices(self.devices.NOR)
        xor_devices = self.devices.find_devices(self.devices.XOR)

        # This sets clock signals to RISING or FALLING, where necessary
        self.update_clocks()

        # Number of iterations to wait for the signals to settle before
        # declaring the network unstable
        iteration_limit = 20

        iterations = 0
        while iterations < iteration_limit:
            iterations += 1
            self.steady_state = True

            for device_id in switch_devices:  # execute switch devices
                if not self.execute_switch(device_id):
                    return False
            # Execute D-type devices before clocks to catch the rising edge of
            # the clock
            for device_id in d_type_devices:  # execute DTYPE devices
                if not self.execute_d_type(device_id):
                    return False
            for device_id in clock_devices:  # complete clock executions
                if not self.execute_clock(device_id):
                    return False
            for device_id in and_devices:  # execute AND gate devices
                if not self.execute_gate(device_id, self.devices.HIGH,
                                         self.devices.HIGH):
                    return False
            for device_id in or_devices:  # execute OR gate devices
                if not self.execute_gate(device_id, self.devices.LOW,
                                         self.devices.LOW):
                    return False
            for device_id in nand_devices:  # execute NAND gate devices
                if not self.execute_gate(device_id, self.devices.HIGH,
                                         self.devices.LOW):
                    return False
            for device_id in nor_devices:  # execute NOR gate devices
                if not self.execute_gate(device_id, self.devices.LOW,
                                         self.devices.HIGH):
                    return False
            for device_id in xor_devices:  # execute XOR devices
                if not self.execute_gate(device_id, None, None):
                    return False
            if self.steady_state:
                break
        return self.steady_state
