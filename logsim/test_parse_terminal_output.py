from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser

PATH = "logsim/test_text/test_extreme_errors/test_parse_bible"

names = Names()
devices = Devices(names=names)
network = Network(names=names, devices=devices)
monitors = Monitors(names=names, devices=devices, network=network)
scanner = Scanner(names=names, path=PATH)
parser = Parser(names=names, devices=devices, network=network, monitors=monitors, scanner=scanner)

parser.parse_network()
for error in parser.fetch_error_output():
    print(error)
