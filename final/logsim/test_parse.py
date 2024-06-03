"""Test the parse module."""
import pytest

from typing import List, Union, Tuple

from logsim.parse import Parser
from logsim.parser_handler import LineTerminalOutput
from logsim.names import Names
from logsim.devices import Devices
from logsim.network import Network
from logsim.monitors import Monitors
from logsim.scanner import Scanner

path_correct = "final/logsim/test_text/test_parse_correct_text.txt"
path_wrong_order = "final/logsim/test_text/test_parse_wrong_order_text.txt"
path_wrong_content = "final/logsim/test_text/test_parse_wrong_content_text.txt"

path_all_error_1 = "final/logsim/test_text/test_parse_all_error_1.txt"
path_all_error_2 = "final/logsim/test_text/test_parse_all_error_2.txt"
path_all_error_3 = "final/logsim/test_text/test_parse_all_error_3.txt"

path_semantic_error_monitor_device_absent = \
    "final/logsim/test_text/test_semantic_errors/semantic_error_monitor_device_absent.txt"
path_semantic_error_input_device_absent = "final/logsim/test_text/test_semantic_errors/semantic_error_input_device_absent.txt"
path_semantic_error_output_device_absent = \
    "final/logsim/test_text/test_semantic_errors/semantic_error_output_device_absent.txt"
path_semantic_error_device_present = "final/logsim/test_text/test_semantic_errors/semantic_error_device_present.txt"
path_semantic_error_monitor_identifier_present = \
    "final/logsim/test_text/test_semantic_errors/semantic_error_monitor_identifier_present.txt"
path_semantic_error_duplicate_keyword = "final/logsim/test_text/test_semantic_errors/semantic_error_duplicate_keyword.txt"
path_semantic_error_input_connected = "final/logsim/test_text/test_semantic_errors/semantic_error_input_connected.txt"
path_semantic_error_missing_clock_or_switch = \
    "final/logsim/test_text/test_semantic_errors/semantic_error_missing_clock_or_switch.txt"
path_semantic_error_missing_input_to_pin = \
    "final/logsim/test_text/test_semantic_errors/semantic_error_missing_input_to_pin.txt"
path_semantic_error_monitor_present = "final/logsim/test_text/test_semantic_errors/semantic_error_monitor_present.txt"
path_semantic_error_input_port_absent = \
    "final/logsim/test_text/test_semantic_errors/semantic_error_input_port_absent.txt"
path_semantic_error_output_port_absent = \
    "final/logsim/test_text/test_semantic_errors/semantic_error_output_port_absent.txt"
path_semantic_error_monitor_port_absent = \
    "final/logsim/test_text/test_semantic_errors/semantic_error_monitor_port_absent.txt"
path_semantic_error_wrong_block_order = \
    "final/logsim/test_text/test_semantic_errors/semantic_error_wrong_block_order.txt"

path_bible = "final/logsim/test_text/test_extreme_errors/test_parse_bible.txt"
path_curly_brackets = "final/logsim/test_text/test_extreme_errors/test_parse_curly_brackets.txt"
path_empty = "final/logsim/test_text/test_extreme_errors/test_parse_empty.txt"
path_lorem_ipsum = "final/logsim/test_text/test_extreme_errors/test_parse_lorem_ipsum.txt"
path_semi_colon = "final/logsim/test_text/test_extreme_errors/test_parse_semi_colon.txt"

path_correct_2 = "final/logsim/test_text/test_parse_correct_text_2.txt"
path_correct_3 = "final/logsim/test_text/test_parse_correct_text_3.txt"
path_correct_4 = "final/logsim/test_text/test_parse_correct_text_4.txt"
path_test_parse_oscillating = "final/logsim/test_text/test_parse_oscillating.txt"

@pytest.fixture
def new_parser(path: str) -> Parser:
    """Return a new instance of the Parser class."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner(path, names)

    return Parser(names, devices, network, monitors, scanner)


def all_error_1_expected_content(parser: Parser) -> List[Tuple[str, int]]:
    """Construct the reference error list for all_error_1 file"""
    return [
        ("Line 3:", parser.error_handler.EXPECT_IDENTIFIER),
        ("Line 4:", parser.error_handler.EXPECT_INPUT_DEVICE),
        ("Line 5:", parser.error_handler.EXPECT_INPUT_DEVICE),
        ("Line 7:", parser.error_handler.EXPECT_COLON),
        ("Line 8:", parser.error_handler.EXPECT_VARIABLE_INPUT_NUMBER),
        ("Line 9:", parser.error_handler.EXPECT_COMMA),
        ("Line 10:", parser.error_handler.EXPECT_SEMICOLON),
        ("Line 13:", parser.error_handler.EXPECT_RC_TRIGGER_CYCLE),
        ("Line 21:", parser.error_handler.EXPECT_INITIAL_STATE),
        ("Line 27:", parser.error_handler.EXPECT_CLOCK_CYCLE),
        ("Line 32:", parser.error_handler.EXPECT_PIN_IN_OR_OUT),
        ("Line 33:", parser.error_handler.EXPECT_FULL_STOP_OR_SEMICOLON),
        ("Line 36:", parser.error_handler.EXPECT_COLON),
        ("Line 43:", parser.error_handler.EXPECT_PIN_IN),
        ("Line 44:", parser.error_handler.EXPECT_FULL_STOP_OR_ARROW),
        ("Line 45:", parser.error_handler.EXPECT_FULL_STOP),
        ("Line 46:", parser.error_handler.EXPECT_FULL_STOP),
        ("Line 47:", parser.error_handler.EXPECT_PIN_IN),
        ("Line 49:", parser.error_handler.EXPECT_PIN_IN),
        ("Line 51:", parser.error_handler.EXPECT_FULL_STOP),
        ("Line 68:", parser.error_handler.EXPECT_CLOSE_CURLY_BRACKET)
    ]


def all_error_2_expected_content(parser: Parser) -> Union[int, List[Tuple[str, int]]]:
    """Construct the reference error list for all_error_2 file"""
    return [
        ("Line 1:", parser.error_handler.WRONG_BLOCK_ORDER),
        ("Line 5:", parser.error_handler.DUPLICATE_KEYWORD),
        ("Line 12:", parser.error_handler.EXPECT_KEYWORD),
        ("Line 16:", parser.error_handler.WRONG_BLOCK_ORDER),
        parser.error_handler.MISSING_MONITOR,
        parser.error_handler.MISSING_CLOCK_OR_SWITCH
    ]


def all_error_3_expected_content(parser: Parser) -> Union[int, List[Tuple[str, int]]]:
    """Construct the reference error list for all_error_3 file"""
    return [
        ("Line 21:", parser.error_handler.EXPECT_OPEN_CURLY_BRACKET),
        ("Line 37:", parser.error_handler.EXPECT_FULL_STOP),
        ("Line 42:", parser.error_handler.EXPECT_PIN_OUT),
        ("Line 43:", parser.error_handler.EXPECT_ARROW),
        ("Line 44:", parser.error_handler.EXPECT_PIN_IN),
        parser.error_handler.MISSING_MONITOR
    ]


def semantic_error_monitor_device_absent_expected(parser: Parser):
    """Construct the reference error list for semantic_error_monitor_device_absent.txt file"""
    return [
        ("Line 24:", parser.monitors.MONITOR_DEVICE_ABSENT)
    ]


def semantic_error_input_device_absent_expected(parser: Parser):
    """Construct the reference error list for semantic_error_input_device_absent.txt file"""
    return [
        ("Line 35:", parser.network.INPUT_DEVICE_ABSENT)
    ]


def semantic_error_output_device_absent_expected(parser: Parser):
    """Construct the reference error list for semantic_error_output_device_absent.txt file"""
    return [
        ("Line 35:", parser.network.OUTPUT_DEVICE_ABSENT)
    ]


def semantic_error_device_present_expected(parser: Parser):
    """Construct the reference error list for semantic_error_device_present.txt file"""
    return [
        ("Line 6:", parser.devices.DEVICE_PRESENT)
    ]


def semantic_error_monitor_identifier_present_expected(parser: Parser):
    """Construct the reference error list for semantic_error_monitor_identifier_present.txt file"""
    return [
        ("Line 31:", parser.monitors.MONITOR_IDENTIFIER_PRESENT)
    ]


def semantic_error_duplicate_keyword_expected(parser: Parser):
    """Construct the reference error list for semantic_error_duplicate_keyword.txt file"""
    return [
        ("Line 17:", parser.error_handler.DUPLICATE_KEYWORD)
    ]


def semantic_error_input_connected_expected(parser: Parser):
    """Construct the reference error list for semantic_error_input_connected.txt file"""
    return [
        ("Line 30:", parser.error_handler.network.INPUT_CONNECTED)
    ]


def semantic_error_missing_clock_or_switch_expected(parser: Parser):
    """Construct the reference error list for semantic_error_missing_clock_or_switch.txt file"""
    return [
        parser.error_handler.MISSING_CLOCK_OR_SWITCH
    ]


def semantic_error_missing_input_to_pin_expected(parser: Parser):
    """Construct the reference error list for semantic_error_missing_input_to_pin.txt file"""
    return [
        parser.error_handler.MISSING_INPUT_TO_PIN
    ]


def semantic_error_monitor_present_expected(parser: Parser):
    """Construct the reference error list for semantic_error_monitor_present.txt file"""
    return [
        ("Line 24:", parser.error_handler.monitors.MONITOR_PRESENT)
    ]


def semantic_error_input_port_absent_expected(parser: Parser):
    """Construct the reference error list for semantic_error_input_port_absent.txt file"""
    return [
        ("Line 39:", parser.error_handler.network.INPUT_PORT_ABSENT)
    ]


def semantic_error_output_port_absent_expected(parser: Parser):
    """Construct the reference error list for semantic_error_output_port_absent.txt file"""
    return [
        ("Line 54:", parser.error_handler.network.OUTPUT_PORT_ABSENT)
    ]


def semantic_error_monitor_port_absent_expected(parser: Parser):
    """Construct the reference error list for semantic_error_monitor_port_absent.txt file"""
    return [
        ("Line 27:", parser.error_handler.monitors.MONITOR_PORT_ABSENT)
    ]


def semantic_error_wrong_block_order_expected(parser: Parser):
    """Construct the reference error list for semantic_error_wrong_block_order.txt file"""
    return [
        ("Line 3:", parser.error_handler.WRONG_BLOCK_ORDER),
        ("Line 18:", parser.error_handler.WRONG_BLOCK_ORDER),
        ("Line 25:", parser.error_handler.WRONG_BLOCK_ORDER),
        ("Line 32:", parser.error_handler.WRONG_BLOCK_ORDER),
        ("Line 37:", parser.error_handler.WRONG_BLOCK_ORDER)
    ]


@pytest.mark.parametrize("path, expected_result", [
    (path_correct, True),
    (path_correct_2, True),
    (path_correct_3, True),
    (path_correct_4, True),
    (path_test_parse_oscillating, True),
    (path_wrong_order, False),
    (path_wrong_content, False)
])
def test_parse_network(new_parser, path, expected_result):
    """Test if network parses correctly."""

    assert new_parser.parse_network() == expected_result


@pytest.mark.parametrize("path, expected_content", [
    (path_all_error_1, all_error_1_expected_content),
    (path_all_error_2, all_error_2_expected_content),
    (path_all_error_3, all_error_3_expected_content),
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
    (path_semantic_error_monitor_port_absent, semantic_error_monitor_port_absent_expected),
    (path_semantic_error_wrong_block_order, semantic_error_wrong_block_order_expected)
])
def test_parse_error(new_parser, path, expected_content):
    """Test if network error output is correct."""

    new_parser.parse_network()
    error_output = new_parser.fetch_error_output()

    for i in range(len(error_output)):
        if isinstance(error_output[i], LineTerminalOutput):
            assert (error_output[i].line_location, error_output[i].error_code) == expected_content(new_parser)[i]
        else:
            assert error_output[i].error_code == expected_content(new_parser)[i]


@pytest.mark.parametrize("path", [
    path_bible, path_curly_brackets, path_empty, path_lorem_ipsum, path_semi_colon
])
def test_parse_extreme_error(new_parser, path):
    """Test if network could be parsed without crashing the parser."""

    assert not new_parser.parse_network()
