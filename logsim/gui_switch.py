import wx

from gui_color import Color


class Switch:
    def __init__(self, parent):
        self.gui = parent

        self.switches_sizer = wx.BoxSizer(wx.VERTICAL)
        self.switches_text = wx.StaticText(parent, wx.ID_ANY, "Switches")
        self.switches_scrolled = wx.ScrolledWindow(parent, style=wx.VSCROLL)
        self.switches_scrolled.SetScrollRate(10, 10)
        self.switches_scrolled_sizer = wx.BoxSizer(wx.VERTICAL)

        self.switches_scrolled.SetSizer(self.switches_scrolled_sizer)
        self.switches_scrolled.SetMinSize((250, 150))
        self.switches_scrolled.SetBackgroundColour(Color.light_background_secondary)

        self.switches_sizer.Add(self.switches_text, 0, wx.ALL, 5)
        self.switches_sizer.Add(self.switches_scrolled, 1, wx.EXPAND | wx.ALL, 5)

    def on_toggle_switch(self, event) -> None:
        """Handle the event when the user toggles a switch."""
        button = event.GetEventObject()
        is_on = button.GetValue()  # toggle button is on when clicked (value 1)
        switch_name = self.gui.toggle_button_switch_name[button.GetId()]
        switch_id = self.gui.names.query(switch_name)

        if is_on:
            button.SetLabel("1")
            self.gui.switches_dict[switch_name] = 1
            self.gui.devices.set_switch(switch_id, 1)
        else:
            button.SetLabel("0")
            self.gui.switches_dict[switch_name] = 0
            self.gui.devices.set_switch(switch_id, 0)
        self.gui.Refresh()
