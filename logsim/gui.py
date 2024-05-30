"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx

from gui_canvas import Canvas
from gui_color import Color
from gui_terminal import Terminal
from gui_buttons import UploadButton, RunButton, ContinueButton, MonitorAddButton, MonitorRemoveButton
from gui_menu import MenuBar
from gui_cycle_selector import CycleSelector
from gui_switch import Switch
from gui_monitor import MonitorsList

from parse import Parser


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    check_errors(self, filename, parser): Handles the error checking when a file is uploaded.

    on_upload_button(self, event): Event handler for when user clicks the upload button to upload a specification file (.txt file).

    on_cycles_spin(self, event): Event handler for when the user changes the spin
                           control value.

    update_monitors_display(self): Handle the event of updating the laist of monitors upon change.

    update_add_remove_button_states(self): Updates the enabled/disabled state of the add and remove buttons.

    on_add_monitor_button(self, event): Event handler for when the users click the add monitor button.

    on_remove_monitor_button(self, event): Event handler for when the user clicks the remove monitor button.

    update_switches_display(self): Event handler for updating the displayed list of switches.

    on_toggle_switch(self, event): Event handler for when the user toggles a switch.

    run_simulation(self): Runs the simulation and plot the monitored traces.

    continue_simulation(self): Continues the simulation and plot the monitored traces.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_continue_button(self, event): Event handler for when the user clicks the continue button.

    toggle_theme(self, event): Event handler for when the user changes the color theme.
    """

    welcoming_text = "Welcome to Logic Simulator\n=========================="

    def __init__(self, title: str, path: str, parser: Parser):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Initialise variables
        self.names = parser.names
        self.devices = parser.devices
        self.network = parser.network
        self.monitors = parser.monitors
        self.parser = parser

        self.num_cycles = 10
        self.total_cycles = self.num_cycles

        # Getting the list of active monitors
        # Creating a dictionary of switches
        self.id_switches = self.devices.find_devices(self.devices.SWITCH)
        self.switches_dict = dict()  # {switch name: switch state}
        self.toggle_button_switch_name = dict()  # {toggle button: switch name}

        # A dictionary for the signals and simulated output
        # {(device_id, port_id): [signal_list]}
        self.signals_dictionary = dict()
        # {device_string: [signal_list]}
        self.signals_plot_dictionary = dict()

        # Initial styling (default as light mode)
        self.theme = "light"
        self.SetBackgroundColour(Color.light_background_color)
        self.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Roboto'))

        # Menu bar
        self.menu_bar = MenuBar(self)

        # Defining sizers for layout
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)  # main sizer with everything
        self.left_sizer = wx.BoxSizer(wx.VERTICAL)  # left sizer for the canvas and terminal
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)  # right sizer for the controls
        self.main_sizer.Add(self.left_sizer, 5, wx.EXPAND | wx.ALL, 10)
        self.main_sizer.Add(self.right_sizer, 1, wx.ALL, 5)

        # Canvas for drawing / plotting signals
        self.canvas = Canvas(self)
        self.left_sizer.Add(self.canvas, 7, wx.EXPAND | wx.ALL, 5)

        # Terminal
        self.terminal = Terminal(self)
        self.left_sizer.Add(self.terminal.border_panel, 3, wx.EXPAND | wx.ALL, 5)

        # Upload button
        self.upload_button = UploadButton(self)
        self.right_sizer.Add(self.upload_button, 0, wx.ALL | wx.EXPAND, 8)

        # No of cycles section
        self.cycle_selector = CycleSelector(self)
        self.right_sizer.Add(self.cycle_selector.cycles_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Monitors section
        self.monitors_list = MonitorsList(self)
        self.right_sizer.Add(self.monitors_list.monitors_sizer, 1, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 0)

        # Add and remove monitor buttons
        self.monitors_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.add_monitor_button = MonitorAddButton(self)
        self.monitors_buttons_sizer.Add(self.add_monitor_button, 1, wx.ALL | wx.EXPAND, 0)

        self.remove_monitor_button = MonitorRemoveButton(self)
        self.monitors_buttons_sizer.Add(self.remove_monitor_button, 1, wx.ALL | wx.EXPAND, 0)

        self.right_sizer.Add(self.monitors_buttons_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 6)

        # Switches section
        self.switch = Switch(self)
        self.right_sizer.Add(self.switch.switches_sizer, 1, wx.EXPAND | wx.TOP, 5)

        # Run button
        self.run_button = RunButton(self)
        self.right_sizer.Add(self.run_button, 0, wx.ALL | wx.EXPAND, 8)

        # Continue button
        self.continue_button = ContinueButton(self)
        self.right_sizer.Add(self.continue_button, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 8)

        # Checking the file supplied using <filepath>
        self.check_errors(path, self.parser)

        # Update the GUI with new monitors and switches
        self.monitors_list.update_monitors_list()
        self.update_switches_display()

        # Set main sizer and size of GUI
        self.SetSizeHints(1080, 720)
        self.SetSizer(self.main_sizer)

    def update_parser(self, parser: Parser):
        self.names = parser.names
        self.devices = parser.devices
        self.network = parser.network
        self.monitors = parser.monitors
        self.parser = parser

    def disable_monitor_buttons(self):
        """Disable buttons controlling monitor"""
        self.add_monitor_button.Disable()
        self.remove_monitor_button.Disable()

    def disable_simulation_buttons(self):
        """Disable buttons controlling simulation"""
        self.run_button.Disable()
        self.run_button.SetBackgroundColour(Color.color_disabled)
        self.continue_button.Disable()
        self.continue_button.SetBackgroundColour(Color.color_disabled)

    def reset_gui_display(self):
        """Reset gui display when new file is uploaded."""
        self.monitors_list.monitors_scrolled_sizer.Clear(True)
        self.switch.switches_scrolled_sizer.Clear(True)

    def check_errors(self, filename: str, parser: Parser) -> bool:
        """Handles the error checking when a file is uploaded."""
        if parser.parse_network():

            # Message on terminal
            self.terminal.append_text(Color.terminal_success_color, f"\nFile {filename} uploaded successfully.")

            # Enable add and remove button
            self.add_monitor_button.Enable()
            self.remove_monitor_button.Enable()

            # Enable run button and disable continue button
            self.run_button.Enable()
            self.run_button.SetBackgroundColour(Color.color_primary)
            self.continue_button.Disable()
            self.continue_button.SetBackgroundColour(Color.color_disabled)

            return True
        else:
            # Message on terminal
            self.terminal.append_text(Color.terminal_error_color, f"\nError in the specification file {filename}.")

            # Disable monitor and simulation buttons
            self.disable_monitor_buttons()
            self.disable_simulation_buttons()

            # Printing the error message in the GUI terminal
            errors = parser.error_handler.error_output_list

            for error in errors:
                self.terminal.append_text(Color.dark_text_color, f"\n{error}")

            return False

    def update_add_remove_button_states(self) -> None:
        """Updates the enabled/disabled state of the add and remove buttons."""
        self.remove_monitor_button.Enable(bool(self.monitors.get_all_identifiers()))

    def update_switches_display(self) -> None:
        """Handle the event of updating the displayed list of switches."""
        # Creating a dictionary of switches
        self.id_switches = self.devices.find_devices(self.devices.SWITCH)
        self.switches_dict = dict()  # {switch name string: switch state}

        for switch_id in self.id_switches:
            switch_name = self.names.get_name_string(switch_id)
            switch_state = self.devices.get_device(switch_id).switch_state
            self.switches_dict[switch_name] = switch_state

        self.switch.switches_scrolled_sizer.Clear(True)

        for switch, state in self.switches_dict.items():
            switch_sizer = wx.BoxSizer(wx.HORIZONTAL)

            label = wx.StaticText(self.switch.switches_scrolled, wx.ID_ANY, switch)
            switch_sizer.Add(label, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)

            initial_label = "1" if state == 1 else "0"
            toggle = wx.ToggleButton(self.switch.switches_scrolled, wx.ID_ANY, initial_label)
            toggle.SetValue(state == 1)
            toggle.SetBackgroundColour(Color.light_button_color)
            toggle.Bind(wx.EVT_TOGGLEBUTTON, self.switch.on_toggle_switch)

            if self.theme == "light":
                label.SetForegroundColour(Color.light_text_color)
                toggle.SetForegroundColour(Color.light_text_color)
                toggle.SetBackgroundColour(Color.light_button_color)
            elif self.theme == "dark":
                label.SetForegroundColour(Color.dark_text_color)
                toggle.SetForegroundColour(Color.dark_text_color)
                toggle.SetBackgroundColour(Color.dark_button_color)

            self.toggle_button_switch_name[toggle.GetId()] = switch

            switch_sizer.Add(toggle, 0, wx.ALIGN_CENTER_VERTICAL)

            self.switch.switches_scrolled_sizer.Add(switch_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.switch.switches_scrolled.SetSizer(self.switch.switches_scrolled_sizer)
        self.switch.switches_scrolled.Layout()
        self.switch.switches_scrolled_sizer.FitInside(self.switch.switches_scrolled)
        self.switch.switches_scrolled_sizer.Layout()

    def run_simulation(self) -> bool:
        """Runs the simulation and plot the monitored traces."""
        self.monitors.reset_monitors()

        # Running the simulation
        self.devices.cold_startup()
        for _ in range(self.num_cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                self.terminal.append_text(Color.terminal_error_color,f"\n\nError: network oscillating!!")
                self.disable_simulation_buttons()
                return False

        self.signals_dictionary = self.monitors.get_all_monitor_signal()
        self.total_cycles = self.num_cycles
        self.canvas.update_cycle(self.total_cycles)
        self.canvas.render("", self.signals_dictionary)
        return True

    def continue_simulation(self) -> bool:
        """Continues the simulation and plot the monitored traces."""
        # Running the simulation
        for _ in range(self.num_cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                self.disable_simulation_buttons()
                return False

        self.signals_dictionary = self.monitors.get_all_monitor_signal()
        self.total_cycles += self.num_cycles
        self.canvas.update_cycle(self.total_cycles)
        self.canvas.render("", self.signals_dictionary)
        return True

    def toggle_theme(self, event) -> None:
        """Handle the event when the user presses the toggle switch menu item to switch between colour themes."""
        if self.theme == "light":
            self.canvas.update_theme(self.theme)
            self.SetBackgroundColour(Color.dark_background_color)
            self.cycle_selector.cycles_text.SetForegroundColour(Color.dark_text_color)
            self.cycle_selector.cycles_spin.SetBackgroundColour(Color.dark_background_secondary)
            self.cycle_selector.cycles_spin.SetForegroundColour(Color.dark_text_color)
            self.monitors_text.SetForegroundColour(Color.dark_text_color)
            self.monitors_scrolled.SetForegroundColour(Color.dark_background_secondary)
            self.monitors_scrolled.SetBackgroundColour(Color.dark_background_secondary)
            self.add_monitor_button.SetBackgroundColour(Color.dark_button_color)
            self.add_monitor_button.SetForegroundColour(Color.dark_text_color)
            self.remove_monitor_button.SetBackgroundColour(Color.dark_button_color)
            self.remove_monitor_button.SetForegroundColour(Color.dark_text_color)
            self.switches_text.SetForegroundColour(Color.dark_text_color)
            self.switches_scrolled.SetBackgroundColour(Color.dark_background_secondary)
            self.switches_scrolled.SetForegroundColour(Color.dark_background_secondary)

            for child in self.monitors_scrolled.GetChildren():
                if isinstance(child, wx.StaticText):
                    child.SetForegroundColour(Color.dark_text_color)
            self.monitors_scrolled.Layout()

            for child in self.switches_scrolled.GetChildren():
                if isinstance(child, wx.StaticText):
                    child.SetForegroundColour(Color.dark_text_color)
                elif isinstance(child, wx.ToggleButton):
                    child.SetBackgroundColour(Color.dark_button_color)
                    child.SetForegroundColour(Color.dark_text_color)

            self.theme = "dark"  # update theme

        elif self.theme == "dark":
            self.canvas.update_theme(self.theme)
            self.SetBackgroundColour(Color.light_background_color)
            self.cycle_selector.cycles_text.SetForegroundColour(Color.light_text_color)
            self.cycle_selector.cycles_spin.SetBackgroundColour(Color.light_background_secondary)
            self.cycle_selector.cycles_spin.SetForegroundColour(Color.light_text_color)
            self.monitors_text.SetForegroundColour(Color.light_text_color)
            self.monitors_scrolled.SetForegroundColour(Color.light_background_secondary)
            self.monitors_scrolled.SetBackgroundColour(Color.light_background_secondary)
            self.add_monitor_button.SetBackgroundColour(Color.light_button_color)
            self.add_monitor_button.SetForegroundColour(Color.light_text_color)
            self.remove_monitor_button.SetBackgroundColour(Color.light_button_color)
            self.remove_monitor_button.SetForegroundColour(Color.light_text_color)
            self.switches_text.SetForegroundColour(Color.light_text_color)
            self.switches_scrolled.SetBackgroundColour(Color.light_background_secondary)
            self.switches_scrolled.SetForegroundColour(Color.light_background_secondary)

            for child in self.monitors_scrolled.GetChildren():
                if isinstance(child, wx.StaticText):
                    child.SetForegroundColour(Color.light_text_color)
            self.monitors_scrolled.Layout()

            for child in self.switches_scrolled.GetChildren():
                if isinstance(child, wx.StaticText):
                    child.SetForegroundColour(Color.light_text_color)
                elif isinstance(child, wx.ToggleButton):
                    child.SetBackgroundColour(Color.light_button_color)
                    child.SetForegroundColour(Color.light_text_color)

            self.theme = "light"  # update theme

        self.Refresh()

