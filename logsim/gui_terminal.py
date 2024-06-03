"""Implement the terminal component in the GUI.

Used in the Logic Simulator project to enable the GUI to display the console logs such as error messages.

Classes:
--------
Terminal - configures the terminal component.
"""
import wx

from gui_color import Color
from base_app import _

class Terminal:
    """Configure the terminal.

    This class provides a terminal compoent for the GUI to display console messages.

    Parameters
    ----------
    parent: parent window.

    Public methods
    --------------
    append_text(self, color, text): Handles the event of adding output messages to the terminal.

    reset_terminal(self): Resets the terminal when a new file is uploaded.
    """

    welcoming_text = _(u"Welcome to Logic Simulator\n==========================")

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

    def append_text(self, color: str, text: str) -> None:
        """Handles the event of adding output messages to the terminal."""
        self.terminal_content.SetDefaultStyle(wx.TextAttr(color))
        self.terminal_content.AppendText(text)

    def reset_terminal(self) -> None:
        """Reset terminal when new file is uploaded"""
        self.terminal_content.Clear()
        self.append_text(Color.terminal_text_color, self.welcoming_text)
