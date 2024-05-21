import pytest

from scanner import Scanner
from names import Names

path = "logsim/test_scanner_text"


#  test the scanner module with the human verified results from test_scanner_text
test_type_list = [7, 5, 9, 2, 8, 1, 6, 7, 5, 9, 2, 9, 0, 8, 1, 6, 7, 5, 9, 4, 9, 3, 9, 9, 4, 9, 3, 9, 1, 9, 4, 9, 3, 9, 1, None, 9, 3, 9, 4, 9, 3, 9, 1, 6, 10]
test_id_list = [1, None, 5, None, '10', None, None, 0, None, 6, None, 7, None, '3', None, None, 4, None, 5, None, 8, None, 9, 10, None, 8, None, 11, None, 12, None, 13, None, 14, None, None, 8, None, 15, None, 13, None, 16, None, None, None]

@pytest.fixture
def new_scanner():
    names = Names()
    new_scanner = Scanner(path=path, names=names)
    return new_scanner


def test_get_symbol(new_scanner):
    for i in range(len(test_type_list)):
        symbol = new_scanner.get_symbol()
        assert symbol.type == test_type_list[i]
        assert symbol.id == test_id_list[i]


def test_scanner_init(new_scanner):
    names = Names()
    with pytest.raises(TypeError):
        scanner = Scanner(path=1, names=names)
    with pytest.raises(TypeError):
        scanner = Scanner(path=path, names="name")
