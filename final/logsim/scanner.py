"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""
from typing import TextIO, List

from logsim.names import Names


class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None
        self.line = None
        self.character_in_line = None


class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """

    symbol_type_list = [COMMA, SEMICOLON, COLON, FULL_STOP, ARROW, OPEN_CURLY_BRACKET, CLOSE_CURLY_BRACKET, KEYWORD,
                        NUMBER, NAME, EOF, INVALID] = range(12)
    keywords_list = ["DEVICE", "CLOCK", "SWITCH", "MONITOR", "CONNECTION"]

    def __init__(self, path: str, names: Names):
        """Open specified file and initialise reserved words and IDs."""

        if not isinstance(path, str):
            raise TypeError("Expected path to be a string.")
        if not isinstance(names, Names):
            raise TypeError("Expected names to be a Names object.")

        self.path = path
        self.file = self.get_file()
        self.file_lines = self.get_file_lines()
        self.names = names
        [self.DEVICE_ID, self.CLOCK_ID, self.SWITCH_ID, self.MONITOR_ID, self.CONNECT_ID] \
            = self.names.lookup(self.keywords_list)
        self.current_character = " "
        self.current_line = 0
        self.current_character_in_line = -1

    def get_symbol(self) -> Symbol:
        """Translate the next sequence of characters into a symbol and return the symbol."""

        symbol = Symbol()
        self.skip_spaces()  # current character now not whitespace

        while self.current_character == "#" or self.current_character == "/":  # comment
            if self.current_character == "#":  # single-line comment
                self.skip_single_line_comment()
            else:  # multi-line comment
                self.skip_multi_line_comment()
            self.skip_spaces()

        symbol.line = self.current_line
        symbol.character_in_line = self.current_character_in_line

        if self.current_character.isalpha():  # name
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])

        elif self.current_character.isdigit():  # number
            symbol.id = self.get_number()
            symbol.type = self.NUMBER

        elif self.current_character == ",":  # punctuation
            symbol.type = self.COMMA
            self.advance()

        elif self.current_character == ";":
            symbol.type = self.SEMICOLON
            self.advance()

        elif self.current_character == ":":
            symbol.type = self.COLON
            self.advance()

        elif self.current_character == ".":
            symbol.type = self.FULL_STOP
            self.advance()

        elif self.current_character == ">":
            symbol.type = self.ARROW
            self.advance()

        elif self.current_character == "{":
            symbol.type = self.OPEN_CURLY_BRACKET
            self.advance()

        elif self.current_character == "}":
            symbol.type = self.CLOSE_CURLY_BRACKET
            self.advance()

        elif not self.current_character:  # end of file
            symbol.type = self.EOF

        else:  # not a valid character
            symbol.id = self.current_character
            symbol.type = self.INVALID
            self.advance()

        return symbol

    def get_file(self) -> TextIO:
        return open(self.path, "r")

    def get_file_lines(self) -> List[str]:
        file = self.get_file()
        file_lines = file.readlines()
        file_lines.append("")
        file.close()
        return file_lines

    def get_next_character(self) -> str:
        """Read and return the next character in file."""

        char = self.file.read(1)
        if char == "\n":  # next line
            self.current_line += 1
            self.current_character_in_line = -1
        else:
            self.current_character_in_line += 1
        return char

    def skip_spaces(self) -> None:
        """Seek and update current_character to the next non-whitespace in file."""

        char = self.current_character

        while char.isspace():
            char = self.get_next_character()

        self.current_character = char

    def skip_single_line_comment(self) -> None:
        """Skip single line comment"""

        char = self.get_next_character()

        while char and char != "\n":
            char = self.get_next_character()

        self.current_character = self.get_next_character()

    def skip_multi_line_comment(self) -> None:
        """Skip multi line comment"""

        char = self.get_next_character()

        while char and char != "/":
            char = self.get_next_character()

        self.current_character = self.get_next_character()

    def get_name(self) -> str:
        """Seek and return the next name string in file."""

        name = self.current_character
        next_char = self.get_next_character()

        while next_char.isalnum() or next_char == "_":
            name += next_char
            next_char = self.get_next_character()

        self.current_character = next_char

        return name

    def get_number(self) -> str:
        """Seek and return the next number string in file."""

        number = self.current_character
        next_char = self.get_next_character()

        while next_char.isdigit():
            number += next_char
            next_char = self.get_next_character()

        self.current_character = next_char

        return number

    def advance(self) -> None:
        """Advance to the next character in file"""

        self.current_character = self.get_next_character()
