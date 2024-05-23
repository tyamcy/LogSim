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

PATH = "holder_path"


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
        self.symbol_list = []
        self.block_dict = {}

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
        if (self.symbol.type == Scanner.KEYWORD and
                self.symbol.id == keyword):
            self.advance()
            if self.symbol.type == Scanner.OPEN_CURLY_BRACKET:
                self.advance()
                sub_rule()
                while self.symbol != Scanner.CLOSE_CURLY_BRACKET:
                    sub_rule()
                self.advance()
            else:
                self.skip_to_after_close_bracket()
                self.error_handler.handle_error()  # expected open bracket
        else:
            self.skip_to_after_close_bracket()
            self.error_handler.handle_error()  # expected the correct keyword type and keyword value

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
                self.error_handler.handle_error()  # expected colon
        else:
            self.error_handler.handle_error()  # device identifier not NAME type

    def clock(self):
        pass

    def switch(self):
        pass

    def monitor(self):
        pass

    def connect(self):
        pass

    def identifier(self) -> bool:
        if self.symbol.type == Scanner.NAME:
            self.advance()
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
                self.advance()
            else:
                # expect input device
                self.error_handler.handle_error(self.error_handler.EXPECT_INPUT_DEVICE, self.symbol)
                return False
        return True

    def variable_input_number(self) -> bool:
        if (self.symbol.type == Scanner.NUMBER and self.symbol_string()[0] != "0"
                and 1 <= int(self.symbol_string()) <= 16):
            self.advance()
            return True
        else:
            # expect variable input number
            self.error_handler.handle_error(self.error_handler.EXPECT_VARIABLE_INPUT_NUMBER, self.symbol)
            return False

    def initial_state(self) -> bool:
        if self.symbol.type == Scanner.NUMBER and self.symbol.id in self.INITIAL_STATE:
            self.advance()
            return True
        else:
            # expect initial state
            self.error_handler.handle_error(self.error_handler.EXPECT_INITIAL_STATE, self.symbol)
            return False

    def pin_in(self) -> bool:
        if self.symbol.type == Scanner.NAME and self.symbol_string() == "I":
            self.advance()
            # expect variable input number
            return self.variable_input_number()
        elif self.symbol.type == Scanner.NAME and self.symbol_string() in self.DTYPE_PIN_IN:
            self.advance()
            return True
        else:
            # expect pin in
            self.error_handler.handle_error(self.error_handler.EXPECT_PIN_IN, self.symbol)
            return False

    def pin_out(self) -> bool:
        if self.symbol.type == Scanner.NAME and self.symbol_string() in self.DTYPE_PIN_OUT:
            self.advance()
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
            self.advance()
            return True
        elif self.symbol.type == Scanner.NAME and self.symbol_string() in self.DTYPE_PIN_OUT:
            self.advance()
            return True
        else:
            # expect pin in or out
            self.error_handler.handle_error(self.error_handler.EXPECT_PIN_IN_OR_OUT, self.symbol)
            return False

    def clock_cycle(self) -> bool:
        if self.symbol.type == Scanner.NUMBER and self.symbol.id[0] != "0":
            self.advance()
            return True
        else:
            # expect clock cycle
            self.error_handler.handle_error(self.error_handler.EXPECT_CLOCK_CYCLE, self.symbol)
            return False

    def skip_to_after_semicolon(self) -> None:
        while self.symbol.type != Scanner.SEMICOLON:
            self.advance()
        self.advance()

    def skip_to_after_close_bracket(self) -> None:
        while self.symbol.type != Scanner.CLOSE_CURLY_BRACKET:
            self.advance()
        self.advance()

    def advance(self) -> None:
        self.symbol = self.scanner.get_symbol()

    def symbol_string(self):
        return self.names.get_name_string(self.symbol.id)

    def make_symbol_list(self):
        self.advance()
        while self.symbol != Scanner.EOF:
            self.symbol_list.append(self.symbol)
            self.advance()
    def make_block_dict(self):
        open_bracket = False
        keyword_positions = []
        block_body_positions = []
        for i in range(len(self.symbol_list)):
            if self.symbol_list[i] == Scanner.KEYWORD:
                if self.symbol_list[i+1] == Scanner.OPEN_CURLY_BRACKET:
                    open_bracket = True
                    # have not finished