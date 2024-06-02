import wx

from gui_color import Color
from internationalization import _

class Switch:
    def __init__(self, parent):
        self.gui = parent

        # Creating a dictionary of switches
        self.id_switches = parent.devices.find_devices(parent.devices.SWITCH)
        self.switches_dict = dict()  # {switch name: switch state}
        self.toggle_button_switch_name = dict()  # {toggle button: switch name}

        self.switches_sizer = wx.BoxSizer(wx.VERTICAL)
        self.switches_text = wx.StaticText(parent, wx.ID_ANY, _(u"Switches"))
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
        switch_name = self.toggle_button_switch_name[button.GetId()]
        switch_id = self.gui.names.query(switch_name)

        if is_on:
            button.SetLabel("1")
            self.switches_dict[switch_name] = 1
            self.gui.devices.set_switch(switch_id, 1)
        else:
            button.SetLabel("0")
            self.switches_dict[switch_name] = 0
            self.gui.devices.set_switch(switch_id, 0)
        self.gui.Refresh()
        
    def update_switches_display(self) -> None:
        """Handle the event of updating the displayed list of switches."""
        # Creating a dictionary of switches
        self.id_switches = self.gui.devices.find_devices(self.gui.devices.SWITCH)
        self.switches_dict = dict()  # {switch name string: switch state}

        for switch_id in self.id_switches:
            switch_name = self.gui.names.get_name_string(switch_id)
            switch_state = self.gui.devices.get_device(switch_id).switch_state
            self.switches_dict[switch_name] = switch_state

        self.switches_scrolled_sizer.Clear(True)

        for switch, state in self.switches_dict.items():
            switch_sizer = wx.BoxSizer(wx.HORIZONTAL)

            label = wx.StaticText(self.switches_scrolled, wx.ID_ANY, switch)
            switch_sizer.Add(label, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)

            initial_label = "1" if state == 1 else "0"
            toggle = wx.ToggleButton(self.switches_scrolled, wx.ID_ANY, initial_label)
            toggle.SetValue(state == 1)
            toggle.SetBackgroundColour(Color.light_button_color)
            toggle.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle_switch)

            if self.gui.theme == "light":
                label.SetForegroundColour(Color.light_text_color)
                toggle.SetForegroundColour(Color.light_text_color)
                toggle.SetBackgroundColour(Color.light_button_color)
            elif self.gui.theme == "dark":
                label.SetForegroundColour(Color.dark_text_color)
                toggle.SetForegroundColour(Color.dark_text_color)
                toggle.SetBackgroundColour(Color.dark_button_color)

            self.toggle_button_switch_name[toggle.GetId()] = switch

            switch_sizer.Add(toggle, 0, wx.ALIGN_CENTER_VERTICAL)

            self.switches_scrolled_sizer.Add(switch_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.switches_scrolled.SetSizer(self.switches_scrolled_sizer)
        self.switches_scrolled.Layout()
        self.switches_scrolled_sizer.FitInside(self.switches_scrolled)
        self.switches_scrolled_sizer.Layout()
