"""Map variable names and string names to unique integers.

Used in the Logic Simulator project. Most of the modules in the project
use this module either directly or indirectly.

Classes
-------
Names - maps variable names and string names to unique integers.
"""

from typing import List


class Names:

    """Map variable names and string names to unique integers.

    This class deals with storing grammatical keywords and user-defined words,
    and their corresponding name IDs, which are internal indexing integers. It
    provides functions for looking up either the name ID or the name string.
    It also keeps track of the number of error codes defined by other classes,
    and allocates new, unique error codes on demand.

    Parameters
    ----------
    No parameters.

    Public methods
    -------------
    unique_error_codes(self, num_error_codes): Returns a list of unique integer
                                               error codes.

    query(self, name_string): Returns the corresponding name ID for the
                        name string. Returns None if the string is not present.

    lookup(self, name_string_list): Returns a list of name IDs for each
                        name string. Adds a name if not already present.

    get_name_string(self, name_id): Returns the corresponding name string for
                        the name ID. Returns None if the ID is not present.
    """

    def __init__(self):
        """Initialise names list."""
        self.error_code_count = 0  # how many error codes have been declared
        self.id_count = 0  # how many name IDs have been assigned
        self.id_to_name = {}  # {name ID: name string}
        self.name_to_id = {}  # {name string: name ID}

    def unique_error_codes(self, num_error_codes: int) -> range:
        """Return a list of unique integer error codes."""
        if not isinstance(num_error_codes, int):
            raise TypeError("Expected num_error_codes to be an integer.")
        if num_error_codes <= 0:
            raise ValueError("Expected num_error_codes to be a positive integer")
        self.error_code_count += num_error_codes
        return range(self.error_code_count - num_error_codes,
                     self.error_code_count)

    def query(self, name_string: str) -> int:
        """Return the corresponding name ID for name_string.

        If the name string is not present in the names list, return None.
        """
        if not isinstance(name_string, str):
            raise TypeError("Expected name_string to be a string.")
        return self.name_to_id.get(name_string)

    def lookup(self, name_string_list: List[str]) -> List[int]:
        """Return a list of name IDs for each name string in name_string_list.

        If the name string is not present in the names list, add it.
        """
        if not isinstance(name_string_list, list):
            raise TypeError("Expected name_string_list to be a list.")
        id_list = []  # initialises an empty name IDs list for the lookup results
        for name in name_string_list:
            if not isinstance(name, str):
                raise TypeError("Expected all values in name_string_list to be strings.")
            if name not in self.name_to_id:
                # adding the new name string to both hashmaps, with current id_count as the name ID
                self.name_to_id[name] = self.id_count
                self.id_to_name[self.id_count] = name
                self.id_count += 1
            # adding the name ID corresponding to the name string to the lookup results list
            id_list.append(self.name_to_id[name])
        return id_list

    def get_name_string(self, name_id: int) -> str:
        """Return the corresponding name string for name_id.

        If the name_id is not an index in the names list, return None.
        """
        if not isinstance(name_id, int):
            raise TypeError("Expected name_id to be an integer.")
        return self.id_to_name.get(name_id)
