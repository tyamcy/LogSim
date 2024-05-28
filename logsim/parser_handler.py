from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner, Symbol


class LineTerminalOutput:
    def __init__(self, line_location: str, line_with_issue: str, arrow: str, message: str, error_code: int):
        self.line_location = line_location
        self.line_with_issue = line_with_issue
        self.arrow = arrow
        self.message = message
        self.error_code = error_code

    def __str__(self):
        return f"\n{self.line_location}\n{self.line_with_issue}\n{self.arrow}\n{self.message}\n"


class FileTerminalOutput:
    def __init__(self, message: str, error_code: int):
        self.message = message
        self.error_code = error_code

    def __str__(self):
        return f"\nFile error: {self.message}\n"


class ParserErrorHandler:
    def __init__(self, names: Names, devices: Devices, network: Network, monitors: Monitors, scanner: Scanner):
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner
        self.error_output_list = []

        # line error
        [self.EXPECT_IDENTIFIER, self.EXPECT_INPUT_DEVICE, self.EXPECT_VARIABLE_INPUT_NUMBER,
         self.EXPECT_CLOCK_CYCLE, self.EXPECT_INITIAL_STATE, self.EXPECT_PIN_IN, self.EXPECT_PIN_OUT,
         self.EXPECT_PIN_IN_OR_OUT, self.EXPECT_KEYWORD, self.EXPECT_OPEN_CURLY_BRACKET, self.EXPECT_COMMA,
         self.EXPECT_SEMICOLON, self.EXPECT_COLON, self.EXPECT_FULL_STOP_OR_SEMICOLON, self.EXPECT_FULL_STOP,
         self.EXPECT_ARROW, self.EXPECT_FULL_STOP_OR_ARROW, self.DUPLICATE_KEYWORD, self.WRONG_BLOCK_ORDER] \
            = names.unique_error_codes(19)

        # file error
        [self.MISSING_INPUT_TO_PIN, self.MISSING_MONITOR, self.MISSING_CLOCK_OR_SWITCH] = names.unique_error_codes(3)

        self.error_limit = 100

    def line_error(self, error_code: int, symbol: Symbol) -> None:
        if len(self.error_output_list) <= self.error_limit:
            error_output = self.get_line_terminal_output(line=symbol.line, character_in_line=symbol.character_in_line,
                                                         error_code=error_code, name=self.symbol_to_name(symbol))

            self.error_output_list.append(error_output)
        elif len(self.error_output_list) == (self.error_limit + 1):
            self.error_output_list.append("\n--------------------------------------------------------"
                                          f"\nOver {self.error_limit} errors, further errors will not be reported!!"
                                          "\n--------------------------------------------------------")

    def symbol_to_name(self, symbol: Symbol) -> str:
        if symbol.id:  # symbol id is not None, i.e. symbol.type is KEYWORD, NUMBER, NAME or INVALID
            if symbol.type == Scanner.NUMBER or symbol.type == Scanner.INVALID:
                return symbol.id
            else:
                return self.names.get_name_string(symbol.id)
        elif symbol.type == Scanner.COMMA:
            return ","
        elif symbol.type == Scanner.SEMICOLON:
            return ";"
        elif symbol.type == Scanner.COLON:
            return ":"
        elif symbol.type == Scanner.FULL_STOP:
            return "."
        elif symbol.type == Scanner.ARROW:
            return ">"
        elif symbol.type == Scanner.OPEN_CURLY_BRACKET:
            return "{"
        elif symbol.type == Scanner.CLOSE_CURLY_BRACKET:
            return "}"
        elif symbol.type == Scanner.EOF:
            return ""
        else:
            raise ValueError("Invalid symbol type")

    def file_error(self, error_code: int, name: str = "") -> None:
        if len(self.error_output_list) <= self.error_limit:
            error_output = FileTerminalOutput(
                message=self.get_error_message(error_code=error_code, name=name),
                error_code=error_code
            )
            self.error_output_list.append(error_output)
        elif len(self.error_output_list) == (self.error_limit + 1):
            self.error_output_list.append("\n--------------------------------------------------------"
                                          f"\nOver {self.error_limit} errors, further errors will not be reported!!"
                                          "\n--------------------------------------------------------")

    def get_line_terminal_output(self, line: int, character_in_line: int, error_code: int, name: str) -> (
            LineTerminalOutput):
        left_char_limit = 25
        right_char_limit = 25
        line_str = self.scanner.file_lines[line]
        line_length = len(line_str)
        if character_in_line > left_char_limit:
            line_str = "..." + line_str[character_in_line-left_char_limit:]
            character_in_line = left_char_limit
        if line_length - character_in_line - 1 > right_char_limit:
            line_str = line_str[:character_in_line+right_char_limit + 1] + "..."
        return LineTerminalOutput(
            line_location=f"Line {line + 1}:",
            line_with_issue=line_str,
            arrow=" " * character_in_line + "^",
            message=self.get_error_message(error_code=error_code, name=name),
            error_code=error_code
        )

    def get_error_message(self, error_code: int, name: str = "") -> str:
        name = "\'" + name + "\'"
        if not (error_code == self.MISSING_CLOCK_OR_SWITCH or error_code == self.MISSING_MONITOR) and not name:
            raise TypeError(f"error_code = {error_code} has 1 required positional argument: 'name'")

        # syntax line error
        if error_code == self.EXPECT_IDENTIFIER:
            return f"Found {name}, expected a non-keyword identifier"
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
        elif error_code == self.EXPECT_COMMA:
            return f"Found {name}, expected ','"
        elif error_code == self.EXPECT_SEMICOLON:
            return f"Found {name}, expected ';'"
        elif error_code == self.EXPECT_COLON:
            return f"Found {name}, expected ':'"
        elif error_code == self.EXPECT_FULL_STOP_OR_SEMICOLON:  # for [ ".", ( pinIn | pinOut ) ], ";" in monitor
            return f"Found {name}, expected '.' (if pin has to be defined) or ';' (if pin does not have to be defined)"
        elif error_code == self.EXPECT_FULL_STOP:
            return f"Found {name}, expected '.'"
        elif error_code == self.EXPECT_ARROW:
            return f"Found {name}, expected '>'"
        elif error_code == self.EXPECT_FULL_STOP_OR_ARROW:  # for [".", pinOut] , ">" in connection
            return f"Found {name}, expected '.' (if pin has to be defined) or '>' (if pin does not have to be defined)"
        elif error_code == self.DUPLICATE_KEYWORD:
            return f"{name} block should not be redefined"
        elif error_code == self.WRONG_BLOCK_ORDER:
            return f"{name} block order is wrong"

        # semantic line error
        elif (error_code == self.network.INPUT_PORT_ABSENT or error_code == self.network.OUTPUT_PORT_ABSENT or
              error_code == self.monitors.MONITOR_PORT_ABSENT):
            return f"Pin {name} does not exist"
        elif error_code == self.network.INPUT_CONNECTED:
            return f"Connection repeatedly assigned to input pin {name}"
        elif (error_code == self.network.INPUT_DEVICE_ABSENT or error_code == self.network.OUTPUT_DEVICE_ABSENT or
              error_code == self.monitors.MONITOR_DEVICE_ABSENT):
            return f"Identifier {name} is not defined"
        elif error_code == self.devices.DEVICE_PRESENT or error_code == self.monitors.MONITOR_IDENTIFIER_PRESENT:
            return f"Identifier {name} should not be redefined"

        # file error
        elif error_code == self.MISSING_INPUT_TO_PIN:
            return f"Missing input to pin {name}"
        elif error_code == self.MISSING_MONITOR:
            return f"At least one monitor should be defined"
        elif error_code == self.MISSING_CLOCK_OR_SWITCH:
            return f"At least one list between 'CLOCK' and 'SWITCH' is needed. neither is found"

        else:
            raise ValueError(f"Invalid error code '{error_code}'")
