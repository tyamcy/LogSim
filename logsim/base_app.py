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
            print(f"Using language '{language}'")
        else:
            selected_language = wx.LANGUAGE_ENGLISH
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
        if obj is not None:
            print(repr(obj))

