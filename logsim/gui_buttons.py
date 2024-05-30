import wx
import os

from gui_color import Color
from gui_dialogs import CustomDialogBox, IdentifierInputDialog

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


class UploadButton(wx.Button):
    def __init__(self, parent, label="Upload"):
        super().__init__(parent, label=label)
        self.gui = parent

        self.SetBackgroundColour(Color.color_primary)
        self.Bind(wx.EVT_BUTTON, self.on_upload)

    def on_upload(self, event) -> None:
        """Handles the event when the user clicks the upload button to select the specification file."""
        wildcard = "Text files (*.txt)|*.txt"
        with wx.FileDialog(self.gui, "Open Specification File", wildcard=wildcard,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            # Canceling the action
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            path = fileDialog.GetPath()  # extracting the file path
            filename = os.path.basename(path)  # extracting the file name

            # Check if file is a text file
            if not path.lower().endswith(".txt"):
                wx.MessageBox("Please select a valid .txt file", "Error", wx.OK | wx.ICON_ERROR)
                return

            # clear display
            self.gui.canvas.clear_display()

            # Processing the file
            progress_dialog = wx.ProgressDialog("Processing file",
                                                "Specification file is being processed...",
                                                maximum=100,
                                                parent=self.gui,
                                                style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE)

            self.gui.terminal.reset_terminal()
            self.gui.reset_gui_display()

            try:
                # Initialise instances of the inner simulator classes
                names = Names()
                devices = Devices(names)
                network = Network(names, devices)
                monitors = Monitors(names, devices, network)

                try:
                    scanner = Scanner(path, names)
                except UnicodeDecodeError:
                    self.gui.terminal.append_text(Color.terminal_error_color, f"\nError: file '{path}' is not a unicode text file")

                    self.gui.disable_monitor_buttons()
                    self.gui.disable_simulation_buttons()
                    return
                parser = Parser(names, devices, network, monitors, scanner)

                # Progress bar mock progress
                for i in range(100):
                    wx.MilliSleep(10)
                    progress_dialog.Update(i + 1)

                if self.gui.check_errors(filename, parser):
                    # Instantiate the circuit for the newly uploaded file
                    self.gui.update_parser(parser)

                    # Update the GUI with new canvas, monitors and switches
                    self.gui.monitors_list.update_monitors_list()
                    self.gui.switch.update_switches_display()

            except IOError:
                progress_dialog.Destroy()
                self.gui.terminal.append_text(Color.terminal_error_color, f"File {filename} upload failed.")

            finally:
                progress_dialog.Update(100)
                progress_dialog.Destroy()


class RunButton(wx.Button):
    def __init__(self, parent, label="Run"):
        super().__init__(parent, label=label)
        self.SetBackgroundColour(Color.color_primary)
        self.Bind(wx.EVT_BUTTON, self.on_run)

        self.gui = parent

    def on_run(self, event) -> None:
        """Handle the event when the user clicks the run button."""
        self.gui.canvas.reset_display()

        self.gui.terminal.append_text(Color.terminal_text_color, "\n\nRunning simulation...")
        self.gui.continue_button.Enable()
        self.gui.continue_button.SetBackgroundColour(Color.color_primary)

        self.gui.run_simulation()


class ContinueButton(wx.Button):
    def __init__(self, parent, label="Continue"):
        super().__init__(parent, label=label)
        self.SetBackgroundColour(Color.color_disabled)
        self.Bind(wx.EVT_BUTTON, self.on_continue)
        self.Disable()

        self.gui = parent

    def on_continue(self, event) -> None:
        """Handle the event when the user continue button."""
        self.gui.continue_simulation()
        self.gui.terminal.append_text(Color.terminal_text_color, "\n\nUpdated parameters, continuing simulation...")


class MonitorAddButton(wx.Button):
    def __init__(self, parent, label="Add"):
        super().__init__(parent, label=label)
        self.SetBackgroundColour(Color.light_button_color)
        self.Bind(wx.EVT_BUTTON, self.on_add_monitor)

        self.gui = parent

    def on_add_monitor(self, event) -> None:
        """Handle the click event of the add monitor button."""
        dialog = CustomDialogBox(self.gui, "Add Monitor", "Select a device to monitor:",
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
            dialog = CustomDialogBox(self.gui, "Add Monitor", "Select a port from the device to monitor:",
                                     output_input_names,
                                     self.gui.theme)
            if dialog.ShowModal() == wx.ID_OK:
                device_port = dialog.get_selected_item()
            if device_port:
                identifier_dialog = IdentifierInputDialog(self.gui, "Enter Identifier",
                                                          "Please enter an identifier for the monitor:",
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
                        wx.MessageBox("Identifier already used, please think of a new one!",
                                      "Error", wx.OK | wx.ICON_ERROR)

                else:
                    wx.MessageBox("Please enter a valid identifier for the monitor! "
                                  "\n(Alphanumerics starting with an alphabet)",
                                  "Error", wx.OK | wx.ICON_ERROR)
                self.gui.update_add_remove_button_states()
        dialog.Destroy()


class MonitorRemoveButton(wx.Button):
    def __init__(self, parent, label="Remove"):
        super().__init__(parent, label=label)
        self.SetBackgroundColour(Color.light_button_color)
        self.Bind(wx.EVT_BUTTON, self.on_remove_monitor)

        self.gui = parent

    def on_remove_monitor(self, event) -> None:
        """Handle the click event of the remove monitor button."""
        dialog = CustomDialogBox(self.gui, "Remove Monitor", "Select a Monitor to Remove:",
                                 list(self.gui.monitors.get_all_identifiers()),
                                 self.gui.theme)
        if dialog.ShowModal() == wx.ID_OK:
            identifier = dialog.get_selected_item()
            if identifier:
                self.gui.monitors.remove_monitor_by_identifier(identifier)
                self.gui.monitors_list.update_monitors_list()
                self.gui.update_add_remove_button_states()

        dialog.Destroy()
