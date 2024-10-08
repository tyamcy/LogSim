"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
Gui - configures the main window and all the widgets.
"""
import wx

from logsim.gui_widgets.color import Color
from logsim.gui_widgets.menu import MenuBar
from logsim.gui_widgets.canvas import Canvas
from logsim.gui_widgets.canvas_buttons import CanvasSettingButtons
from logsim.gui_widgets.terminal import Terminal
from logsim.gui_widgets.buttons import RunButton, ContinueButton, MonitorAddButton, MonitorRemoveButton
from logsim.gui_widgets.cycle_selector import CycleSelector
from logsim.gui_widgets.switch import Switch
from logsim.gui_widgets.monitor import MonitorsList

from logsim.internationalization import _
from logsim.parse import Parser


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

    update_parser(self, parser): Updates the parser object.

    on_upload_button(self, event): Event handler for when user clicks the upload button to upload
    a specification file (.txt file).

    disable_monitor_buttons(self): Disable buttons controlling monitor

    disable_simulation_buttons(self): Disable buttons controlling simulation.

    reset_gui_display(self): Reset gui display when new file is uploaded.

    update_add_remove_button_states(self): Updates the enabled/disabled state of the add and remove buttons.

    run_simulation(self): Runs the simulation and plot the monitored traces.

    continue_simulation(self): Continues the simulation and plot the monitored traces.

    toggle_theme(self, event): Event handler for when the user changes the color theme.
    """

    def __init__(self, title: str, path: str, parser: Parser):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=_(title), size=(800, 600))

        # Initialise variables
        self.names = parser.names
        self.devices = parser.devices
        self.network = parser.network
        self.monitors = parser.monitors
        self.parser = parser

        self.num_cycles = 10
        self.total_cycles = self.num_cycles

        self.mode = "3D"

        # A dictionary for the signals and simulated output
        self.signals_dictionary = dict()   # {(device_id, port_id): [signal_list]}
        self.signals_plot_dictionary = dict()  # {device_string: [signal_list]}

        self.menu_bar = MenuBar(self)
        self.canvas = Canvas(self)
        self.canvas_buttons = CanvasSettingButtons(self)
        self.terminal = Terminal(self)
        self.cycle_selector = CycleSelector(self)
        self.monitors_list = MonitorsList(self)
        self.add_monitor_button = MonitorAddButton(self)
        self.remove_monitor_button = MonitorRemoveButton(self)
        self.switch = Switch(self)
        self.run_button = RunButton(self)
        self.continue_button = ContinueButton(self)

        # Set GUI layout
        self.theme = "light"
        self.set_gui_layout()

        # Checking the file supplied using <filepath>
        self.check_errors(path, self.parser)

        # Update the GUI with new monitors and switches
        self.monitors_list.update_monitors_list()
        self.switch.update_switches_display()

    def set_gui_layout(self) -> None:
        """Set up the gui layout."""
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)  # main sizer with everything
        left_sizer = wx.BoxSizer(wx.VERTICAL)  # left sizer for the canvas and terminal
        right_sizer = wx.BoxSizer(wx.VERTICAL)  # right sizer for the controls
        main_sizer.Add(left_sizer, 5, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(right_sizer, 1, wx.ALL, 5)

        left_sizer.Add(self.canvas, 20, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(self.canvas_buttons.canvas_buttons_panel, 1, wx.EXPAND | wx.ALL, 1)
        left_sizer.Add(self.terminal.border_panel, 7, wx.EXPAND | wx.ALL, 5)
        right_sizer.Add(self.cycle_selector.cycles_sizer, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 8)
        right_sizer.Add(self.monitors_list.monitors_sizer, 1, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 0)

        monitors_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        monitors_buttons_sizer.Add(self.add_monitor_button, 1, wx.ALL | wx.EXPAND, 0)
        monitors_buttons_sizer.Add(self.remove_monitor_button, 1, wx.ALL | wx.EXPAND, 0)

        right_sizer.Add(monitors_buttons_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 6)
        right_sizer.Add(self.switch.switches_sizer, 1, wx.EXPAND | wx.TOP, 5)
        right_sizer.Add(self.run_button, 0, wx.ALL | wx.EXPAND, 8)
        right_sizer.Add(self.continue_button, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 8)

        self.SetBackgroundColour(Color.light_background_color)
        self.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Roboto'))
        self.SetSizeHints(1080, 720)
        self.SetSizer(main_sizer)

    def check_errors(self, filename: str, parser: Parser) -> bool:
        """Handles the error checking when a file is uploaded."""
        if parser.parse_network():

            # Message on terminal
            self.terminal.append_text(Color.terminal_success_color,
                                      _(u"\nFile {filename} uploaded successfully.")
                                      .format(filename=filename))

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
            self.terminal.append_text(Color.terminal_error_color,
                                      _(u"\nError in the specification file {filename}.")
                                      .format(filename=filename))

            # Disable monitor and simulation buttons
            self.disable_monitor_buttons()
            self.disable_simulation_buttons()

            # Printing the error message in the GUI terminal
            errors = parser.error_handler.error_output_list

            for error in errors:
                self.terminal.append_text(Color.dark_text_color, f"\n{error}")

            return False

    def update_parser(self, parser: Parser) -> None:
        """Updates the parser object."""
        self.names = parser.names
        self.devices = parser.devices
        self.network = parser.network
        self.monitors = parser.monitors
        self.parser = parser

    def disable_monitor_buttons(self) -> None:
        """Disable buttons controlling monitor."""
        self.add_monitor_button.Disable()
        self.remove_monitor_button.Disable()

    def disable_simulation_buttons(self) -> None:
        """Disable buttons controlling simulation."""
        self.run_button.Disable()
        self.run_button.SetBackgroundColour(Color.color_disabled)
        self.continue_button.Disable()
        self.continue_button.SetBackgroundColour(Color.color_disabled)

    def reset_gui_display(self) -> None:
        """Reset gui display when new file is uploaded."""
        self.monitors_list.monitors_scrolled_sizer.Clear(True)
        self.switch.switches_scrolled_sizer.Clear(True)

    def update_add_remove_button_states(self) -> None:
        """Updates the enabled/disabled state of the add and remove buttons."""
        self.remove_monitor_button.Enable(bool(self.monitors.get_all_identifiers()))

    def run_simulation(self) -> bool:
        """Runs the simulation and plot the monitored traces."""
        self.monitors.reset_monitors()

        # Running the simulation
        self.devices.cold_startup()
        for __ in range(self.num_cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                self.terminal.append_text(Color.terminal_error_color,
                                          _(u"\n\nError: network oscillating!!"))

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
            self.canvas_buttons.canvas_buttons_panel.SetBackgroundColour(Color.dark_background_color)
            self.canvas_buttons.screenshot_button.SetBackgroundColour(Color.dark_button_color)
            self.canvas_buttons.screenshot_button.SetForegroundColour(Color.dark_text_color)
            self.canvas_buttons.origin_button.SetBackgroundColour(Color.dark_button_color)
            self.canvas_buttons.origin_button.SetForegroundColour(Color.dark_text_color)
            self.canvas_buttons.grid_button.SetBackgroundColour(Color.dark_button_color)
            self.canvas_buttons.grid_button.SetForegroundColour(Color.dark_text_color)
            self.canvas_buttons.toggle_mode_button.SetBackgroundColour(Color.dark_button_color)
            self.canvas_buttons.toggle_mode_button.SetForegroundColour(Color.dark_text_color)
            self.cycle_selector.cycles_text.SetForegroundColour(Color.dark_text_color)
            self.cycle_selector.cycles_spin.SetBackgroundColour(Color.dark_background_secondary)
            self.cycle_selector.cycles_spin.SetForegroundColour(Color.dark_text_color)
            self.monitors_list.monitors_text.SetForegroundColour(Color.dark_text_color)
            self.monitors_list.monitors_scrolled.SetForegroundColour(Color.dark_background_secondary)
            self.monitors_list.monitors_scrolled.SetBackgroundColour(Color.dark_background_secondary)
            self.add_monitor_button.SetBackgroundColour(Color.dark_button_color)
            self.add_monitor_button.SetForegroundColour(Color.dark_text_color)
            self.remove_monitor_button.SetBackgroundColour(Color.dark_button_color)
            self.remove_monitor_button.SetForegroundColour(Color.dark_text_color)
            self.switch.switches_text.SetForegroundColour(Color.dark_text_color)
            self.switch.switches_scrolled.SetBackgroundColour(Color.dark_background_secondary)
            self.switch.switches_scrolled.SetForegroundColour(Color.dark_background_secondary)

            for child in self.monitors_list.monitors_scrolled.GetChildren():
                if isinstance(child, wx.StaticText):
                    child.SetForegroundColour(Color.dark_text_color)
            self.monitors_list.monitors_scrolled.Layout()

            for child in self.switch.switches_scrolled.GetChildren():
                if isinstance(child, wx.StaticText):
                    child.SetForegroundColour(Color.dark_text_color)
                elif isinstance(child, wx.ToggleButton):
                    child.SetBackgroundColour(Color.dark_button_color)
                    child.SetForegroundColour(Color.dark_text_color)

            self.theme = "dark"  # update theme

        elif self.theme == "dark":
            self.canvas.update_theme(self.theme)
            self.SetBackgroundColour(Color.light_background_color)
            self.canvas_buttons.canvas_buttons_panel.SetBackgroundColour(Color.light_background_color)
            self.canvas_buttons.screenshot_button.SetBackgroundColour(Color.light_button_color)
            self.canvas_buttons.screenshot_button.SetForegroundColour(Color.light_text_color)
            self.canvas_buttons.origin_button.SetBackgroundColour(Color.light_button_color)
            self.canvas_buttons.origin_button.SetForegroundColour(Color.light_text_color)
            self.canvas_buttons.grid_button.SetBackgroundColour(Color.light_button_color)
            self.canvas_buttons.grid_button.SetForegroundColour(Color.light_text_color)
            self.canvas_buttons.toggle_mode_button.SetBackgroundColour(Color.light_button_color)
            self.canvas_buttons.toggle_mode_button.SetForegroundColour(Color.light_text_color)
            self.cycle_selector.cycles_text.SetForegroundColour(Color.light_text_color)
            self.cycle_selector.cycles_spin.SetBackgroundColour(Color.light_background_secondary)
            self.cycle_selector.cycles_spin.SetForegroundColour(Color.light_text_color)
            self.monitors_list.monitors_text.SetForegroundColour(Color.light_text_color)
            self.monitors_list.monitors_scrolled.SetForegroundColour(Color.light_background_secondary)
            self.monitors_list.monitors_scrolled.SetBackgroundColour(Color.light_background_secondary)
            self.add_monitor_button.SetBackgroundColour(Color.light_button_color)
            self.add_monitor_button.SetForegroundColour(Color.light_text_color)
            self.remove_monitor_button.SetBackgroundColour(Color.light_button_color)
            self.remove_monitor_button.SetForegroundColour(Color.light_text_color)
            self.switch.switches_text.SetForegroundColour(Color.light_text_color)
            self.switch.switches_scrolled.SetBackgroundColour(Color.light_background_secondary)
            self.switch.switches_scrolled.SetForegroundColour(Color.light_background_secondary)

            for child in self.monitors_list.monitors_scrolled.GetChildren():
                if isinstance(child, wx.StaticText):
                    child.SetForegroundColour(Color.light_text_color)
            self.monitors_list.monitors_scrolled.Layout()

            for child in self.switch.switches_scrolled.GetChildren():
                if isinstance(child, wx.StaticText):
                    child.SetForegroundColour(Color.light_text_color)
                elif isinstance(child, wx.ToggleButton):
                    child.SetBackgroundColour(Color.light_button_color)
                    child.SetForegroundColour(Color.light_text_color)

            self.theme = "light"  # update theme

        self.Refresh()
