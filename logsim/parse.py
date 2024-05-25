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
from parser_handler import ParserErrorHandler

PATH = "test_parser_1"


class Parser:
    DTYPE_PIN_IN = ["DATA", "CLK", "SET", "CLEAR"]
    DTYPE_PIN_OUT = ["Q", "QBAR"]
    VARIABLE_INPUT_DEVICE = ["AND", "NAND", "OR", "NOR"]
    FIXED_INPUT_DEVICE = ["XOR", "DTYPE"]
    INITIAL_STATE = ["0", "1"]

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
        self.error_handler = ParserErrorHandler(names=names, devices=devices, network=network, monitors=monitors,
                                                scanner=scanner)
        self.symbol = None

    def parse_network(self) -> bool:
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.

        return True

    def parse_list(self, keyword: int, sub_rule: bool()):
        if (self.symbol.type == Scanner.KEYWORD and
                self.symbol.id == keyword):
            self.advance()
            if self.symbol.type == Scanner.OPEN_CURLY_BRACKET:
                self.advance()
                # list cannot be empty
                # wrong sub-rule
                if not sub_rule():
                    self.skip_to_semicolon_or_close_bracket()
                while self.symbol.type != Scanner.CLOSE_CURLY_BRACKET and self.symbol.type != Scanner.EOF:
                    # wrong sub-rule
                    if not sub_rule():
                        self.skip_to_semicolon_or_close_bracket()
                self.advance()
            else:
                # expect open curly bracket
                self.error_handler.handle_error(self.error_handler.EXPECT_OPEN_CURLY_BRACKET, self.symbol)
                self.skip_to_close_bracket()
        else:
            # expect keyword
            self.error_handler.handle_error(self.error_handler.EXPECT_KEYWORD, self.symbol)
            self.skip_to_close_bracket()

    def device_list(self):
        print("parsing device list")
        self.parse_list(keyword=self.scanner.DEVICE_ID, sub_rule=self.device)
        print("device list correct")

    def clock_list(self):
        print("parsing clock list")
        self.parse_list(keyword=self.scanner.CLOCK_ID, sub_rule=self.clock)
        print("clock list correct")
    def switch_list(self):
        print("parsing switch list")
        self.parse_list(keyword=self.scanner.SWITCH_ID, sub_rule=self.switch)
        print("switch list correct")

    def monitor_list(self):
        print("parsing monitor list")
        self.parse_list(keyword=self.scanner.MONITOR_ID, sub_rule=self.monitor)
        print("monitor list correct")

    def connect_list(self):
        print("parsing connect list")
        self.parse_list(keyword=self.scanner.CONNECT_ID, sub_rule=self.connect)
        print("connect list correct")

    def device(self) -> bool:
        print("parsing device")
        # expect identifier
        if not self.identifier():
            return False
        self.advance()

        # expect colon
        if not self.colon():
            return False
        self.advance()

        # expect input device
        if not self.input_device():
            return False
        self.advance()

        # expect semicolon
        return self.semicolon()

    def clock(self) -> bool:
        # expect identifier
        if not self.identifier():
            return False
        self.advance()

        # expect colon
        if not self.colon():
            return False
        self.advance()

        # expect clock cycle
        if not self.clock_cycle():
            return False
        self.advance()

        # expect semicolon
        return self.semicolon()

    def switch(self) -> bool:
        # expect identifier
        if not self.identifier():
            return False
        self.advance()

        # expect colon
        if not self.colon():
            return False
        self.advance()

        # expect initial state
        if not self.initial_state():
            return False
        self.advance()

        # expect semicolon
        return self.semicolon()

    def monitor(self) -> bool:
        # expect identifier
        if not self.identifier():
            return False
        self.advance()

        # expect colon
        if not self.colon():
            return False
        self.advance()

        # expect identifier
        if not self.identifier():
            return False
        self.advance()

        # except full stop or semicolon
        # optionally expect full stop
        if self.symbol.type == Scanner.FULL_STOP:
            self.advance()
            if not self.pin_in_or_out():
                # expect pin in or out
                return False
            self.advance()
        elif self.symbol.type != Scanner.SEMICOLON:  # not full stop or semicolon
            self.error_handler.handle_error(self.error_handler.EXPECT_FULL_STOP_OR_SEMICOLON, self.symbol)
            return False
        # expect semicolon
        return self.semicolon()

    def connect(self) -> bool:
        # expect identifier
        if not self.identifier():
            return False
        self.advance()

        # expect full stop or arrow
        # optionally expect full stop
        if self.symbol.type == Scanner.FULL_STOP:
            self.advance()
            # expect pin out
            if not self.pin_out():
                return False
            self.advance()
        elif self.symbol.type != Scanner.ARROW:  # not full stop or arrow
            self.error_handler.handle_error(self.error_handler.EXPECT_FULL_STOP_OR_ARROW, self.symbol)
            return False
        # expect arrow
        if self.symbol.type != Scanner.ARROW:
            self.error_handler.handle_error(self.error_handler.EXPECT_ARROW, self.symbol)
            return False
        self.advance()

        # expect identifier
        if not self.identifier():
            return False
        self.advance()

        # expect full stop
        if not self.full_stop():
            return False
        self.advance()

        # expect pin in
        if not self.pin_in():
            return False
        self.advance()

        # expect semicolon
        return self.semicolon()

    def colon(self) -> bool:
        if not self.symbol.type == Scanner.COLON:
            self.error_handler.handle_error(self.error_handler.EXPECT_COLON, self.symbol)
            return False
        else:
            return True

    def semicolon(self) -> bool:
        if not self.symbol.type == Scanner.SEMICOLON:
            self.error_handler.handle_error(self.error_handler.EXPECT_SEMICOLON, self.symbol)
            return False
        else:
            self.advance()
            return True

    def full_stop(self) -> bool:
        if not self.symbol.type == Scanner.FULL_STOP:
            self.error_handler.handle_error(self.error_handler.EXPECT_FULL_STOP, self.symbol)
            return False
        else:
            return True

    def identifier(self) -> bool:
        # Note: EBNF technically allows keywords to be used as identifier, but here the software will not allow
        if self.symbol.type == Scanner.NAME:
            return True
        else:
            self.error_handler.handle_error(self.error_handler.EXPECT_IDENTIFIER, self.symbol)
            return False

    def input_device(self) -> bool:
        if self.symbol.type == Scanner.NAME:
            if self.symbol_string() in self.VARIABLE_INPUT_DEVICE:
                self.advance()
                if self.symbol.type != Scanner.COMMA:
                    # expect comma
                    self.error_handler.handle_error(self.error_handler.EXPECT_COMMA, self.symbol)
                    return False
                self.advance()
                # expect variable input number
                return self.variable_input_number()
            elif self.symbol_string() in self.FIXED_INPUT_DEVICE:
                return True
            else:
                # expect input device
                self.error_handler.handle_error(self.error_handler.EXPECT_INPUT_DEVICE, self.symbol)
                return False

    def variable_input_number(self) -> bool:
        if (self.symbol.type == Scanner.NUMBER and self.symbol.id[0] != "0"
                and 1 <= int(self.symbol.id) <= 16):
            return True
        else:
            # expect variable input number
            self.error_handler.handle_error(self.error_handler.EXPECT_VARIABLE_INPUT_NUMBER, self.symbol)
            return False

    def initial_state(self) -> bool:
        if self.symbol.type == Scanner.NUMBER and self.symbol.id in self.INITIAL_STATE:
            return True
        else:
            # expect initial state
            self.error_handler.handle_error(self.error_handler.EXPECT_INITIAL_STATE, self.symbol)
            return False

    def pin_in(self) -> bool:
        if self.symbol.type == Scanner.NAME and self.symbol_string()[0] == "I":
            # expect variable input number
            try:
                variable_number = int(self.symbol_string()[1:])
                if 1 <= variable_number <= 16:
                    return True
                else:
                    self.error_handler.handle_error(self.error_handler.EXPECT_VARIABLE_INPUT_NUMBER, self.symbol)
                    return False
            except ValueError:
                self.error_handler.handle_error(self.error_handler.EXPECT_PIN_IN, self.symbol)
                return False
        elif self.symbol.type == Scanner.NAME and self.symbol_string() in self.DTYPE_PIN_IN:
            return True
        else:
            # expect pin in
            self.error_handler.handle_error(self.error_handler.EXPECT_PIN_IN, self.symbol)
            return False

    def pin_out(self) -> bool:
        if self.symbol.type == Scanner.NAME and self.symbol_string() in self.DTYPE_PIN_OUT:
            return True
        else:
            # expect pin out
            self.error_handler.handle_error(self.error_handler.EXPECT_PIN_OUT, self.symbol)
            return False

    def pin_in_or_out(self) -> bool:
        if self.symbol.type == Scanner.NAME and self.symbol_string() == "I":
            self.advance()
            # expect variable input number
            return self.variable_input_number()
        elif self.symbol.type == Scanner.NAME and self.symbol_string() in self.DTYPE_PIN_IN:
            return True
        elif self.symbol.type == Scanner.NAME and self.symbol_string() in self.DTYPE_PIN_OUT:
            return True
        else:
            # expect pin in or out
            self.error_handler.handle_error(self.error_handler.EXPECT_PIN_IN_OR_OUT, self.symbol)
            return False

    def clock_cycle(self) -> bool:
        if self.symbol.type == Scanner.NUMBER and self.symbol.id[0] != "0":
            return True
        else:
            # expect clock cycle
            self.error_handler.handle_error(self.error_handler.EXPECT_CLOCK_CYCLE, self.symbol)
            return False

    def skip_to_semicolon_or_close_bracket(self) -> None:
        while self.symbol.type != Scanner.SEMICOLON or Scanner.CLOSE_CURLY_BRACKET or Scanner.EOF:
            self.advance()

    def skip_to_close_bracket(self) -> None:
        while self.symbol.type != Scanner.CLOSE_CURLY_BRACKET or Scanner.EOF:
            self.advance()

    def advance(self) -> None:
        self.symbol = self.scanner.get_symbol()

    def symbol_string(self) -> str:
        return self.names.get_name_string(self.symbol.id)
