import wx

from gui_color import Color


class UploadButton(wx.Button):
    def __init__(self, parent, function, label="Upload"):
        super().__init__(parent, label=label)
        self.SetBackgroundColour(Color.color_primary)
        self.Bind(wx.EVT_BUTTON, function)


class RunButton(wx.Button):
    def __init__(self, parent, function, label="Run"):
        super().__init__(parent, label=label)
        self.SetBackgroundColour(Color.color_primary)
        self.Bind(wx.EVT_BUTTON, function)


class ContinueButton(wx.Button):
    def __init__(self, parent, function, label="Continue"):
        super().__init__(parent, label=label)
        self.SetBackgroundColour(Color.color_disabled)
        self.Bind(wx.EVT_BUTTON, function)
        self.Disable()


class MonitorAddButton(wx.Button):
    def __init__(self, parent, function, label="Add"):
        super().__init__(parent, label=label)
        self.SetBackgroundColour(Color.light_button_color)
        self.Bind(wx.EVT_BUTTON, function)


class MonitorRemoveButton(wx.Button):
    def __init__(self, parent, function, label="Remove"):
        super().__init__(parent, label=label)
        self.SetBackgroundColour(Color.light_button_color)
        self.Bind(wx.EVT_BUTTON, function)
