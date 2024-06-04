import sys
from unittest.mock import Mock

# Mock the wx module
sys.modules['wx'] = Mock()
sys.modules['wx'].GetTranslation = lambda x: x

