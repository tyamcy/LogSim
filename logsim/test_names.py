"""Test the names module."""
import pytest

from names import Names


@pytest.fixture
def new_names():
    """Return a new names instance."""
    return Names()


@pytest.fixture
def name_string_list():
    """Return a list of example names."""
    return ["DEVICE", "g1", "1234", ";"]


@pytest.fixture
def used_names(name_string_list):
    """Return a names instance, after four names have been added."""
    names = Names()
    names.lookup(name_string_list)
    return names


def test_unique_error_code(new_names):
    [error_code_1] = new_names.unique_error_codes(1)
    [error_code_2] = new_names.unique_error_codes(1)
    assert error_code_1 != error_code_2


def test_unique_error_code_raise_exception(new_names):
    """Test if unique_error_code raises expected exceptions."""
    with pytest.raises(TypeError):
        new_names.unique_error_codes(1.4)
    with pytest.raises(TypeError):
        new_names.unique_error_codes("hello")
    with pytest.raises(ValueError):
        new_names.unique_error_codes(-1)


@pytest.mark.parametrize("string, expected_id", [
    ("DEVICE", 0),
    ("g1", 1),
    ("1234", 2),
    (";", 3),
    (">", None)
])
def test_query(new_names, used_names, string, expected_id):
    """Test if query returns the expected ID."""
    # Name is present
    assert used_names.query(string) == expected_id
    # Name is absent
    assert new_names.query(string) is None


def test_lookup(new_names, used_names, name_string_list):
    """Test if lookup returns the expected ID list."""
    assert used_names.lookup(name_string_list) == [0, 1, 2, 3]
    assert new_names.lookup(name_string_list) == [0, 1, 2, 3]


@pytest.mark.parametrize("name_id, expected_string", [
    (0, "DEVICE"),
    (1, "g1"),
    (2, "1234"),
    (3, ";"),
    (4, None)
])
def test_get_name_string(new_names, used_names, name_id, expected_string):
    """Test if get_string returns the expected string."""
    # Name is present
    assert used_names.get_name_string(name_id) == expected_string
    # Name is absent
    assert new_names.get_name_string(name_id) is None


