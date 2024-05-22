"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner

PATH = "holder_path"


class Parser:
    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names: Names, devices: Devices, network: Network, monitors: Monitors, scanner: Scanner):
        """Initialise constants."""
        self.names = Names()
        self.devices = Devices(names=self.names)
        self.network = Network(names=self.names, devices=self.devices)
        self.monitors = Monitors(names=self.names, devices=self.devices, network=self.network)
        self.scanner = Scanner(names=self.names, path=PATH)
        self.error_count = 0
        self.symbol = self.scanner.get_symbol()

    def parse_network(self) -> bool:
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.

        if (self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == self.scanner.DEVICE_ID):
            self.advance()
            self.device_list()
        if (self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == self.scanner.CLOCK_ID):
            self.advance()
            self.clock_list()
        if (self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == self.scanner.SWITCH_ID):
            self.advance()
            self.switch_list()
        if (self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == self.scanner.MONITOR_ID):
            self.advance()
            self.monitor_list()
            self.advance()
            if (self.symbol.type == self.scanner.KEYWORD and
                    self.symbol.id == self.scanner.CONNECT_ID):
                self.connect_list()
        else:
            self.error()

        return True

    def device_list(self):
        if self.symbol.type == self.scanner.OPEN_CURLY_BRACKET:
            self.advance()
            self.device()
            while self.symbol != self.scanner.CLOSE_CURLY_BRACKET:
                self.device()
        else:
            self.skip_to_after_close_bracket()
            self.error()
        self.advance()

    def clock_list(self):
        pass

    def switch_list(self):
        pass

    def monitor_list(self):
        pass

    def connect_list(self):
        pass

    def device(self):
        if self.symbol.type == self.scanner.NAME:
            self.advance()
            if self.symbol.type == self.scanner.COLON:
                self.advance()

            else:
                self.error()
        else:
            self.error()

    def variable_input_device(self):
        if self.symbol.type == self.scanner.NAME:
            if self.symbol_string() in ["AND", "NAND", "OR", "NOR"]:
                self.advance()
            else:
                self.error()  # device name not accepted
        else:
            self.error()  # not NAME type

    def fixed_input_device(self):
        if self.symbol.type == self.scanner.NAME:
            if self.symbol_string() in ["XOR", "DTYPE"]:
                self.advance()
            else:
                self.error()  # device name not accepted
        else:
            self.error()  # not NAME type

    def initial_state(self):
        if self.symbol.type == self.scanner.NUMBER:
            if self.symbol.id in [0, 1]:
                self.advance()
            else:
                self.error()  # not a state of 0 or 1
        else:
            self.error()  # not NUMBER type

    def pin_in(self):
        if self.symbol.type == self.scanner.NAME:
            if self.symbol_string() == "I":
                self.advance()
                self.variable_input_number()
            elif self.symbol_string() in ["DATA", "CLK", "SET", "CLEAR"]:
                self.advance()
            else:
                self.error()  # pin in name not accepted
        else:
            self.error()  # not NAME type

    def pin_out(self):
        if self.symbol.type == self.scanner.NAME:
            if self.symbol_string() in ["Q", "QBAR"]:
                self.advance()
            else:
                self.error()  # pin out name not accepted
        else:
            self.error()  # not NAME type

    def variable_input_number(self):
        if self.symbol.type == self.scanner.NUMBER:
            if self.symbol.id in range(1, 17):
                self.advance()
            else:
                self.error()  # input number not in range
        else:
            self.error()  # not NUMBER type

    def clock_cycle(self):
        if self.symbol.type == self.scanner.NUMBER:
            if self.symbol.id in range(1, 17):
                self.advance()
            else:
                self.error()  # input number not in range
        else:
            self.error()  # not NUMBER type

    def skip_to_after_semicolon(self):
        pass

    def skip_to_after_close_bracket(self):
        pass

    def advance(self):
        self.symbol = self.scanner.get_symbol()

    def error(self):
        self.error_count += 1
        # need extra error handling, implement later

    def symbol_string(self):
        return self.names.get_name_string(self.symbol.id)
