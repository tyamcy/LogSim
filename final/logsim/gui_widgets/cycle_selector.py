"""Implement the cycle selector component for the GUI.

Used in the Logic Simulator project to enable the user toggle the states of the switches.

Classes:
--------
CycleSelector - configures the cycle selector component.
"""
import wx

from logsim.internationalization import _


class CycleSelector:
    """Configure the number of cycles section.

    This class provides a component that allows the user to choose the number of simulation cycles.

    Parameters
    ----------
    parent: parent window.

    Public methods
    --------------
    on_cycles_spin(self, event): Handle the event when the user changes the spin control value.
    """

    def __init__(self, parent):
        """Initialize layout and syling of component."""
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
