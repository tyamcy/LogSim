import wx

from gui_color import Color

class Terminal:
    welcoming_text = "Welcome to Logic Simulator\n=========================="

    def __init__(self, parent):
        self.border_panel = wx.Panel(parent)
        self.border_panel.SetBackgroundColour(Color.terminal_background_color)
        self.terminal_panel = wx.Panel(self.border_panel)
        self.terminal_panel.SetBackgroundColour(Color.terminal_background_color)

        self.terminal_content = wx.TextCtrl(self.terminal_panel,
                                            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.BORDER_NONE)
        self.terminal_content.SetBackgroundColour(Color.terminal_background_color)
        self.terminal_content.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Consolas'))
        self.terminal_content.SetForegroundColour(Color.terminal_text_color)
        self.terminal_content.AppendText(self.welcoming_text)

        self.terminal_sizer = wx.BoxSizer(wx.VERTICAL)
        self.terminal_sizer.Add(self.terminal_content, 1, wx.EXPAND | wx.ALL, 0)
        self.terminal_panel.SetSizer(self.terminal_sizer)

        self.border_sizer = wx.BoxSizer(wx.VERTICAL)
        self.border_sizer.Add(self.terminal_panel, 1, wx.EXPAND | wx.ALL, 10)
        self.border_panel.SetSizer(self.border_sizer)
