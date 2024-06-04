"""Handles translation and provides language metadata."""
import wx

_ = wx.GetTranslation

language_domain = "gui"
supported_language = {
    u"en_GB": wx.LANGUAGE_ENGLISH_UK,
    u"zh_HK": wx.LANGUAGE_CHINESE_HONGKONG
}
