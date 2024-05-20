"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""
from typing import TextIO
from names import Names
from functools import cached_property

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

    def __init__(self, path: str, names: Names):
        """Open specified file and initialise reserved words and IDs."""

        self.path = path
        self.names = names
        self.symbol_type_list = [self.COMMA, self.SEMICOLON, self.COLON, self.FULL_STOP, self.ARROW,
                                 self.OPEN_CURLY_BRACKET, self.CLOSE_CURLY_BRACKET, self.KEYWORD, self.NUMBER,
                                 self.NAME] = range(10)
        self.keywords_list = ["DEVICE", "CLOCK", "SWITCH", "MONITOR", "CONNECTION"]
        [self.DEVICE_ID, self.CONNECT_ID, self.SWITCH_ID, self.MONITOR_ID, self.CONNECT_ID] \
            = self.names.lookup(self.keywords_list)
        self.current_character = ""

    def get_symbol(self) -> Symbol:
        """Translate the next sequence of characters into a symbol and return the symbol."""

        symbol = Symbol()
        self.skip_spaces()  # current character now not whitespace

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

        else:  # not a valid character
            # throw error
            self.advance()

            return symbol

    @cached_property
    def file(self) -> TextIO:
        """Open and return the file specified by path."""
        try:
            return open(self.path, "r")
        except FileNotFoundError:
            print(f"Error! File '{self.path}' could not be found")

    def get_next_character(self) -> str:
        """Read and return the next character in file."""

        return self.file.read(1)

    def skip_spaces(self) -> None:
        """Seek and update current_character to the next non-whitespace character in file."""

        char = self.current_character

        while char.isspace():
            char = self.get_next_character()

        self.current_character = char

    def skip_single_line_comment(self) -> None:
        pass

    def skip_multi_line_comment(self) -> None:
        pass

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

        number = self.get_next_character()
        next_char = self.get_next_character()

        while next_char.isdigit():
            number += next_char
            next_char = self.get_next_character()

        self.current_character = next_char

        return number

    def advance(self) -> None:
        """Advance to the next character in file"""

        self.current_character = self.get_next_character()