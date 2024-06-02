import wx

def init_locale():
    """Initialize wx.locale."""
    locale = wx.Locale(wx.LANGUAGE_ENGLISH_UK)
    if locale.IsOk():
        locale.AddCatalogLookupPathPrefix("locale")
        locale.AddCatalog("gui")
    else:
        locale = None

_ = wx.GetTranslation