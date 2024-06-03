"""Implement an app with language setting that helps display the graphical user interface

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
App - creates an app for the graphical user interface with language setting.
"""
import sys
import wx
from wx.lib.mixins.inspection import InspectionMixin

language_domain = "gui"
supported_language = {
    u"en": wx.LANGUAGE_ENGLISH,
    u"zh": wx.LANGUAGE_CHINESE_HONGKONG
}
_ = wx.GetTranslation


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
        wx.Locale.AddCatalogLookupPathPrefix('locale')
        self.update_language(language)

    def update_language(self, language):
        """Update the language to the requested one."""

        # if an unsupported language is requested default to English
        if language in supported_language:
            selected_language = supported_language[language]
        else:
            selected_language = wx.LANGUAGE_ENGLISH
            if language:
                print(f"Unsupported language '{language}', using default language 'en'")
            
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

