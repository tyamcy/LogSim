# -*- coding: utf-8 -*-
import sys
import os

import wx
import builtins
import language_const
from wx.lib.mixins.inspection import InspectionMixin

builtins.__dict__['_'] = wx.GetTranslation


def display_hook(obj):
    if obj is not None:
        print(repr(obj))


class App(wx.App, InspectionMixin):
    def __init__(self, redirect):
        super().__init__(redirect)
        sys.displayhook = display_hook

        self.app_name = "logsim"
        self.setup_configuration()
        self.locale = None
        wx.Locale.AddCatalogLookupPathPrefix('locale')
        self.update_language(self.app_config.Read(u"Language"))

    def setup_configuration(self):
        """Setup an application configuration file"""

        # locale config
        sp = wx.StandardPaths.Get()
        self.locale_config = sp.GetUserConfigDir()
        self.locale_config = os.path.join(self.locale_config, self.app_name)
        if not os.path.exists(self.locale_config):
            os.mkdir(self.locale_config)

        # app configuration
        self.app_config = wx.FileConfig(appName=self.app_name,
                                        vendorName=u'who you wish',
                                        localFilename=os.path.join(
                                       self.locale_config, "AppConfig"))
        if not self.app_config.HasEntry(u'Language'):
            self.app_config.Write(key=u'Language', value=u'en')
        self.app_config.Flush()

    def update_language(self, lang):
        """Update the language to the requested one."""
        lang = "zh"

        # if an unsupported language is requested default to English
        if lang in language_const.supported_language:
            selected_language = language_const.supported_language[lang]
            print(f"Using language '{lang}'")
        else:
            selected_language = wx.LANGUAGE_ENGLISH
            print(f"Unsupported language '{lang}', using default language 'en'")
            
        if self.locale:
            assert sys.getrefcount(self.locale) <= 2
            del self.locale
        
        # create locale object
        self.locale = wx.Locale(selected_language)
        if self.locale.IsOk():
            self.locale.AddCatalog(language_const.language_domain)
        else:
            self.locale = None

_ = wx.GetTranslation
            
