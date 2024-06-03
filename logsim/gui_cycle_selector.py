import wx

from base_app import _


class CycleSelector:
    def __init__(self, parent):
        self.gui = parent

        self.cycles_sizer = wx.BoxSizer(wx.VERTICAL)
        self.cycles_text = wx.StaticText(parent, wx.ID_ANY, _(u"No. of Cycles"))
        self.cycles_spin = wx.SpinCtrl(parent, wx.ID_ANY, str(parent.num_cycles))

        self.cycles_spin.SetRange(1, 100)
        self.cycles_spin.Bind(wx.EVT_SPINCTRL, self.on_cycles_spin)

        self.cycles_sizer.Add(self.cycles_text, 0, wx.EXPAND | wx.ALL, 5)
        self.cycles_sizer.Add(self.cycles_spin, 0, wx.EXPAND | wx.ALL, 5)

    def on_cycles_spin(self, event) -> None:
        """Handle the event when the user changes the spin control value."""
        spin_value = self.cycles_spin.GetValue()
        self.gui.num_cycles = spin_value
