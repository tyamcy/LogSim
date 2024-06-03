"""Implement the interactive buttons for the Logic Simulator.

Used in the Logic Simulator project to enable the user to perform different actions via button clicks.

Classes:
--------
RunButton - a button that allows users to run the simulation.
ContinueButton - a button that allows users to continue the simulation.
MonitorAddButton - a button that allows users to add a new monitor point.
MonitorRemoveButton - a button that allows users to remove an existing monitor point.
"""
import wx
import os

from gui_color import Color
from gui_dialogs import CustomDialogBox, IdentifierInputDialog

from base_app import _


class RunButton(wx.Button):
    """Configure the run button.

    This class provides a button that allows users to start the simulation (cold start).

    Parameters
    ----------
    parent: parent window.
    label: text on the button.

    Public methods
    --------------
    on_run(self, event): Handle the event when the user clicks the run button.
    """

    def __init__(self, parent, label=_(u"Run")):
        """Initialize button layout and styling."""
        super().__init__(parent, label=label)
        self.SetBackgroundColour(Color.color_primary)
        self.Bind(wx.EVT_BUTTON, self.on_run)

        self.gui = parent

    def on_run(self, event) -> None:
        """Handle the event when the user clicks the run button."""
        self.gui.canvas.reset_display()

        self.gui.terminal.append_text(Color.terminal_text_color, _(u"\n\nRunning simulation..."))
        self.gui.continue_button.Enable()
        self.gui.continue_button.SetBackgroundColour(Color.color_primary)

        self.gui.run_simulation()


class ContinueButton(wx.Button):
    """Configure the continue button.

    This class provides a button that allows users to continue the simulation.

    Parameters
    ----------
    parent: parent window.
    label: text on the button.

    Public methods
    --------------
    on_continue(self, event): Handle the event when the user continue button.
    """

    def __init__(self, parent, label=_(u"Continue")):
        """Initialize button layout and styling."""
        super().__init__(parent, label=label)
        self.SetBackgroundColour(Color.color_disabled)
        self.Bind(wx.EVT_BUTTON, self.on_continue)
        self.Disable()

        self.gui = parent

    def on_continue(self, event) -> None:
        """Handle the event when the user continue button."""
        self.gui.continue_simulation()
        self.gui.terminal.append_text(Color.terminal_text_color, _(u"\n\nUpdated parameters, continuing simulation..."))


class MonitorAddButton(wx.Button):
    """Configure the add monitor button.

    This class provides a button that allows users to add an active monitor point.

    Parameters
    ----------
    parent: parent window.
    label: text on the button.

    Public methods
    --------------
    on_add_monitor(self, event): Handle the click event of the add monitor button.
    """

    def __init__(self, parent, label=_("Add")):
        """Initialize button layout and styling."""
        super().__init__(parent, label=label)
        self.SetBackgroundColour(Color.light_button_color)
        self.Bind(wx.EVT_BUTTON, self.on_add_monitor)

        self.gui = parent

    def on_add_monitor(self, event) -> None:
        """Handle the click event of the add monitor button."""
        dialog = CustomDialogBox(self.gui, _(u"Add Monitor"), _(u"Select a device to monitor:"),
                                 self.gui.devices.fetch_all_device_names(),
                                 self.gui.theme)
        device_name = None
        device_port = None
        if dialog.ShowModal() == wx.ID_OK:
            device_name = dialog.get_selected_item()
        if device_name:
            device_id = self.gui.names.query(device_name)
            output_input_names = self.gui.devices.fetch_device_output_names(device_id)
            output_input_names += self.gui.devices.fetch_device_input_names(device_id)
            dialog = CustomDialogBox(self.gui, _(u"Add Monitor"), _(u"Select a port from the device to monitor:"),
                                     output_input_names,
                                     self.gui.theme)
            if dialog.ShowModal() == wx.ID_OK:
                device_port = dialog.get_selected_item()
            if device_port:
                identifier_dialog = IdentifierInputDialog(self.gui, _(u"Enter Identifier"),
                                                          _(u"Please enter an identifier for the monitor:"),
                                                          self.gui.theme)
                if identifier_dialog.ShowModal() == wx.ID_OK:
                    identifier = identifier_dialog.get_identifier()

                else:
                    identifier = None

                device_id = self.gui.names.query(device_name)
                port_id = self.gui.names.query(device_port) if device_port != "output" else None
                if identifier and isinstance(identifier, str) and identifier[0].isalpha():
                    error_type = self.gui.monitors.make_monitor(device_id, port_id, identifier)
                    if error_type == self.gui.monitors.NO_ERROR:
                        self.gui.monitors_list.update_monitors_list()
                    elif error_type == self.gui.monitors.MONITOR_IDENTIFIER_PRESENT:
                        wx.MessageBox(_(u"Identifier already used, please think of a new one!"),
                                      _(u"Error"), wx.OK | wx.ICON_ERROR)

                else:
                    wx.MessageBox(_(u"Please enter a valid identifier for the monitor! "
                                  "\n(Alphanumerics starting with an alphabet)"),
                                  _(u"Error"), wx.OK | wx.ICON_ERROR)
                self.gui.update_add_remove_button_states()
        dialog.Destroy()


class MonitorRemoveButton(wx.Button):
    """Configure the remove monitor button.

    This class provides a button that allows users to remove an active monitor point.

    Parameters
    ----------
    parent: parent window.
    label: text on the button.

    Public methods
    --------------
    on_remove_monitor(self, event): Handle the click event of the remove monitor button.
    """

    def __init__(self, parent, label=_(u"Remove")):
        """Initialize button layout and styling."""
        super().__init__(parent, label=label)
        self.SetBackgroundColour(Color.light_button_color)
        self.Bind(wx.EVT_BUTTON, self.on_remove_monitor)

        self.gui = parent

    def on_remove_monitor(self, event) -> None:
        """Handle the click event of the remove monitor button."""
        dialog = CustomDialogBox(self.gui, _(u"Remove Monitor"), _(u"Select a Monitor to Remove:"),
                                 list(self.gui.monitors.get_all_identifiers()),
                                 self.gui.theme)
        if dialog.ShowModal() == wx.ID_OK:
            identifier = dialog.get_selected_item()
            if identifier:
                self.gui.monitors.remove_monitor_by_identifier(identifier)
                self.gui.monitors_list.update_monitors_list()
                self.gui.update_add_remove_button_states()

        dialog.Destroy()
