from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parser_handler import ParserErrorHandler
from parse import Parser

PATH = "test_parser_1"

names = Names()
devices = Devices(names=names)
network = Network(names=names, devices=devices)
monitors = Monitors(names=names, devices=devices, network=network)
scanner = Scanner(names=names, path=PATH)
parser = Parser(names=names, devices=devices, network=network, monitors=monitors, scanner=scanner)

print(parser.parse_network())
for error in parser.fetch_error_output():
    print(error)
