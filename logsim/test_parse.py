"""Test the parse module."""
import pytest

from parse import Parser
from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner

path_correct = "logsim/test_text/test_parse_correct_text"
path_wrong_order = "logsim/test_text/test_parse_wrong_order_text"
path_wrong_content = "logsim/test_text/test_parse_wrong_content_text"
path_all_error_1 = "logsim/test_text/test_parse_all_error_1"
path_all_error_2 = "logsim/test_text/test_parse_all_error_2"


@pytest.fixture
def new_parser(path):
    """Return a new instance of the Parser class."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner(path, names)

    return Parser(names, devices, network, monitors, scanner)


def all_error_1_expected_content(parser: Parser):
    return [
        ("Line 3:", parser.error_handler.EXPECT_IDENTIFIER),
        ("Line 4:", parser.error_handler.EXPECT_INPUT_DEVICE),
        ("Line 5:", parser.error_handler.EXPECT_INPUT_DEVICE),
        ("Line 7:", parser.error_handler.EXPECT_COLON),
        ("Line 8:", parser.error_handler.EXPECT_VARIABLE_INPUT_NUMBER),
        ("Line 9:", parser.error_handler.EXPECT_COMMA),
        ("Line 10:", parser.error_handler.EXPECT_SEMICOLON),
        ("Line 12:", parser.monitors.MONITOR_PRESENT),
        ("Line 20:", parser.error_handler.EXPECT_INITIAL_STATE),
        ("Line 26:", parser.error_handler.EXPECT_CLOCK_CYCLE),
        ("Line 31:", parser.error_handler.EXPECT_PIN_IN_OR_OUT),
        ("Line 32:", parser.error_handler.EXPECT_FULL_STOP_OR_SEMICOLON),
        ("Line 34:", parser.monitors.MONITOR_PRESENT),
        ("Line 35:", parser.error_handler.EXPECT_COLON),
        ("Line 36:", parser.network.DEVICE_ABSENT),
        ("Line 41:", None),  # no error code defined now - add later
        ("Line 42:", parser.error_handler.EXPECT_PIN_IN),
        ("Line 43:", parser.error_handler.EXPECT_ARROW),
        ("Line 44:", parser.error_handler.EXPECT_FULL_STOP),
        ("Line 45:", parser.error_handler.EXPECT_FULL_STOP),
        ("Line 46:", parser.error_handler.EXPECT_PIN_IN),
        ("Line 47:", parser.network.INPUT_CONNECTED),
        ("Line 48:", parser.network.PORT_ABSENT),
        ("Line 50:", parser.error_handler.EXPECT_FULL_STOP_OR_ARROW),
        ("Line 57:", parser.network.INPUT_CONNECTED),
        ("Line 64:", parser.network.PORT_ABSENT),
        ("Line 65:", parser.network.DEVICE_ABSENT)
    ]

def all_error_2_expected_content(parser: Parser):
    return [
        ("Line 1", parser.error_handler.WRONG_BLOCK_ORDER),
        ("Line 5", parser.error_handler.DUPLICATE_KEYWORD),
        ("Line 12", parser.error_handler.EXPECT_KEYWORD),
        ("Line 16", parser.error_handler.EXPECT_OPEN_CURLY_BRACKET),
    ]
    # Need to test MISSING_MONITOR and MISSING_CLOCK_OR_SWITCH

@pytest.mark.parametrize("path, expected_result", [
    (path_correct, True),
    (path_wrong_order, False),
    (path_wrong_content, False)
])
def test_parse_network(new_parser, path, expected_result):
    """Test if network parses correctly."""

    assert new_parser.parse_network() == expected_result


@pytest.mark.parametrize("path, expected_content", [
    (path_all_error_1, all_error_1_expected_content),
    (path_all_error_2, all_error_2_expected_content)
])
def test_parse_error(new_parser, path, expected_content):
    """Test if network error output is correct"""

    new_parser.parse_network()
    error_output = new_parser.error_handler.get_error_output()

    for i in range(len(error_output)):
        assert (error_output[i].line, error_output[i].error_code) == expected_content(new_parser)[i]

