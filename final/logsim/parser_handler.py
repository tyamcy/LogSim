"""Handler functions used by the parser.

Used in the Logic Simulator project to handle the syntactic and semantic
errors reported by the parser.

Classes
-------
LimeTerminalOutput - stores terminal outputs for line errors reported by parser.
FileTerminalOutput - stores terminal outputs for file errors reported by parser.
ParserErrorHandler - generates terminal outputs from errors reported by the parser.
"""

from logsim.names import Names
from logsim.devices import Devices
from logsim.network import Network
from logsim.monitors import Monitors
from logsim.scanner import Scanner, Symbol
from logsim.internationalization import _


class LineTerminalOutput:

    """Encapsulate a line error and store the error output to display on the terminal.

    Parameters
    ----------
    line_location: string. Contains string with format "Line NUMBER:"
    line_with_issue: string. Contains a (truncated) copy of the line with issue.
    arrow: string. Contains the string with "^" symbol at the right location.
    message: string. Contains the error message.
    error_code: integer.

    Public methods
    --------------
     __str__(self): Returns the terminal output representation of the instance.
    """

    def __init__(self, line_location: str, line_with_issue: str, arrow: str, message: str, error_code: int):
        """Initialise line terminal output content."""
        self.line_location = line_location
        self.line_with_issue = line_with_issue
        self.arrow = arrow
        self.message = message
        self.error_code = error_code

    def __str__(self):
        """Return the terminal output representation of the instance."""
        return f"\n{self.line_location}\n{self.line_with_issue}\n{self.arrow}\n{self.message}\n"


class FileTerminalOutput:

    """Encapsulate a file error and store the error output to display on the terminal.

    Parameters
    ----------
    message: string. Contains the error message.
    error_code: integer.

    Public methods
    --------------
     __str__(self): Returns the terminal output representation of the instance.
    """

    def __init__(self, message: str, error_code: int):
        """Initialise file terminal output content."""
        self.message = message
        self.error_code = error_code

    def __str__(self):
        """Return the terminal output representation of the instance."""
        return _(u"\nFile error: {message}\n").format(message=self.message)


class ParserErrorHandler:

    """Handle the syntactic and semantic errors reported by the parser.

    The parser error handler facilitates the parser for error handling. If the parser detects error
    in the definition file, the parser calls the error handler to create the respective terminal outputs.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    line_error(self, error_code, symbol): Create terminal outputs for errors appearing in a specific line.
    file_error(self, error_code, name): Create terminal outputs for errors related to the whole file,
                                rather than a specific line.

    """

    def __init__(self, names: Names, devices: Devices, network: Network, monitors: Monitors, scanner: Scanner):
        """Initialise constants."""
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
         self.EXPECT_ARROW, self.EXPECT_FULL_STOP_OR_ARROW, self.DUPLICATE_KEYWORD, self.WRONG_BLOCK_ORDER,
         self.EXPECT_CLOSE_CURLY_BRACKET, self.EXPECT_RC_TRIGGER_CYCLE] = names.unique_error_codes(21)

        # file error
        [self.MISSING_INPUT_TO_PIN, self.MISSING_MONITOR, self.MISSING_CLOCK_OR_SWITCH] = names.unique_error_codes(3)

        self.error_limit = 25

    def symbol_to_name(self, symbol: Symbol) -> str:
        """Return the string representation of the given symbol."""
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

    def error_limit_exceeded(self) -> None:
        """Add terminal output to indicate the number of error exceeds the display limit"""
        self.error_output_list.append("\n--------------------------------------------------------" +
                                      _(u"\nOver {error_limit} errors, further errors will not be reported!!")
                                      .format(error_limit=self.error_limit) +
                                      "\n--------------------------------------------------------")

    def line_error(self, error_code: int, symbol: Symbol) -> None:
        """Add terminal output to indicate error occurring in a line."""
        if len(self.error_output_list) <= self.error_limit:
            error_output = self.get_line_terminal_output(line=symbol.line, character_in_line=symbol.character_in_line,
                                                         error_code=error_code, name=self.symbol_to_name(symbol))

            self.error_output_list.append(error_output)
        elif len(self.error_output_list) == (self.error_limit + 1):
            self.error_limit_exceeded()

    def file_error(self, error_code: int, name: str = "") -> None:
        """Add terminal output to indicate error occurring in the scope of the whole file."""
        if len(self.error_output_list) <= self.error_limit:
            error_output = FileTerminalOutput(
                message=self.get_error_message(error_code=error_code, name=name),
                error_code=error_code
            )
            self.error_output_list.append(error_output)
        elif len(self.error_output_list) == (self.error_limit + 1):
            self.error_limit_exceeded()

    def get_line_terminal_output(self, line: int, character_in_line: int, error_code: int, name: str) -> (
            LineTerminalOutput):
        """Return terminal output based on information of the line error encountered."""
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
            line_location=_(u"Line {line_num}:").format(line_num=line + 1),
            line_with_issue=line_str,
            arrow=" " * character_in_line + "^",
            message=self.get_error_message(error_code=error_code, name=name),
            error_code=error_code
        )

    def get_error_message(self, error_code: int, name: str = "") -> str:
        """Return the error message based on the error encountered."""
        name = "\'" + name + "\'"
        if not (error_code == self.MISSING_CLOCK_OR_SWITCH or error_code == self.MISSING_MONITOR) and not name:
            raise TypeError(f"error_code = {error_code} has 1 required positional argument: 'name'")

        # syntax line error
        if error_code == self.EXPECT_IDENTIFIER:
            return _(u"Found {name}, expected a non-keyword identifier").format(name=name)
        elif error_code == self.EXPECT_INPUT_DEVICE:
            return _(u"Found {name}, expected 'AND', 'NAND', 'OR', 'NOR', 'XOR', 'DTYPE' or 'RC'").format(name=name)
        elif error_code == self.EXPECT_VARIABLE_INPUT_NUMBER:
            return _(u"Found {name}, expected integer between 1 and 16").format(name=name)
        elif error_code == self.EXPECT_CLOCK_CYCLE or error_code == self.EXPECT_RC_TRIGGER_CYCLE:
            return _(u"Found {name}, expected positive integer with no leading zero").format(name=name)
        elif error_code == self.EXPECT_INITIAL_STATE:
            return _(u"Found {name}, expected 0 or 1").format(name=name)
        elif error_code == self.EXPECT_PIN_IN:
            return _(u"Found {name}, expected 'I1-16', 'DATA', 'CLK', 'SET' or 'CLEAR'").format(name=name)
        elif error_code == self.EXPECT_PIN_OUT:
            return _(u"Found {name}, expected 'Q' or 'QBAR'").format(name=name)
        elif error_code == self.EXPECT_PIN_IN_OR_OUT:  # for ( pinIn | pinOut ) in monitor
            return _(u"Found {name}, expected 'I1-16', 'DATA', 'CLK', 'SET', 'CLEAR', 'Q' or 'QBAR'").format(name=name)
        elif error_code == self.EXPECT_KEYWORD:
            return (_(u"Found {name}, expected a keyword ('DEVICE', 'CLOCK', 'SWITCH', 'MONITOR' or 'CONNECTION')")
                    .format(name=name))
        elif error_code == self.EXPECT_OPEN_CURLY_BRACKET:
            return _(u"Found {name}, expected '{{'").format(name=name)
        elif error_code == self.EXPECT_COMMA:
            return _(u"Found {name}, expected ','").format(name=name)
        elif error_code == self.EXPECT_SEMICOLON:
            return _(u"Found {name}, expected ';'").format(name=name)
        elif error_code == self.EXPECT_COLON:
            return _(u"Found {name}, expected ':'").format(name=name)
        elif error_code == self.EXPECT_FULL_STOP_OR_SEMICOLON:  # for [ ".", ( pinIn | pinOut ) ], ";" in monitor
            return (
                _(u"Found {name}, expected '.' (if pin has to be defined) or ';' (if pin does not have to be defined)")
                .format(name=name)
            )
        elif error_code == self.EXPECT_FULL_STOP:
            return _(u"Found {name}, expected '.'").format(name=name)
        elif error_code == self.EXPECT_ARROW:
            return _(u"Found {name}, expected '>'").format(name=name)
        elif error_code == self.EXPECT_FULL_STOP_OR_ARROW:  # for [".", pinOut] , ">" in connection
            return (
                _(u"Found {name}, expected '.' (if pin has to be defined) or '>' (if pin does not have to be defined)")
                .format(name=name)
            )
        elif error_code == self.DUPLICATE_KEYWORD:
            return _(u"{name} block should not be redefined").format(name=name)
        elif error_code == self.WRONG_BLOCK_ORDER:
            return _(u"{name} block order is wrong").format(name=name)
        elif error_code == self.EXPECT_CLOSE_CURLY_BRACKET:
            return _(u"Found {name}, expected '}}'").format(name=name)

        # semantic line error
        elif (error_code == self.network.INPUT_PORT_ABSENT or error_code == self.network.OUTPUT_PORT_ABSENT or
              error_code == self.monitors.MONITOR_PORT_ABSENT):
            return _(u"Pin {name} does not exist").format(name=name)
        elif error_code == self.network.INPUT_CONNECTED:
            return _(u"Connection repeatedly assigned to input pin {name}").format(name=name)
        elif (error_code == self.network.INPUT_DEVICE_ABSENT or error_code == self.network.OUTPUT_DEVICE_ABSENT or
              error_code == self.monitors.MONITOR_DEVICE_ABSENT):
            return _(u"Identifier {name} is not defined").format(name=name)
        elif error_code == self.devices.DEVICE_PRESENT or error_code == self.monitors.MONITOR_IDENTIFIER_PRESENT:
            return _(u"Identifier {name} should not be redefined").format(name=name)

        # file error
        elif error_code == self.MISSING_INPUT_TO_PIN:
            return _(u"Missing input to pin {name}").format(name=name)
        elif error_code == self.MISSING_MONITOR:
            return _(u"At least one monitor should be defined")
        elif error_code == self.MISSING_CLOCK_OR_SWITCH:
            return _(u"At least one list between 'CLOCK' and 'SWITCH' is needed. neither is found")

        else:
            raise ValueError(f"Invalid error code '{error_code}'")
