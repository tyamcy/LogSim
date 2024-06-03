#!/usr/bin/env python3
"""Parse command line options and arguments for the Logic Simulator.

This script parses options and arguments specified on the command line, and
runs either the command line user interface or the graphical user interface.

Usage
-----
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface: logsim.py <file path>
"""
import getopt
import os
import sys
from contextlib import contextmanager

import base_app
from typing import List
from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from userint import UserInterface
from gui import Gui


@contextmanager
def scanner_init_error_handler(path: str) -> None:
    """Context manager to handle initialization errors for scanner"""
    try:
        yield
    except FileNotFoundError:
        print(f"Error: no such file '{path}'")
        sys.exit()
    except UnicodeDecodeError:
        print(f"Error: file '{path}' is not a unicode text file")
        sys.exit()


def main(arg_list: List[str]) -> None:
    """Parse the command line options and arguments specified in arg_list.

    Run either the command line user interface, the graphical user interface,
    or display the usage message.
    """
    usage_message = ("Usage:\n"
                     "Show help: logsim.py -h\n"
                     "Command line user interface: logsim.py -c <file path>\n"
                     "Graphical user interface: logsim.py <file path>")
    parsing_message = "Assembling logic circuit..."
    try:
        options, arguments = getopt.getopt(arg_list, "hc:")
    except getopt.GetoptError:
        print("Error: invalid command line arguments\n")
        print(usage_message)
        sys.exit()

    # Initialise instances of the four inner simulator classes
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    for option, path in options:
        if option == "-h":  # print the usage message
            print(usage_message)
            sys.exit()
        elif option == "-c":  # use the command line user interface
            with scanner_init_error_handler(path):
                scanner = Scanner(path, names)
            parser = Parser(names, devices, network, monitors, scanner)
            print(parsing_message)
            if parser.parse_network():
                # Initialise an instance of the userint.UserInterface() class
                userint = UserInterface(names, devices, network, monitors)
                userint.command_interface()
            else:
                print(f"\u001b[31m\nError in the specification file\n{path}.\u001b[0m")
                for error in parser.fetch_error_output():
                    print(error)

    if not options:  # no option given, use the graphical user interface

        if len(arguments) != 1:  # wrong number of arguments
            print("Error: one file path required\n")
            print(usage_message)
            sys.exit()

        [path] = arguments
        with scanner_init_error_handler(path):
            scanner = Scanner(path, names)
        parser = Parser(names, devices, network, monitors, scanner)

        # It is possible to provide a file that is wrong initially
        # An error will be given in the GUI terminal
        # Initialise an instance of the gui.Gui() class
        language = os.environ.get("LANG")
        app = base_app.App(language)
        gui = Gui("Logic Simulator", path, parser)
        gui.Show(True)
        app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
