"""Test the monitors module."""
import pytest

from names import Names
from network import Network
from devices import Devices
from monitors import Monitors


@pytest.fixture
def new_monitors():
    """Return a Monitors class instance with monitors set on three outputs."""
    new_names = Names()
    new_devices = Devices(new_names)
    new_network = Network(new_names, new_devices)
    new_monitors = Monitors(new_names, new_devices, new_network)

    [SW1_ID, SW2_ID, OR1_ID, I1, I2] = new_names.lookup(["Sw1", "Sw2", "Or1",
                                                        "I1", "I2"])
    # Add 2 switches and an OR gate
    new_devices.make_device(OR1_ID, new_devices.OR, 2)
    new_devices.make_device(SW1_ID, new_devices.SWITCH, 0)
    new_devices.make_device(SW2_ID, new_devices.SWITCH, 0)

    # Make connections
    new_network.make_connection(SW1_ID, None, OR1_ID, I1)
    new_network.make_connection(SW2_ID, None, OR1_ID, I2)

    # Set monitors
    new_monitors.make_monitor(OR1_ID, None, "A1")
    new_monitors.make_monitor(SW1_ID, None, "B")
    new_monitors.make_monitor(SW2_ID, None, "C")
    new_monitors.make_monitor(OR1_ID, None, "A2")
    new_monitors.make_monitor(OR1_ID, I1, "Input1")
    new_monitors.make_monitor(OR1_ID, I2, "Input2")

    return new_monitors


def test_make_monitor(new_monitors):
    """Test if make_monitor correctly updates the signals dictionary."""
    names = new_monitors.names
    [SW1_ID, SW2_ID, OR1_ID, I1, I2] = names.lookup(["Sw1", "Sw2", "Or1",
                                                         "I1", "I2"])

    assert new_monitors.signals_dictionary == {(SW1_ID, None): [],
                                               (SW2_ID, None): [],
                                               (OR1_ID, None): [],
                                               (OR1_ID, I1): [],
                                               (OR1_ID, I2): []}


def test_identify_monitor(new_monitors):
    """Test if make_monitor correctly updates the identifiers dictionary."""
    names = new_monitors.names
    [SW1_ID, SW2_ID, OR1_ID, I1, I2] = names.lookup(["Sw1", "Sw2", "Or1",
                                                     "I1", "I2"])

    assert new_monitors.port_to_identifier == {(SW1_ID, None): {"B"},
                                               (SW2_ID, None): {"C"},
                                               (OR1_ID, None): {"A1", "A2"},
                                               (OR1_ID, I1): {"Input1"},
                                               (OR1_ID, I2): {"Input2"}}


def test_make_monitor_gives_errors(new_monitors):
    """Test if make_monitor returns the correct errors."""
    names = new_monitors.names
    network = new_monitors.network
    devices = new_monitors.devices
    [SW1_ID, SW3_ID, OR1_ID, I1, SWITCH_ID] = names.lookup(["Sw1", "Sw3",
                                                            "Or1", "I1",
                                                            "SWITCH"])

    # input is allowed
    assert new_monitors.make_monitor(OR1_ID, I1, "E") == new_monitors.NO_ERROR

    # multiple identifiers for the same port is allowed
    assert new_monitors.make_monitor(SW1_ID,
                                     None, "F") == new_monitors.NO_ERROR
    # repeated identifier is not allowed
    assert new_monitors.make_monitor(SW1_ID,
                                     None, "F") == new_monitors.MONITOR_IDENTIFIER_PRESENT
    # I1 is not a device_id in the network
    assert new_monitors.make_monitor(I1,
                                     None, "G") == new_monitors.MONITOR_DEVICE_ABSENT

    # Make a new switch device
    devices.make_device(SW3_ID, SWITCH_ID, 0)

    assert new_monitors.make_monitor(SW3_ID, None, "H") == new_monitors.NO_ERROR


def test_remove_monitor_by_port(new_monitors):
    """Test if remove_monitor_ correctly updates the signals and identifiers dictionary."""
    names = new_monitors.names
    [SW1_ID, SW2_ID, OR1_ID, I1, I2] = names.lookup(["Sw1", "Sw2", "Or1",
                                                     "I1", "I2"])

    new_monitors.remove_monitor_by_port(SW1_ID, None)
    assert new_monitors.signals_dictionary == {(SW2_ID, None): [],
                                               (OR1_ID, None): [],
                                               (OR1_ID, I1): [],
                                               (OR1_ID, I2): []}

    assert new_monitors.port_to_identifier == {(SW2_ID, None): {"C"},
                                               (OR1_ID, None): {"A1", "A2"},
                                               (OR1_ID, I1): {"Input1"},
                                               (OR1_ID, I2): {"Input2"}}


def test_remove_monitor_by_identifier(new_monitors):
    """Test if remove_monitor correctly updates the signals and identifiers dictionary."""
    names = new_monitors.names
    [SW1_ID, SW2_ID, OR1_ID, I1, I2] = names.lookup(["Sw1", "Sw2", "Or1",
                                                     "I1", "I2"])
    new_monitors.remove_monitor_by_identifier(identifier="A1")
    assert new_monitors.signals_dictionary == {(SW1_ID, None): [],
                                               (SW2_ID, None): [],
                                               (OR1_ID, None): [],
                                               (OR1_ID, I1): [],
                                               (OR1_ID, I2): []}

    assert new_monitors.port_to_identifier == {(SW1_ID, None): {"B"},
                                               (SW2_ID, None): {"C"},
                                               (OR1_ID, None): {"A2"},
                                               (OR1_ID, I1): {"Input1"},
                                               (OR1_ID, I2): {"Input2"}}


def test_get_signal_names(new_monitors):
    """Test if get_signal_names returns the correct signal name lists."""
    names = new_monitors.names
    devices = new_monitors.devices
    [D_ID] = names.lookup(["D1"])

    # Create a D-type device
    devices.make_device(D_ID, devices.D_TYPE)

    assert new_monitors.get_signal_names() == [["Or1", "Sw1", "Sw2", "Or1.I1", "Or1.I2"],
                                               ["D1.Q", "D1.QBAR"]]


def test_record_signals(new_monitors):
    """Test if record_signals records the correct signals."""
    names = new_monitors.names
    devices = new_monitors.devices
    network = new_monitors.network

    [SW1_ID, SW2_ID, OR1_ID, I1, I2] = names.lookup(["Sw1", "Sw2", "Or1",
                                                     "I1", "I2"])

    HIGH = devices.HIGH
    LOW = devices.LOW

    # Both switches are currently LOW
    network.execute_network()
    new_monitors.record_signals()

    # Set Sw1 to HIGH
    devices.set_switch(SW1_ID, HIGH)
    network.execute_network()
    new_monitors.record_signals()

    # Set Sw2 to HIGH
    devices.set_switch(SW2_ID, HIGH)
    network.execute_network()
    new_monitors.record_signals()

    assert new_monitors.signals_dictionary == {
        (OR1_ID, None): [LOW, HIGH, HIGH],
        (SW1_ID, None): [LOW, HIGH, HIGH],
        (SW2_ID, None): [LOW, LOW, HIGH],
        (OR1_ID, I1): [LOW, HIGH, HIGH],
        (OR1_ID, I2): [LOW, LOW, HIGH]}


def test_get_margin(new_monitors):
    """Test if get_margin returns the length of the longest monitor name."""
    names = new_monitors.names
    devices = new_monitors.devices
    [D_ID, DTYPE_ID, QBAR_ID, Q_ID] = names.lookup(["Dtype1", "DTYPE",
                                                    "QBAR", "Q"])

    # Create a D-type device and set monitors on its outputs
    devices.make_device(D_ID, DTYPE_ID)
    new_monitors.make_monitor(D_ID, QBAR_ID, "D1_QBAR")
    new_monitors.make_monitor(D_ID, Q_ID, "D1_Q")

    # Longest name should be D1_QBAR
    assert new_monitors.get_margin() == 7


def test_reset_monitors(new_monitors):
    """Test if reset_monitors clears the signal lists of all the monitors."""
    names = new_monitors.names
    devices = new_monitors.devices
    [SW1_ID, SW2_ID, OR1_ID, I1, I2] = names.lookup(["Sw1", "Sw2", "Or1",
                                                     "I1", "I2"])

    LOW = devices.LOW
    new_monitors.record_signals()
    new_monitors.record_signals()
    assert new_monitors.signals_dictionary == {(SW1_ID, None): [LOW, LOW],
                                               (SW2_ID, None): [LOW, LOW],
                                               (OR1_ID, None): [LOW, LOW],
                                               (OR1_ID, I1): [LOW, LOW],
                                               (OR1_ID, I2): [LOW, LOW]}
    new_monitors.reset_monitors()
    assert new_monitors.signals_dictionary == {(SW1_ID, None): [],
                                               (SW2_ID, None): [],
                                               (OR1_ID, None): [],
                                               (OR1_ID, I1): [],
                                               (OR1_ID, I2): []}


def test_display_signals(capsys, new_monitors):
    """Test if signal traces are displayed correctly on the console."""
    names = new_monitors.names
    devices = new_monitors.devices
    network = new_monitors.network

    [SW1_ID, CLOCK_ID, CL_ID] = names.lookup(["Sw1", "CLOCK", "Clock1"])

    HIGH = devices.HIGH

    # Make a clock and set a monitor on its output
    devices.make_device(CL_ID, CLOCK_ID, 2)
    new_monitors.make_monitor(CL_ID, None, "CLK")

    # Both switches are currently LOW
    for _ in range(10):
        network.execute_network()
        new_monitors.record_signals()

    # Set Sw1 to HIGH
    devices.set_switch(SW1_ID, HIGH)
    for _ in range(10):
        network.execute_network()
        new_monitors.record_signals()

    new_monitors.display_signals()

    # Get std_output
    out, _ = capsys.readouterr()

    traces = out.split("\n")
    assert len(traces) == 8
    assert "A1    : __________----------" in traces
    assert "B     : __________----------" in traces
    assert "C     : ____________________" in traces
    assert "A2    : __________----------" in traces
    assert "Input1: __________----------" in traces
    assert "Input2: ____________________" in traces

    # Clock could be anywhere in its cycle, but its half period is 2
    assert ("CLK   : __--__--__--__--__--" in traces or
            "CLK   : _--__--__--__--__--_" in traces or
            "CLK   : --__--__--__--__--__" in traces or
            "CLK   : -__--__--__--__--__-" in traces)

    assert "" in traces  # additional empty line at the end
