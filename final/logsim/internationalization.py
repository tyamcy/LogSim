"""Handles translation and provides language metadata."""
import wx

_ = wx.GetTranslation

language_domain = "gui"
supported_language = {
    u"en_gb.utf-8": wx.LANGUAGE_ENGLISH_UK,
    u"zh_hk.utf-8": wx.LANGUAGE_CHINESE_HONGKONG
}
