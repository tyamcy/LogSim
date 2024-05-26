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


def new_parser(path):
    """Return a new instance of the Parser class."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner(path, names)

    return Parser(names, devices, network, monitors, scanner)


@pytest.fixture
def another_parser():
    """Return a new instance of the Parser class."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner(path_correct, names)

    return Parser(names, devices, network, monitors, scanner)


@pytest.mark.parametrize("path, expected_result", [
    (path_correct, True),
    (path_wrong_order, False),
    (path_wrong_content, False)
])
def test_parse_network(another_parser, path, expected_result):
    """Test if network parses correctly."""

    assert another_parser.parse_network() == expected_result
