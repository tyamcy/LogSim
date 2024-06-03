"""Implement pop up dialog boxes for the GUI.

Used in the Logic Simulator project to enable pop up dialog boxes for selection.

Classes:
--------
CustomDialogBox - custom dialog box for the add and remove buttons.
IdentifierInputDialog - custom dialog box to input an identifier for the monitor.
"""
from typing import Optional

import wx

from logsim.gui_widgets.color import Color


class CustomDialogBox(wx.Dialog):
    """Custom dialog box for the add and remove buttons.

    Parameters
    ----------
    parent: parent window.
    title: title of the dialog box.
    message: message to display on the dialog box.
    choices: options listed in the dialog box. 
    theme: colour theme of the GUI.

    Public methods
    --------------
    get_selected_item(self): Return the selected item.
    """

    def __init__(self, parent, title: str, message: str, choices: list, theme: str):
        """Initializes the layout and styling of the dialog box."""
        super().__init__(parent, title=title)
        self.selection = None

        sizer = wx.BoxSizer(wx.VERTICAL)

        text = wx.StaticText(self, label=message)
        sizer.Add(text, flag=wx.ALL, border=5)

        self.list_box = wx.ListBox(self, choices=choices, style=wx.LB_SINGLE | wx.LB_NEEDED_SB)
        self.list_box.SetSizeHints(minSize=(250, 150))

        if theme == "light":
            self.list_box.SetBackgroundColour(Color.light_background_secondary)
            self.list_box.SetForegroundColour(Color.light_text_color)
            self.SetBackgroundColour(Color.light_background_color)
            self.SetForegroundColour(Color.light_text_color)
            text.SetForegroundColour(Color.light_text_color)
        elif theme == "dark":
            self.list_box.SetBackgroundColour(Color.dark_background_secondary)
            self.list_box.SetForegroundColour(Color.dark_text_color)
            self.SetBackgroundColour(Color.dark_background_color)
            self.SetForegroundColour(Color.dark_text_color)
            text.SetForegroundColour(Color.dark_text_color)

        sizer.Add(self.list_box, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        sizer.Add(button_sizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(sizer)
        self.Fit()

    def get_selected_item(self) -> Optional[str]:
        """Return the selected item."""
        selection_index = self.list_box.GetSelection()
        if selection_index != wx.NOT_FOUND:
            return self.list_box.GetString(selection_index)
        return None


class IdentifierInputDialog(wx.Dialog):
    """Custom dialog box to input an identifier for the monitor.

    Parameters
    ----------
    parent : parent window.
    title : title of the dialog box.
    message : message to display on the dialog box.
    theme : color theme of the GUI.

    Public methods
    --------------
    get_identifier(self): Return the entered identifier from the text control.
    """

    def __init__(self, parent, title: str, message: str, theme: str):
        """Initializes the layout and styling of the dialog box."""
        super().__init__(parent, title=title)

        self.theme = theme

        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, label=message)
        sizer.Add(label, flag=wx.ALL, border=10)

        self.text_ctrl = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.text_ctrl, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        # Apply theme settings
        if self.theme == "light":
            self.SetBackgroundColour(Color.light_background_color)
            self.text_ctrl.SetForegroundColour(Color.light_text_color)
            self.text_ctrl.SetBackgroundColour(Color.light_background_secondary)
            label.SetForegroundColour(Color.light_text_color)
        elif self.theme == "dark":
            self.SetBackgroundColour(Color.dark_background_color)
            self.text_ctrl.SetForegroundColour(Color.dark_text_color)
            self.text_ctrl.SetBackgroundColour(Color.dark_background_secondary)
            label.SetForegroundColour(Color.dark_text_color)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        sizer.Add(button_sizer, flag=wx.EXPAND | wx.ALL, border=10)

        self.SetSizer(sizer)
        self.Fit()

    def get_identifier(self) -> str:
        """Return the entered identifier from the text control."""
        return self.text_ctrl.GetValue()
