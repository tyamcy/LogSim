import wx

from gui_color import Color


class MonitorsList:
    def __init__(self, parent):
        self.gui = parent

        self.monitors_sizer = wx.BoxSizer(wx.VERTICAL)
        self.monitors_text = wx.StaticText(parent, wx.ID_ANY, "Monitors")
        self.monitors_scrolled = wx.ScrolledWindow(parent, style=wx.VSCROLL)
        self.monitors_scrolled.SetScrollRate(10, 10)
        self.monitors_scrolled_sizer = wx.BoxSizer(wx.VERTICAL)

        self.monitors_scrolled.SetMinSize((250, 150))
        self.monitors_scrolled.SetBackgroundColour(Color.light_background_secondary)
        self.monitors_sizer.Add(self.monitors_text, 0, wx.ALL, 5)
        self.monitors_sizer.Add(self.monitors_scrolled, 1, wx.EXPAND | wx.ALL, 5)

    def update_monitors_list(self) -> None:
        """Handle the event of updating the list of monitors upon change."""
        self.monitors_scrolled_sizer.Clear(True)

        # Change text colour depending on theme
        if self.gui.theme == "light":
            color = Color.light_text_color
        else:
            color = Color.dark_text_color

        if not self.gui.monitors.get_all_identifiers():
            # Empty list, displays a message saying "No active monitors"
            no_monitor_text = wx.StaticText(self.monitors_scrolled, wx.ID_ANY, "No active monitors")
            no_monitor_text.SetForegroundColour(color)
            self.monitors_scrolled_sizer.Add(no_monitor_text, 0, wx.ALL | wx.CENTER, 5)
        else:
            # Populate the display if there are active monitors
            for identifier, (device_name, port_name) in self.gui.monitors.fetch_identifier_to_device_port_name().items():
                output = identifier + ": " + device_name
                if port_name:
                    output += "." + port_name
                monitor_label = wx.StaticText(self.monitors_scrolled, wx.ID_ANY, output)
                monitor_label.SetForegroundColour(color)
                self.monitors_scrolled_sizer.Add(monitor_label, 0, wx.ALL | wx.EXPAND, 5)

        self.monitors_scrolled.SetSizer(self.monitors_scrolled_sizer)
        self.monitors_scrolled.Layout()
        self.monitors_scrolled_sizer.FitInside(self.monitors_scrolled)
        self.monitors_scrolled_sizer.Layout()