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
from collections import OrderedDict
from copy import copy


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
        self.block_parse_flags = {"DEVICE": False,
                                  "SWITCH": False,
                                  "CLOCK": False,
                                  "MONITOR": False,
                                  "CONNECTION": False}
        self.block_order_flags = OrderedDict([("DEVICE", False),
                                              ("SWITCH", False),
                                              ("CLOCK", False),
                                              ("MONITOR", False),
                                              ("CONNECTION", False)])
        self.current_identifier = None
        self.current_qualifier = None
        self.current_device_kind = None

    def parse_network(self) -> bool:
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        self.advance()
        while self.symbol.type != Scanner.EOF:
            if self.symbol.type == Scanner.KEYWORD:
                keyword = self.names.get_name_string(self.symbol.id)
                if self.block_parse_flags[keyword]:
                    self.error_handler.line_error(self.error_handler.DUPLICATE_KEYWORD, self.symbol)
                    self.skip_to_close_bracket()
                    self.advance()
                elif self.block_order_flags[keyword]:
                    self.error_handler.line_error(self.error_handler.WRONG_BLOCK_ORDER, self.symbol)
                    self.skip_to_close_bracket()
                    self.advance()
                elif keyword == "DEVICE":
                    self.device_list()
                    self.advance()
                elif keyword == "SWITCH":
                    self.switch_list()
                    self.advance()
                elif keyword == "CLOCK":
                    self.clock_list()
                    self.advance()
                elif keyword == "MONITOR":
                    self.monitor_list()
                    self.advance()
                elif keyword == "CONNECTION":
                    if self.block_parse_flags["MONITOR"]:
                        self.connect_list()
                        self.advance()
                    else:
                        self.error_handler.line_error(self.error_handler.WRONG_BLOCK_ORDER, self.symbol)
                        self.skip_to_close_bracket()
                        self.advance()
                self.set_flag(keyword)
            else:
                self.error_handler.line_error(self.error_handler.EXPECT_KEYWORD, self.symbol)
                self.skip_to_close_bracket()
                self.advance()

        # check file level error
        # missing monitor list
        if not self.block_parse_flags["MONITOR"]:
            self.error_handler.file_error(self.error_handler.MISSING_MONITOR)
        # missing clock or switch list
        if not self.block_parse_flags["CLOCK"] and not self.block_parse_flags["SWITCH"]:
            self.error_handler.file_error(self.error_handler.MISSING_CLOCK_OR_SWITCH)
        # missing input to pin
        if not len(self.fetch_error_output()):
            for device in self.devices.devices_list:
                device_id = device.device_id
                for input_id in device.inputs:
                    input_signal = self.network.get_input_signal(device_id, input_id)
                    if input_signal is None:  # this input is unconnected
                        self.error_handler.file_error(self.error_handler.MISSING_INPUT_TO_PIN,
                                                      self.devices.get_signal_name(device_id, input_id))

        return False if self.fetch_error_output() else True

    def parse_list(self, keyword: str, sub_rule: bool()):
        self.advance()
        if self.symbol.type == Scanner.OPEN_CURLY_BRACKET:
            self.advance()
            # list cannot be empty
            # wrong first sub-rule
            if not sub_rule():
                self.skip_after_semicolon_or_to_close_bracket()

            # check for subsequent sub-rule if any
            while self.symbol.type != Scanner.CLOSE_CURLY_BRACKET and Scanner.EOF:
                # wrong sub-rule
                if not sub_rule():
                    self.skip_after_semicolon_or_to_close_bracket()

        else:
            # expect open curly bracket
            self.error_handler.line_error(self.error_handler.EXPECT_OPEN_CURLY_BRACKET, self.symbol)
            self.skip_to_close_bracket()

    def set_flag(self, keyword: str) -> None:
        # set block parse flag
        self.block_parse_flags[keyword] = True
        # set block order flag
        for key in self.block_order_flags:
            if key == keyword:
                break
            self.block_order_flags[key] = True

    def device_list(self):
        self.parse_list(keyword="DEVICE", sub_rule=self.device)

    def clock_list(self):
        self.parse_list(keyword="CLOCK", sub_rule=self.clock)

    def switch_list(self):
        self.parse_list(keyword="SWITCH", sub_rule=self.switch)

    def monitor_list(self):
        self.parse_list(keyword="MONITOR", sub_rule=self.monitor)

    def connect_list(self):
        self.parse_list(keyword="CONNECTION", sub_rule=self.connect)

    def device(self) -> bool:
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
        if not self.semicolon():
            return False
        else:
            #  attempts to make device if there is no syntax error so far
            self.make_device()
            return True

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
        self.current_qualifier = copy(self.symbol)
        self.advance()

        # expect semicolon
        if not self.semicolon():
            return False
        else:
            self.current_device_kind = self.devices.CLOCK
            self.make_device()
            return True

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
        self.current_qualifier = copy(self.symbol)
        self.advance()

        # expect semicolon
        if not self.semicolon():
            return False
        else:
            self.current_device_kind = self.devices.SWITCH
            self.make_device()
            return True

    def monitor(self) -> bool:
        # expect identifier
        if not self.identifier():
            return False
        identifier_symbol = copy(self.symbol)
        self.advance()

        # expect colon
        if not self.colon():
            return False
        self.advance()

        # expect identifier
        if not self.identifier():
            return False
        device_symbol = copy(self.symbol)
        self.advance()

        # except full stop or semicolon
        # optionally expect full stop
        port_symbol = None
        if self.symbol.type == Scanner.FULL_STOP:
            self.advance()
            if not self.pin_in_or_out():
                # expect pin in or out
                return False
            port_symbol = self.symbol
            self.advance()
        elif self.symbol.type != Scanner.SEMICOLON:  # not full stop or semicolon
            self.error_handler.line_error(self.error_handler.EXPECT_FULL_STOP_OR_SEMICOLON, self.symbol)
            return False
        # expect semicolon
        if not self.semicolon():
            return False
        else:
            #  attempts to make monitor
            self.make_monitor(identifier_symbol=identifier_symbol, port_symbol=port_symbol, device_symbol=device_symbol)
            return True

    def connect(self) -> bool:
        # expect identifier
        if not self.identifier():
            return False
        out_device_symbol = copy(self.symbol)
        self.advance()
        # expect full stop or arrow
        # optionally expect full stop
        out_port_symbol = None
        if self.symbol.type == Scanner.FULL_STOP:
            self.advance()
            # expect pin out
            if not self.pin_out():
                return False
            out_port_symbol = copy(self.symbol)
            self.advance()
        elif self.symbol.type != Scanner.ARROW:  # not full stop or arrow
            self.error_handler.line_error(self.error_handler.EXPECT_FULL_STOP_OR_ARROW, self.symbol)
            return False
        # expect arrow
        if self.symbol.type != Scanner.ARROW:
            self.error_handler.line_error(self.error_handler.EXPECT_ARROW, self.symbol)
            return False
        self.advance()

        # expect identifier
        if not self.identifier():
            return False
        in_device_symbol = copy(self.symbol)
        self.advance()

        # expect full stop
        if not self.full_stop():
            return False
        self.advance()

        # expect pin in
        if not self.pin_in():
            return False
        in_port_symbol = copy(self.symbol)
        self.advance()

        # expect semicolon
        if not self.semicolon():
            return False
        else:
            # attempts to make connection between devices
            self.make_connection(out_device_symbol, out_port_symbol, in_device_symbol, in_port_symbol)
            return True

    def colon(self) -> bool:
        if not self.symbol.type == Scanner.COLON:
            self.error_handler.line_error(self.error_handler.EXPECT_COLON, self.symbol)
            return False
        else:
            return True

    def semicolon(self) -> bool:
        if not self.symbol.type == Scanner.SEMICOLON:
            self.error_handler.line_error(self.error_handler.EXPECT_SEMICOLON, self.symbol)
            return False
        else:
            self.advance()
            return True

    def full_stop(self) -> bool:
        if not self.symbol.type == Scanner.FULL_STOP:
            self.error_handler.line_error(self.error_handler.EXPECT_FULL_STOP, self.symbol)
            return False
        else:
            return True

    def identifier(self) -> bool:
        # Note: EBNF technically allows keywords to be used as identifier, but here the software will not allow
        if self.symbol.type == Scanner.NAME:
            self.current_identifier = copy(self.symbol)
            return True
        else:
            self.error_handler.line_error(self.error_handler.EXPECT_IDENTIFIER, self.symbol)
            return False

    def input_device(self) -> bool:
        if self.symbol.type == Scanner.NAME:
            if self.symbol_string() in self.VARIABLE_INPUT_DEVICE:
                self.current_device_kind = self.symbol.id
                self.advance()
                if self.symbol.type != Scanner.COMMA:
                    # expect comma
                    self.error_handler.line_error(self.error_handler.EXPECT_COMMA, self.symbol)
                    return False
                self.advance()

                # expect variable input number
                return self.variable_input_number()
            elif self.symbol_string() in self.FIXED_INPUT_DEVICE:
                self.current_qualifier = None
                self.current_device_kind = self.symbol.id
                return True

        # expect input device
        self.error_handler.line_error(self.error_handler.EXPECT_INPUT_DEVICE, self.symbol)
        return False

    def variable_input_number(self) -> bool:
        if (self.symbol.type == Scanner.NUMBER and self.symbol.id[0] != "0"
                and 1 <= int(self.symbol.id) <= 16):
            self.current_qualifier = copy(self.symbol)
            return True
        else:
            # expect variable input number
            self.error_handler.line_error(self.error_handler.EXPECT_VARIABLE_INPUT_NUMBER, self.symbol)
            return False

    def initial_state(self) -> bool:
        if self.symbol.type == Scanner.NUMBER and self.symbol.id in self.INITIAL_STATE:
            return True
        else:
            # expect initial state
            self.error_handler.line_error(self.error_handler.EXPECT_INITIAL_STATE, self.symbol)
            return False

    def pin_in_variable_input_number(self, input_number: str) -> bool:
        if input_number.isnumeric() and input_number[0] != "0" and 1 <= int(input_number) <= 16:
            return True
        else:
            return False

    def pin_in(self) -> bool:
        if self.symbol.type == Scanner.NAME and self.symbol_string()[0] == "I":
            # expect variable input number
            remaining_symbol_string = self.symbol_string()[1:]
            if self.pin_in_variable_input_number(remaining_symbol_string):
                return True
            else:
                self.error_handler.line_error(self.error_handler.EXPECT_PIN_IN, self.symbol)
                return False
        elif self.symbol.type == Scanner.NAME and self.symbol_string() in self.DTYPE_PIN_IN:
            return True
        else:
            # expect pin in
            self.error_handler.line_error(self.error_handler.EXPECT_PIN_IN, self.symbol)
            return False

    def pin_out(self) -> bool:
        if self.symbol.type == Scanner.NAME and self.symbol_string() in self.DTYPE_PIN_OUT:
            return True
        else:
            # expect pin out
            self.error_handler.line_error(self.error_handler.EXPECT_PIN_OUT, self.symbol)
            return False

    def pin_in_or_out(self) -> bool:
        if self.symbol.type == Scanner.NAME and self.symbol_string()[0] == "I":
            # expect variable input number
            remaining_symbol_string = self.symbol_string()[1:]
            if self.pin_in_variable_input_number(remaining_symbol_string):
                return True
            else:
                self.error_handler.line_error(self.error_handler.EXPECT_PIN_IN_OR_OUT, self.symbol)
                return False
        elif self.symbol.type == Scanner.NAME and self.symbol_string() in self.DTYPE_PIN_IN:
            return True
        elif self.symbol.type == Scanner.NAME and self.symbol_string() in self.DTYPE_PIN_OUT:
            return True
        else:
            # expect pin in or out
            self.error_handler.line_error(self.error_handler.EXPECT_PIN_IN_OR_OUT, self.symbol)
            return False

    def clock_cycle(self) -> bool:
        if self.symbol.type == Scanner.NUMBER and self.symbol.id[0] != "0":
            return True
        else:
            # expect clock cycle
            self.error_handler.line_error(self.error_handler.EXPECT_CLOCK_CYCLE, self.symbol)
            return False

    def skip_after_semicolon_or_to_close_bracket(self) -> None:
        while (self.symbol.type != Scanner.SEMICOLON and
               self.symbol.type != Scanner.CLOSE_CURLY_BRACKET and
               self.symbol.type != Scanner.EOF):
            self.advance()
        if self.symbol.type == Scanner.SEMICOLON:
            self.advance()

    def skip_to_close_bracket(self) -> None:
        while self.symbol.type != Scanner.CLOSE_CURLY_BRACKET and self.symbol.type != Scanner.EOF:
            self.advance()

    def skip_to_keyword(self) -> None:
        self.advance()
        while self.symbol.type != Scanner.KEYWORD and self.symbol.type != Scanner.EOF:
            self.advance()

    def advance(self) -> None:
        self.symbol = self.scanner.get_symbol()

    def symbol_string(self) -> str:
        return self.names.get_name_string(self.symbol.id)

    def fetch_error_output(self):
        return self.error_handler.error_output_list

    def error_count(self):
        return len(self.error_handler.error_output_list)

    def make_device(self):
        if not self.error_count():
            device_kind = self.current_device_kind
            device_id = self.current_identifier.id
            device_property = int(self.current_qualifier.id) if self.current_qualifier else None
            error_type = self.devices.make_device(device_id, device_kind, device_property)
            if error_type == self.devices.NO_ERROR:
                pass
            elif error_type == self.devices.DEVICE_PRESENT:
                self.error_handler.line_error(error_type, self.current_identifier)
            elif error_type == self.devices.QUALIFIER_PRESENT:
                self.error_handler.line_error(error_type, self.current_qualifier)
            else:
                print(f"Error type: {error_type}, should not be encountered")

    def make_monitor(self, identifier_symbol, port_symbol, device_symbol):
        if not self.error_count():
            identifier = self.names.get_name_string(identifier_symbol.id)
            port_id = port_symbol.id if port_symbol else None
            device_id = device_symbol.id
            error_type = self.monitors.make_monitor(identifier=identifier, port_id=port_id, device_id=device_id)
            if error_type == self.monitors.NO_ERROR:
                pass
            elif error_type == self.monitors.MONITOR_PORT_ABSENT:
                self.error_handler.line_error(self.monitors.MONITOR_PORT_ABSENT, port_symbol)
            elif error_type == self.monitors.MONITOR_IDENTIFIER_PRESENT:
                self.error_handler.line_error(self.monitors.MONITOR_IDENTIFIER_PRESENT, identifier_symbol)
            elif error_type == self.monitors.MONITOR_DEVICE_ABSENT:
                self.error_handler.line_error(self.monitors.MONITOR_DEVICE_ABSENT, device_symbol)
            elif error_type == self.monitors.MONITOR_PORT_ABSENT:
                self.error_handler.line_error(self.monitors.MONITOR_PORT_ABSENT, port_symbol)
            else:
                print(f"Error type: {error_type}, should not be encountered")

    def make_connection(self, out_device_symbol, out_port_symbol, in_device_symbol, in_port_symbol):
        if not self.error_count():
            out_device_id = out_device_symbol.id
            out_port_id = out_port_symbol.id if out_port_symbol else None
            in_device_id = in_device_symbol.id
            in_port_id = in_port_symbol.id
            error_type = self.network.make_connection(out_device_id, out_port_id, in_device_id, in_port_id)
            if error_type == self.network.NO_ERROR:
                pass
            elif error_type == self.network.INPUT_PORT_ABSENT:
                self.error_handler.line_error(self.network.INPUT_PORT_ABSENT, in_port_symbol)
            elif error_type == self.network.OUTPUT_PORT_ABSENT:
                self.error_handler.line_error(self.network.OUTPUT_PORT_ABSENT, out_port_symbol)
            elif error_type == self.network.INPUT_DEVICE_ABSENT:
                self.error_handler.line_error(self.network.INPUT_DEVICE_ABSENT, in_device_symbol)
            elif error_type == self.network.OUTPUT_DEVICE_ABSENT:
                self.error_handler.line_error(self.network.OUTPUT_DEVICE_ABSENT, out_device_symbol)
            elif error_type == self.network.INPUT_CONNECTED:
                self.error_handler.line_error(self.network.INPUT_CONNECTED, in_port_symbol)
            else:
                print(f"Error type: {error_type}, should not be encountered")
