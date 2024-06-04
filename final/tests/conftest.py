"""Mock wx module for GitHub workflow to run pytest without installing wxPython."""
import sys
from unittest.mock import Mock

sys.modules['wx'] = Mock()
sys.modules['wx'].GetTranslation = lambda x: x

