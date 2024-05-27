"""Test the parse module."""
import pytest

from parse import Parser
from parser_handler import LineTerminalOutput, FileTerminalOutput
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

path_semantic_error_monitor_device_absent = "logsim/test_text/test_semantic_errors/semantic_error_monitor_device_absent"
path_semantic_error_input_device_absent = "logsim/test_text/test_semantic_errors/semantic_error_input_device_absent"
path_semantic_error_output_device_absent = "logsim/test_text/test_semantic_errors/semantic_error_output_device_absent"
path_semantic_error_device_present = "logsim/test_text/test_semantic_errors/semantic_error_device_present"
path_semantic_error_monitor_identifier_present = \
    "logsim/test_text/test_semantic_errors/semantic_error_monitor_identifier_present"
path_semantic_error_duplicate_keyword = "logsim/test_text/test_semantic_errors/semantic_error_duplicate_keyword"
path_semantic_error_input_connected = "logsim/test_text/test_semantic_errors/semantic_error_input_connected"
path_semantic_error_missing_clock_or_switch = \
    "logsim/test_text/test_semantic_errors/semantic_error_missing_clock_or_switch"
path_semantic_error_missing_input_to_pin = "logsim/test_text/test_semantic_errors/semantic_error_missing_input_to_pin"
path_semantic_error_monitor_present = "logsim/test_text/test_semantic_errors/semantic_error_monitor_present"
path_semantic_error_input_port_absent = "logsim/test_text/test_semantic_errors/semantic_error_input_port_absent"
path_semantic_error_output_port_absent = "logsim/test_text/test_semantic_errors/semantic_error_output_port_absent"
path_semantic_error_wrong_block_order = "logsim/test_text/test_semantic_errors/semantic_error_wrong_block_order"


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
        ("Line 20:", parser.error_handler.EXPECT_INITIAL_STATE),
        ("Line 26:", parser.error_handler.EXPECT_CLOCK_CYCLE),
        ("Line 31:", parser.error_handler.EXPECT_PIN_IN_OR_OUT),
        ("Line 32:", parser.error_handler.EXPECT_FULL_STOP_OR_SEMICOLON),
        ("Line 35:", parser.error_handler.EXPECT_COLON),
        ("Line 42:", parser.error_handler.EXPECT_PIN_IN),
        ("Line 43:", parser.error_handler.EXPECT_FULL_STOP_OR_ARROW),
        ("Line 44:", parser.error_handler.EXPECT_FULL_STOP),
        ("Line 45:", parser.error_handler.EXPECT_FULL_STOP),
        ("Line 46:", parser.error_handler.EXPECT_PIN_IN),
        ("Line 48:", parser.error_handler.EXPECT_VARIABLE_INPUT_NUMBER),
        ("Line 50:", parser.error_handler.EXPECT_FULL_STOP),
    ]


def all_error_2_expected_content(parser: Parser):
    return [
        ("Line 1:", parser.error_handler.WRONG_BLOCK_ORDER),
        ("Line 5:", parser.error_handler.DUPLICATE_KEYWORD),
        ("Line 12:", parser.error_handler.EXPECT_KEYWORD),
        ("Line 16:", parser.error_handler.WRONG_BLOCK_ORDER),
        parser.error_handler.MISSING_MONITOR,
        parser.error_handler.MISSING_CLOCK_OR_SWITCH
    ]


def semantic_error_monitor_device_absent_expected(parser: Parser):
    return [
        ("Line 24:", parser.monitors.MONITOR_DEVICE_ABSENT)
    ]


def semantic_error_input_device_absent_expected(parser: Parser):
    return [
        ("Line 35:", parser.network.INPUT_DEVICE_ABSENT)
    ]


def semantic_error_output_device_absent_expected(parser: Parser):
    return [
        ("Line 35:", parser.network.OUTPUT_DEVICE_ABSENT)
    ]


def semantic_error_device_present_expected(parser: Parser):
    return [
        ("Line 6:", parser.devices.DEVICE_PRESENT)
    ]


def semantic_error_monitor_identifier_present_expected(parser: Parser):
    return [
        ("Line 31:", parser.monitors.MONITOR_IDENTIFIER_PRESENT)
    ]


def semantic_error_duplicate_keyword_expected(parser: Parser):
    return [
        ("Line 17:", parser.error_handler.DUPLICATE_KEYWORD)
    ]


def semantic_error_input_connected_expected(parser: Parser):
    return [
        ("Line 30:", parser.error_handler.network.INPUT_CONNECTED)
    ]


def semantic_error_missing_clock_or_switch_expected(parser: Parser):
    return [
        parser.error_handler.MISSING_CLOCK_OR_SWITCH
    ]


def semantic_error_missing_input_to_pin_expected(parser: Parser):
    return [
        parser.error_handler.MISSING_INPUT_TO_PIN
    ]


def semantic_error_monitor_present_expected(parser: Parser):
    return [
        ("Line 24:", parser.error_handler.monitors.MONITOR_PRESENT)
    ]


def semantic_error_input_port_absent_expected(parser: Parser):
    return [
        ("Line 39:", parser.error_handler.network.INPUT_PORT_ABSENT)
    ]


def semantic_error_output_port_absent_expected(parser: Parser):
    return [
        ("Line 54:", parser.error_handler.network.OUTPUT_PORT_ABSENT)
    ]


def semantic_error_wrong_block_order_expected(parser: Parser):
    return [
        ("Line 3:", parser.error_handler.WRONG_BLOCK_ORDER)
    ]


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
    (path_all_error_2, all_error_2_expected_content),
    (path_semantic_error_monitor_device_absent, semantic_error_monitor_device_absent_expected),
    (path_semantic_error_input_device_absent, semantic_error_input_device_absent_expected),
    (path_semantic_error_output_device_absent, semantic_error_output_device_absent_expected),
    (path_semantic_error_device_present, semantic_error_device_present_expected),
    (path_semantic_error_monitor_identifier_present, semantic_error_monitor_identifier_present_expected),
    (path_semantic_error_duplicate_keyword, semantic_error_duplicate_keyword_expected),
    (path_semantic_error_input_connected, semantic_error_input_connected_expected),
    (path_semantic_error_missing_clock_or_switch, semantic_error_missing_clock_or_switch_expected),
    (path_semantic_error_missing_input_to_pin, semantic_error_missing_input_to_pin_expected),
    (path_semantic_error_monitor_present, semantic_error_monitor_present_expected),
    (path_semantic_error_input_port_absent, semantic_error_input_port_absent_expected),
    (path_semantic_error_output_port_absent, semantic_error_output_port_absent_expected),
    # (path_semantic_error_wrong_block_order, semantic_error_wrong_block_order_expected)
])
def test_parse_error(new_parser, path, expected_content):
    """Test if network error output is correct"""

    new_parser.parse_network()
    error_output = new_parser.fetch_error_output()

    for i in range(len(error_output)):
        if isinstance(error_output[i], LineTerminalOutput):
            assert (error_output[i].line_location, error_output[i].error_code) == expected_content(new_parser)[i]
        else:
            assert error_output[i].error_code == expected_content(new_parser)[i]

