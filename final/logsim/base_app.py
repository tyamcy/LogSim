"""Implement an app with language setting that helps display the graphical user interface

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
App - creates an app for the graphical user interface with language setting.
"""
import sys
import os
import locale
import wx
from wx.lib.mixins.inspection import InspectionMixin

from logsim.internationalization import language_domain, supported_language


class App(wx.App, InspectionMixin):
    """Create an app with language setting for the graphical user interface.

    This class provides an application to hold the graphical user interface  for the
    Logic Simulator, with language display setting to change the language used
    based on the user's preference

    Parameters
    ----------
    language: language of the app

    Public methods
    --------------
    No public methods.
    """

    def __init__(self, language):
        super().__init__()
        sys.displayhook = self.display_hook
        self.locale = None

        current_file_directory = os.path.dirname(os.path.abspath(__file__))
        language_directory = os.path.join(current_file_directory, 'language')
        wx.Locale.AddCatalogLookupPathPrefix(language_directory)

        self.update_language(language)

    def update_language(self, language):
        """Update the language to the requested one."""
        # if the input language is supported, use the language
        if language and language.lower() in supported_language:
            selected_language = supported_language[language.lower()]
        else:
            # if there is no language input, use system default language if supported, else use English
            if not language:
                language = ".".join(locale.getdefaultlocale())
                if language.lower() in supported_language:
                    selected_language = supported_language[language.lower()]
                else:
                    print(f"System language '{language}' is not supported, using default language 'en_GB.UTF-8'")
                    selected_language = wx.LANGUAGE_ENGLISH
            # if the input language is not supported, use English
            else:
                print(f"Language '{language}' is not supported, using default language 'en_GB.UTF-8'")
                selected_language = wx.LANGUAGE_ENGLISH

        if self.locale:
            assert sys.getrefcount(self.locale) <= 2
            del self.locale

        # create locale object
        self.locale = wx.Locale(selected_language)
        if self.locale.IsOk():
            self.locale.AddCatalog(language_domain)
        else:
            self.locale = None

    def display_hook(self, obj):
        """Install a custom displayhook to keep Python from setting the global _ (underscore)
        to the value of the last evaluated expression.

        If we don't do this, our mapping of _ to gettext can get overwritten.

        This is useful/needed in interactive debugging with PyShell.
        """
        if obj is not None:
            print(repr(obj))
