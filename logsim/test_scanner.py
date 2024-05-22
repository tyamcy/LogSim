"""Test the scanner module with 'test_scaner_text'."""
import pytest

from scanner import Scanner
from names import Names

path = "logsim/test_scanner_text"


class NameTest:
    # Keyword
    DEVICE = 0
    CLOCK = 1
    SWITCH = 2
    MONITOR = 3
    CONNECTION = 4

    # Name
    CLK1 = 5
    G1 = 6
    NOR = 7
    D1 = 8
    CLK = 9
    A = 10
    SET = 11
    B = 12
    D2 = 13
    CLEAR = 14
    Q = 15
    DATA = 16


test_list = [
    (Scanner.KEYWORD, NameTest.CLOCK),
    (Scanner.OPEN_CURLY_BRACKET, None),
    (Scanner.NAME, NameTest.CLK1),
    (Scanner.COLON, None),
    (Scanner.NUMBER, '10'),
    (Scanner.SEMICOLON, None),
    (Scanner.CLOSE_CURLY_BRACKET, None),
    (Scanner.KEYWORD, NameTest.DEVICE),
    (Scanner.OPEN_CURLY_BRACKET, None),
    (Scanner.NAME, NameTest.G1),
    (Scanner.COLON, None),
    (Scanner.NAME, NameTest.NOR),
    (Scanner.COMMA, None),
    (Scanner.NUMBER, '3'),
    (Scanner.SEMICOLON, None),
    (Scanner.CLOSE_CURLY_BRACKET, None),
    (Scanner.KEYWORD, NameTest.CONNECTION),
    (Scanner.OPEN_CURLY_BRACKET, None),
    (Scanner.NAME, NameTest.CLK1),
    (Scanner.ARROW, None),
    (Scanner.NAME, NameTest.D1),
    (Scanner.FULL_STOP, None),
    (Scanner.NAME, NameTest.CLK),
    (Scanner.NAME, NameTest.A),
    (Scanner.ARROW, None),
    (Scanner.NAME, NameTest.D1),
    (Scanner.FULL_STOP, None),
    (Scanner.NAME, NameTest.SET),
    (Scanner.SEMICOLON, None),
    (Scanner.NAME, NameTest.B),
    (Scanner.ARROW, None),
    (Scanner.NAME, NameTest.D2),
    (Scanner.FULL_STOP, None),
    (Scanner.NAME, NameTest.CLEAR),
    (Scanner.SEMICOLON, None),
    (None, None),  # '[' is not a valid symbol
    (Scanner.NAME, NameTest.D1),
    (Scanner.FULL_STOP, None),
    (Scanner.NAME, NameTest.Q),
    (Scanner.ARROW, None),
    (Scanner.NAME, NameTest.D2),
    (Scanner.FULL_STOP, None),
    (Scanner.NAME, NameTest.DATA),
    (Scanner.SEMICOLON, None),
    (Scanner.CLOSE_CURLY_BRACKET, None),
    (Scanner.EOF, None)
]


@pytest.fixture
def new_scanner():
    """Return a new instance of the Scanner class."""
    new_scanner = Scanner(path=path, names=Names())
    return new_scanner


def test_get_symbol(new_scanner):
    """Test if get_symbol returns the expected symbol type and ID."""
    for i in range(len(test_list)):
        symbol = new_scanner.get_symbol()
        assert (symbol.type, symbol.id) == test_list[i]


def test_scanner_raise_exception():
    """Test if Scanner initialization raises expected exceptions."""
    with pytest.raises(TypeError):
        Scanner(path=1, names=Names())
    with pytest.raises(TypeError):
        Scanner(path=path, names="name")
