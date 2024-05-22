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
from scanner import Scanner, Symbol

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
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner
        self.error_count = 0
        self.symbol = None
        self.symbol_list = []
        self.block_dict = {}

        # syntax error
        [self.EXPECT_IDENTIFIER, self.EXPECT_INPUT_DEVICE, self.EXPECT_VARIABLE_INPUT_NUMBER,
         self.EXPECT_CLOCK_CYCLE, self.EXPECT_INITIAL_STATE, self.EXPECT_PIN_IN, self.EXPECT_PIN_OUT,
         self.EXPECT_PIN_IN_OR_OUT, self.EXPECT_KEYWORD, self.EXPECT_OPEN_CURLY_BRACKET,
         self.EXPECT_CLOSE_CURLY_BRACKET_BEFORE_KEYWORD, self.EXPECT_COLON,
         self.EXPECT_SEMICOLON, self.EXPECT_FULL_STOP_OR_SEMICOLON,
         self.EXPECT_FULL_STOP, self.EXPECT_ARROW, self.EXPECT_FULL_STOP_OR_ARROW, self.MISSING_MONITOR] \
            = names.unique_error_codes(18)

        # semantic error
        [self.MISSING_CLOCK_OR_SWITCH] = names.unique_error_codes(1)

        self.error_count = 0

    def parse_network(self) -> bool:
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        self.make_symbol_list()
        self.make_block_dict()

        return True

    def list_parse(self, keyword, sub_rule):
        if (self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == keyword):
            self.advance()
            if self.symbol.type == self.scanner.OPEN_CURLY_BRACKET:
                self.advance()
                sub_rule()
                while self.symbol != self.scanner.CLOSE_CURLY_BRACKET:
                    sub_rule()
                self.advance()
            else:
                self.skip_to_after_close_bracket()
                self.handle_error()  # expected open bracket
        else:
            self.skip_to_after_close_bracket()
            self.handle_error()  # expected the correct keyword type and keyword value

    def device_list(self):
        self.list_parse(keyword=self.scanner.DEVICE_ID, sub_rule=self.device)

    def clock_list(self):
        self.list_parse(keyword=self.scanner.CLOCK_ID, sub_rule=self.clock)

    def switch_list(self):
        self.list_parse(keyword=self.scanner.SWITCH_ID, sub_rule=self.switch)

    def monitor_list(self):
        self.list_parse(keyword=self.scanner.MONITOR_ID, sub_rule=self.monitor)

    def connect_list(self):
        self.list_parse(keyword=self.scanner.CONNECT_ID, sub_rule=self.connect)

    def device(self):
        if self.symbol.type == self.scanner.NAME:
            self.advance()
            if self.symbol.type == self.scanner.COLON:
                self.advance()
                if self.fixed_input_device():
                    pass
            else:
                self.handle_error()  # expected colon
        else:
            self.handle_error()  # device identifier not NAME type

    def clock(self):
        pass

    def switch(self):
        pass

    def monitor(self):
        pass

    def connect(self):
        pass

    def variable_input_device(self):
        if self.symbol.type == self.scanner.NAME:
            if self.symbol_string() in ["AND", "NAND", "OR", "NOR"]:
                self.advance()
                return True
            else:
                self.handle_error()  # device name not accepted
                return False
        else:
            self.handle_error()  # not NAME type
            return False

    def fixed_input_device(self):
        if self.symbol.type == self.scanner.NAME:
            if self.symbol_string() in ["XOR", "DTYPE"]:
                self.advance()
                return True
            else:
                self.handle_error()  # device name not accepted
                return False
        else:
            self.handle_error()  # not NAME type
            return False

    def initial_state(self):
        if self.symbol.type == self.scanner.NUMBER:
            if self.symbol.id in [0, 1]:
                self.advance()
            else:
                self.handle_error()  # not a state of 0 or 1
        else:
            self.handle_error()  # not NUMBER type

    def pin_in(self):
        if self.symbol.type == self.scanner.NAME:
            if self.symbol_string() == "I":
                self.advance()
                self.variable_input_number()
            elif self.symbol_string() in ["DATA", "CLK", "SET", "CLEAR"]:
                self.advance()
            else:
                self.handle_error()  # pin in name not accepted
        else:
            self.handle_error()  # not NAME type

    def pin_out(self):
        if self.symbol.type == self.scanner.NAME:
            if self.symbol_string() in ["Q", "QBAR"]:
                self.advance()
            else:
                self.handle_error()  # pin out name not accepted
        else:
            self.handle_error()  # not NAME type

    def variable_input_number(self):
        if self.symbol.type == self.scanner.NUMBER:
            if int(self.symbol.id) in range(1, 17):
                self.advance()
                return True
            else:
                self.handle_error()  # input number not in range
                return False
        else:
            self.handle_error()  # not NUMBER type
            return False

    def clock_cycle(self):
        if self.symbol.type == self.scanner.NUMBER:
            if self.symbol.id[0] != "0":
                self.advance()
            else:
                self.handle_error()  # cycle starts with 0 or is 0
        else:
            self.handle_error()  # not NUMBER type

    def skip_to_after_semicolon(self):
        while self.symbol.type != self.scanner.SEMICOLON:
            self.advance()
        self.advance()

    def skip_to_after_close_bracket(self):
        while self.symbol.type != self.scanner.CLOSE_CURLY_BRACKET:
            self.advance()
        self.advance()

    def advance(self):
        self.symbol = self.scanner.get_symbol()
        while not self.symbol.type:
            self.handle_error()  # ERROR symbol encountered
            self.symbol = self.scanner.get_symbol()

    def symbol_string(self):
        return self.names.get_name_string(self.symbol.id)

    def make_symbol_list(self):
        self.advance()
        while self.symbol != self.scanner.EOF:
            self.symbol_list.append(self.symbol)
            self.advance()
    def make_block_dict(self):
        open_bracket = False
        keyword_positions = []
        block_body_positions = []
        for i in range(len(self.symbol_list)):
            if self.symbol_list[i] == self.scanner.KEYWORD:
                if self.symbol_list[i+1] == self.scanner.OPEN_CURLY_BRACKET:
                    open_bracket = True
                    # have not finished

    def handle_error(self, error_code: int, symbol: Symbol):
        self.error_count += 1
        # need extra error handling, implement later

    def get_error_message(self, error_code: int, name: str == "") -> str:
        if error_code not in [self.MISSING_MONITOR, self.MISSING_CLOCK_OR_SWITCH] and not name:
            raise TypeError(f"error_code = {error_code} has 1 required positional argument: 'name'")

        # syntax error
        if error_code == self.EXPECT_IDENTIFIER:
            return f"Found {name}, expected an identifier"
        elif error_code == self.EXPECT_INPUT_DEVICE:
            return f"Found {name}, expected 'AND', 'NAND', 'OR', 'NOR', 'XOR' or 'DTYPE'"
        elif error_code == self.EXPECT_VARIABLE_INPUT_NUMBER:
            return f"Found {name}, expected integer between 1 and 16"
        elif error_code == self.EXPECT_CLOCK_CYCLE:
            return f"Found {name}, expected positive integer with no leading zero"
        elif error_code == self.EXPECT_INITIAL_STATE:
            return f"Found {name}, expected 0 or 1"
        elif error_code == self.EXPECT_PIN_IN:
            return f"Found {name}, expected 'I1-16', 'DATA', 'CLK', 'SET' or 'CLEAR'"
        elif error_code == self.EXPECT_PIN_OUT:
            return f"Found {name}, expected 'Q' or 'QBAR'"
        elif error_code == self.EXPECT_PIN_IN_OR_OUT:  # for ( pinIn | pinOut ) in monitor
            return f"Found {name}, expected 'I1-16', 'DATA', 'CLK', 'SET', 'CLEAR', 'Q' or 'QBAR'"
        elif error_code == self.EXPECT_KEYWORD:
            return f"Found {name}, expected a keyword ('DEVICE', 'CLOCK', 'SWITCH', 'MONITOR' or 'CONNECTION')"
        elif error_code == self.EXPECT_OPEN_CURLY_BRACKET:
            return f"Found {name}, expected '{{'"
        elif error_code == self.EXPECT_CLOSE_CURLY_BRACKET_BEFORE_KEYWORD:
            return f"Found {name}, expected '}}' before keyword"
        elif error_code == self.EXPECT_COLON:
            return f"Found {name}, expected ':'"
        elif error_code == self.EXPECT_SEMICOLON:
            return f"Found {name}, expected ';'"
        elif error_code == self.EXPECT_FULL_STOP_OR_SEMICOLON:  # for [ ".", ( pinIn | pinOut ) ], ";" in monitor
            return f"Found {name}, expected '.' (if pin has to be defined) or ';' (if pin does not have to be defined)"
        elif error_code == self.EXPECT_FULL_STOP:
            return f"Found {name}, expected '.'"
        elif error_code == self.EXPECT_ARROW:
            return f"Found {name}, expected '>'"
        elif error_code == self.EXPECT_FULL_STOP_OR_ARROW:  # for [".", pinOut] , ">" in connection
            return f"Found {name}, expected '.' (if pin has to be defined) or ';' (if pin does not have to be defined)"
        elif error_code == self.MISSING_MONITOR:
            return f"'MONITOR' list not found"

        # semantic error
        elif error_code == self.network.PORT_ABSENT:
            return f"Pin {name} does not exist"
        elif error_code == self.network.INPUT_CONNECTED:
            return f"Connection repeatedly assigned to input pin {name}"
        elif False:  # undefined error code now - implement later
            return f"Missing input to pin {name}"
        elif error_code == self.network.DEVICE_ABSENT:
            return f"Identifier {name} is not defined"
        elif error_code == self.devices.DEVICE_PRESENT or self.monitors.MONITOR_PRESENT:
            return f"Identifier {name} should not be redefined"
        elif error_code == self.MISSING_CLOCK_OR_SWITCH:
            return f"At least one list between 'CLOCK' and 'SWITCH' is needed. neither is found"
        else:
            raise ValueError(f"Invalid semantic error code '{error_code}' or invalid empty name")

