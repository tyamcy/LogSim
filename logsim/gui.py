"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT
import os

from gui_widgets import CustomDialogBox, IdentifierInputDialog

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.

    update_theme(self, theme): Updates the colour palette.

    update_theme(self, theme): Updates the colour palette.
    """

    def __init__(self, parent, devices: Devices, monitors: Monitors, names: Names):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        self.devices = devices
        self.monitors = monitors
        self.names = names
        self.total_cycles = 0
        self.signals = {}
        self.signals_dictionary = {}

        # Colour themes
        self.light_color_background = (0.98, 0.98, 0.98, 1)
        self.light_color_text = (0, 0, 0)
        self.light_color_trace = (0, 0, 0)
        self.dark_color_background = (0.267, 0.267, 0.267, 1)
        self.dark_color_text = (1, 1, 1)
        self.dark_color_trace = (1, 1, 1)

        # Initialise colours
        self.color_background = self.light_color_background
        self.color_text = self.light_color_text
        self.color_trace = self.light_color_trace

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1
        self.zoom_current = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(*self.color_background)
        GL.glClearColor(*self.color_background)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text: str, signals={}) -> None:
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        if signals:
            self.signals = signals  # updating the dictionary of signal values

        if self.signals:
            x_start = 60
            y_start = 50
            width = 30  # width of a cycle
            height = 30  # height of a pulse
            y_diff = 75  # distance between different plots

            # Annotate y-axis (no. of cycles)
            self.render_text("0", x_start, y_start - 20)
            no_cycles = len(list(self.signals.values())[0])
            self.render_text(str(no_cycles), x_start + no_cycles * width, y_start - 20)

            """refactor later"""
            identifier_dict = self.monitors.fetch_identifier_to_device_port_name()
            for index, (identifier, (device_name, port_name)) in enumerate(identifier_dict.items()):
                device_id = self.names.query(device_name)
                port_id = self.names.query(port_name) if port_name else None
                trace = self.signals[(device_id, port_id)]

                # Update y
                y = y_start + index * y_diff

                # Rendering the identifier name
                self.render_text(identifier, 20, y + int(y_diff / 5))

                # Adding 0 and 1
                self.render_text("0", 40, y)
                self.render_text("1", 40, y + height)

                # Check x starting position
                if self.total_cycles > len(trace):
                    x_start += (self.total_cycles - len(trace)) * width

                # Update x
                x = x_start
                x_next = x_start + width

                GL.glColor3f(*self.color_trace)
                GL.glBegin(GL.GL_LINE_STRIP)

                for value in trace:
                    if value == 0:
                        y_curr = y
                    elif value == 1:
                        y_curr = y + height
                        # x = 10 + i * x_spacing
                    GL.glVertex2f(x, y_curr)
                    GL.glVertex2f(x_next, y_curr)

                    # Update x
                    x = x_next
                    x_next += width

                GL.glEnd()
                x_start = 60

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event) -> None:
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        # text = "".join(["Canvas redrawn on paint event, size is ",
        #                str(size.width), ", ", str(size.height)])
        self.render("")
        # text = "".join(["Canvas redrawn on paint event, size is ",
        #                str(size.width), ", ", str(size.height)])
        self.render("")

    def on_size(self, event) -> None:
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event) -> None:
        """Handle mouse events."""
        text = ""
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                    event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                    event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text: str, x_pos: int, y_pos: int) -> None:
        """Handle text drawing operations."""
        GL.glColor3f(*self.color_text)
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def update_theme(self, theme: str) -> None:
        """Handle background colour update."""
        self.SetCurrent(self.context)
        if theme == "dark":
            self.color_background = self.light_color_background
            self.color_text = self.light_color_text
            self.color_trace = self.light_color_trace
            GL.glClearColor(*self.light_color_background)
            GL.glColor3f(*self.light_color_text)
        elif theme == "light":
            self.color_background = self.dark_color_background
            self.color_text = self.dark_color_text
            self.color_trace = self.dark_color_trace
            GL.glClearColor(*self.dark_color_background)
            GL.glColor3f(*self.dark_color_text)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self.SwapBuffers()

    def reset_display(self) -> None:
        """Return to the initial viewpoint at the origin."""
        # Reset location parameters
        self.pan_x = 0
        self.pan_y = 0
        self.zoom = 1
        self.init = False
        self.on_paint(None)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

    def update_cycle(self, cycle: int) -> None:
        """Keeps track of the total number of simulation cycles."""
        self.total_cycles = cycle

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

    fetch_cycle(self): Tracks the total number of simulation cycles.
    """

    welcoming_text = "Welcome to Logic Simulator\n=========================="

    def __init__(self, title: str, path: str, names: Names, devices: Devices, network: Network, monitors: Monitors, parser: Parser):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Initialise variables
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
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

        # Colour styles
        self.color_primary = "#4DA2B4"
        self.color_primary_shade = "#397E8D"
        self.color_disabled = "#CBBBBB"

        # UI Theme Colours - Light Mode
        self.light_button_color = "#EAEAEA"
        self.light_background_color = "#DDDDDD"
        self.light_background_secondary = "#FAFAFA"
        self.light_text_color = "#000000"

        # UI Theme Colours - Dark Mode
        self.dark_button_color = "#555555"
        self.dark_background_color = "#333333"
        self.dark_background_secondary = "#444444"
        self.dark_text_color = "#FFFFFF"

        # Terminal Colours
        self.terminal_background_color = "#222222"
        self.terminal_text_color = "#FFFFFF"
        self.terminal_success_color = "#16C60C"
        self.terminal_warning_color = "#F9F1A5"
        self.terminal_error_color = "#E74856"

        # Initial styling (default as light mode)
        self.theme = "light"
        self.SetBackgroundColour(self.light_background_color)
        self.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Roboto'))

        # Menu bar
        # Configure the menu bar
        menuBar = wx.MenuBar()

        # File menu
        fileMenu = wx.Menu()
        theme_icon = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_MENU, (16, 16))
        about_icon = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_MENU, (16, 16))
        exit_icon = wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_MENU, (16, 16))
        toggle_theme_item = wx.MenuItem(fileMenu, wx.ID_PAGE_SETUP, "&Toggle theme")
        about_item = wx.MenuItem(fileMenu, wx.ID_ABOUT, "&About")
        exit_item = wx.MenuItem(fileMenu, wx.ID_EXIT, "&Exit")
        toggle_theme_item.SetBitmap(theme_icon)
        about_item.SetBitmap(about_icon)
        exit_item.SetBitmap(exit_icon)
        fileMenu.Append(toggle_theme_item)
        fileMenu.AppendSeparator()
        fileMenu.Append(about_item)
        fileMenu.Append(exit_item)

        # Help menu
        helpMenu = wx.Menu()
        help_icon = wx.ArtProvider.GetBitmap(wx.ART_HELP, wx.ART_MENU, (16, 16))
        help_item = wx.MenuItem(helpMenu, wx.ID_HELP, "&Quick Guide")
        help_item.SetBitmap(help_icon)
        helpMenu.Append(help_item)

        # Adding everything to menuBar
        menuBar.Append(fileMenu, "&Menu")
        menuBar.Append(helpMenu, "&Help")
        self.SetMenuBar(menuBar)

        # Bind event to menuBar
        self.Bind(wx.EVT_MENU, self.on_menu)

        # Main UI layout
        # Canvas for drawing / plotting signals
        self.canvas = MyGLCanvas(self, devices, monitors, names)

        # Defining sizers for layout
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)  # main sizer with everything
        self.left_sizer = wx.BoxSizer(wx.VERTICAL)  # left sizer for the canvas and terminal
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)  # right sizer for the controls

        # Terminal
        self.border_panel = wx.Panel(self)
        self.border_panel.SetBackgroundColour(self.terminal_background_color)
        self.terminal_panel = wx.Panel(self.border_panel)
        self.terminal_panel.SetBackgroundColour(self.terminal_background_color)

        self.terminal = wx.TextCtrl(self.terminal_panel,
                                    style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.BORDER_NONE)
        self.terminal.SetBackgroundColour(self.terminal_background_color)
        self.terminal.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Consolas'))
        self.terminal.SetForegroundColour(self.terminal_text_color)
        self.terminal.AppendText(self.welcoming_text)

        self.terminal_sizer = wx.BoxSizer(wx.VERTICAL)
        self.terminal_sizer.Add(self.terminal, 1, wx.EXPAND | wx.ALL, 0)
        self.terminal_panel.SetSizer(self.terminal_sizer)

        self.border_sizer = wx.BoxSizer(wx.VERTICAL)
        self.border_sizer.Add(self.terminal_panel, 1, wx.EXPAND | wx.ALL, 10)
        self.border_panel.SetSizer(self.border_sizer)

        self.left_sizer.Add(self.canvas, 7, wx.EXPAND | wx.ALL, 5)
        self.left_sizer.Add(self.border_panel, 3, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(self.left_sizer, 5, wx.EXPAND | wx.ALL, 10)
        self.main_sizer.Add(self.right_sizer, 1, wx.ALL, 5)

        # Upload button
        self.upload_button = wx.Button(self, wx.ID_ANY, "Upload")
        self.upload_button.SetBackgroundColour(self.color_primary)
        self.upload_button.Bind(wx.EVT_BUTTON, self.on_upload_button)
        self.right_sizer.Add(self.upload_button, 0, wx.ALL | wx.EXPAND, 8)

        # No of cycles section
        self.cycles_sizer = wx.BoxSizer(wx.VERTICAL)
        self.cycles_text = wx.StaticText(self, wx.ID_ANY, "No. of Cycles")
        self.cycles_spin = wx.SpinCtrl(self, wx.ID_ANY, str(self.num_cycles))
        self.cycles_spin.SetRange(1, 100)

        self.cycles_spin.Bind(wx.EVT_SPINCTRL, self.on_cycles_spin)

        self.cycles_sizer.Add(self.cycles_text, 0, wx.EXPAND | wx.ALL, 5)
        self.cycles_sizer.Add(self.cycles_spin, 0, wx.EXPAND | wx.ALL, 5)
        self.right_sizer.Add(self.cycles_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Monitors section
        self.monitors_sizer = wx.BoxSizer(wx.VERTICAL)
        self.monitors_text = wx.StaticText(self, wx.ID_ANY, "Monitors")
        self.monitors_scrolled = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self.monitors_scrolled.SetScrollRate(10, 10)
        self.monitors_scrolled_sizer = wx.BoxSizer(wx.VERTICAL)

        self.update_monitors_display()

        self.monitors_scrolled.SetMinSize((250, 150))
        self.monitors_scrolled.SetBackgroundColour(self.light_background_secondary)
        self.monitors_sizer.Add(self.monitors_text, 0, wx.ALL, 5)
        self.monitors_sizer.Add(self.monitors_scrolled, 1, wx.EXPAND | wx.ALL, 5)
        self.right_sizer.Add(self.monitors_sizer, 1, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 0)

        # Add and remove monitor buttons
        self.monitors_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.add_monitor_button = wx.Button(self, wx.ID_ANY, "Add")
        self.add_monitor_button.SetBackgroundColour(self.light_button_color)
        self.add_monitor_button.Bind(wx.EVT_BUTTON, self.on_add_monitor_button)
        self.monitors_buttons_sizer.Add(self.add_monitor_button, 1, wx.ALL | wx.EXPAND, 0)

        self.remove_monitor_button = wx.Button(self, wx.ID_ANY, "Remove")
        self.remove_monitor_button.SetBackgroundColour(self.light_button_color)
        self.remove_monitor_button.Bind(wx.EVT_BUTTON, self.on_remove_monitor_button)
        self.monitors_buttons_sizer.Add(self.remove_monitor_button, 1, wx.ALL | wx.EXPAND, 0)

        self.right_sizer.Add(self.monitors_buttons_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 6)

        # Switches section
        self.switches_sizer = wx.BoxSizer(wx.VERTICAL)
        self.switches_text = wx.StaticText(self, wx.ID_ANY, "Switches")
        self.switches_scrolled = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self.switches_scrolled.SetScrollRate(10, 10)
        self.switches_scrolled_sizer = wx.BoxSizer(wx.VERTICAL)

        self.update_switches_display()

        self.switches_scrolled.SetSizer(self.switches_scrolled_sizer)
        self.switches_scrolled.SetMinSize((250, 150))
        self.switches_scrolled.SetBackgroundColour(self.light_background_secondary)

        self.switches_sizer.Add(self.switches_text, 0, wx.ALL, 5)
        self.switches_sizer.Add(self.switches_scrolled, 1, wx.EXPAND | wx.ALL, 5)

        self.right_sizer.Add(self.switches_sizer, 1, wx.EXPAND | wx.TOP, 5)

        # Run and continue button
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.run_button.SetBackgroundColour(self.color_primary)
        self.run_button.SetBackgroundColour(self.color_primary)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.right_sizer.Add(self.run_button, 0, wx.ALL | wx.EXPAND, 8)

        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue")
        self.continue_button.SetBackgroundColour(self.color_disabled)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.continue_button.Disable()
        self.right_sizer.Add(self.continue_button, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 8)

        # Checking the file supplied using <filepath>
        self.check_errors(path, self.parser)

        # Set main sizer and size of GUI
        self.SetSizeHints(1080, 720)
        self.SetSizer(self.main_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\n"
                          "\nCreated by Mojisola Agboola\n2017\n"
                          "\nModified by Thomas Yam, Maxwell Li, Chloe Yiu\n2024",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)
        if Id == wx.ID_PAGE_SETUP:
            self.toggle_theme(wx.EVT_BUTTON)
        if Id == wx.ID_HELP:
            wx.MessageBox("Controls\n"
                          "\nUpload: Choose the specification file.\n"
                          "\nNo. of Cycles: Change the number of simulation cycles.\n"
                          "\nMonitor: The monitor section displays active monitor points.\n"
                          "\nAdd: Add monitor points.\n"
                          "\nRemove: Delete monitor points.\n"
                          "\nSwitch: Toggle the button to turn the switch on and off.\n"
                          "\nRun: Runs the simulation.\n"
                          "\nContinue: Continues the simulation with updated paramaters.",
                          "Controls", wx.ICON_INFORMATION | wx.OK)

    def disable_monitor_and_simulation_buttons(self):
        """Disable buttons controlling monitor and simulation when file uploaded is invalid"""
        # Disable add and remove button (monitor)
        self.add_monitor_button.Disable()
        self.remove_monitor_button.Disable()

        # Disable run and continue button (simulation)
        self.run_button.Disable()
        self.run_button.SetBackgroundColour(self.color_disabled)
        self.continue_button.Disable()
        self.continue_button.SetBackgroundColour(self.color_disabled)

    def reset_terminal(self):
        """Reset terminal when new file is uploaded"""
        self.terminal.Clear()
        self.terminal.SetDefaultStyle(wx.TextAttr(self.terminal_text_color))
        self.terminal.AppendText(self.welcoming_text)

    def reset_canvas(self):
        """Reset canvas when new file is uploaded"""
        self.canvas.reset_display()
        self.canvas.render("")

    def reset_gui_display(self):
        """Reset gui display when new file is uploaded."""
        self.monitors_scrolled_sizer.Clear(True)
        self.switches_scrolled_sizer.Clear(True)

    def check_errors(self, filename: str, parser: Parser) -> bool:
        """Handles the error checking when a file is uploaded."""
        if parser.parse_network():
            self.reset_canvas()

            # Message on terminal
            self.terminal.SetDefaultStyle(wx.TextAttr(self.terminal_success_color))
            self.terminal.AppendText(f"\nFile {filename} uploaded successfully.")

            # Enable add and remove button
            self.add_monitor_button.Enable()
            self.remove_monitor_button.Enable()

            # Enable run button and disable continue button
            self.run_button.Enable()
            self.run_button.SetBackgroundColour(self.color_primary)
            self.continue_button.Disable()
            self.continue_button.SetBackgroundColour(self.color_disabled)

            return True
        else:
            # Message on terminal
            self.terminal.SetDefaultStyle(wx.TextAttr(self.terminal_error_color))
            self.terminal.AppendText(f"\nError in the specification file {filename}.")

            # Disable monitor and simulation buttons
            self.disable_monitor_and_simulation_buttons()

            # Printing the error message in the GUI terminal
            errors = parser.error_handler.error_output_list
            for error in errors:
                if error:
                    self.terminal.SetDefaultStyle(wx.TextAttr(self.dark_text_color))
                    self.terminal.AppendText(f"\n{error}")

            return False

    def on_upload_button(self, event) -> None:
        """Handles the event when the user clicks the upload button to select the specification file."""
        wildcard = "Text files (*.txt)|*.txt"
        with wx.FileDialog(self, "Open Specification File", wildcard=wildcard,
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

            self.reset_terminal()
            self.reset_canvas()
            self.reset_gui_display()

            # Processing the file
            try:
                # Initialise instances of the inner simulator classes
                names = Names()
                devices = Devices(names)
                network = Network(names, devices)
                monitors = Monitors(names, devices, network)
                try:
                    scanner = Scanner(path, names)
                except UnicodeDecodeError:
                    self.terminal.SetDefaultStyle(wx.TextAttr(self.terminal_error_color))
                    self.terminal.AppendText(f"\nError: file '{path}' is not a unicode text file")
                    self.disable_monitor_and_simulation_buttons()
                    return
                parser = Parser(names, devices, network, monitors, scanner)

                if parser.parse_network():
                    # Instantiate the circuit for the newly uploaded file
                    self.names = names
                    self.devices = devices
                    self.network = network
                    self.monitors = monitors
                    self.scanner = scanner
                    self.parser = parser
                    self.canvas.signals = {}
                    self.canvas.signals_dictionary = {}

                if self.check_errors(filename, parser):
                    # Update the GUI with new monitors and switches
                    self.update_monitors_display()
                    self.update_switches_display()

            except IOError:
                self.terminal.SetDefaultStyle(wx.TextAttr(self.terminal_error_color))
                self.terminal.AppendText(f"File {filename} upload failed.")

    def on_cycles_spin(self, event) -> None:
        """Handle the event when the user changes the spin control value."""
        spin_value = self.cycles_spin.GetValue()
        self.num_cycles = spin_value

    def update_monitors_display(self) -> None:
        """Handle the event of updating the list of monitors upon change."""
        self.monitors_scrolled_sizer.Clear(True)

        # Change text colour depending on theme
        if self.theme == "light":
            color = self.light_text_color
        else:
            color = self.dark_text_color

        if not self.monitors.get_all_identifiers():
            # Empty list, displays a message saying "No active monitors"
            no_monitor_text = wx.StaticText(self.monitors_scrolled, wx.ID_ANY, "No active monitors")
            no_monitor_text.SetForegroundColour(color)
            self.monitors_scrolled_sizer.Add(no_monitor_text, 0, wx.ALL | wx.CENTER, 5)
        else:
            # Populate the display if there are active monitors
            for identifier, (device_name, port_name) in self.monitors.fetch_identifier_to_device_port_name().items():
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

    def update_add_remove_button_states(self) -> None:
        """Updates the enabled/disabled state of the add and remove buttons."""
        self.remove_monitor_button.Enable(bool(self.monitors.get_all_identifiers()))

    def on_add_monitor_button(self, event) -> None:
        """Handle the click event of the add monitor button."""
        dialog = CustomDialogBox(self, "Add Monitor", "Select a device to monitor:",
                                 self.devices.fetch_all_device_names(),
                                 self.theme)
        device_name = None
        device_port = None
        if dialog.ShowModal() == wx.ID_OK:
            device_name = dialog.get_selected_item()
        if device_name:
            device_id = self.names.query(device_name)
            output_input_names = self.devices.fetch_device_output_names(device_id)
            output_input_names += self.devices.fetch_device_input_names(device_id)
            dialog = CustomDialogBox(self, "Add Monitor", "Select a port from the device to monitor:",
                                     output_input_names,
                                     self.theme)
            if dialog.ShowModal() == wx.ID_OK:
                device_port = dialog.get_selected_item()
            if device_port:
                identifier_dialog = IdentifierInputDialog(self, "Enter Identifier",
                                                          "Please enter an identifier for the monitor:", self.theme)
                if identifier_dialog.ShowModal() == wx.ID_OK:
                    identifier = identifier_dialog.get_identifier()

                else:
                    identifier = None

                device_id = self.names.query(device_name)
                port_id = self.names.query(device_port) if device_port != "output" else None
                if identifier and isinstance(identifier, str) and identifier[0].isalpha():
                    error_type = self.monitors.make_monitor(device_id, port_id, identifier)
                    if error_type == self.monitors.NO_ERROR:
                        self.update_monitors_display()
                    elif error_type == self.monitors.MONITOR_IDENTIFIER_PRESENT:
                        wx.MessageBox("Identifier already used, please think of a new one!",
                                      "Error", wx.OK | wx.ICON_ERROR)

                else:
                    wx.MessageBox("Please enter a valid identifier for the monitor! "
                                  "\n(Alphanumerics starting with an alphabet)",
                                  "Error", wx.OK | wx.ICON_ERROR)
                self.update_add_remove_button_states()
        dialog.Destroy()

    def on_remove_monitor_button(self, event) -> None:
        """Handle the click event of the remove monitor button."""
        dialog = CustomDialogBox(self, "Remove Monitor", "Select a Monitor to Remove:",
                                 list(self.monitors.get_all_identifiers()),
                                 self.theme)
        if dialog.ShowModal() == wx.ID_OK:
            identifier = dialog.get_selected_item()
            if identifier:
                self.monitors.remove_monitor_by_identifier(identifier)
                self.update_monitors_display()
                self.update_add_remove_button_states()
                
        dialog.Destroy()

    def update_switches_display(self) -> None:
        """Handle the event of updating the displayed list of switches."""
        # Creating a dictionary of switches
        self.id_switches = self.devices.find_devices(self.devices.SWITCH)
        self.switches_dict = dict()  # {switch name string: switch state}

        for switch_id in self.id_switches:
            switch_name = self.names.get_name_string(switch_id)
            switch_state = self.devices.get_device(switch_id).switch_state
            self.switches_dict[switch_name] = switch_state

        self.switches_scrolled_sizer.Clear(True)

        for switch, state in self.switches_dict.items():
            switch_sizer = wx.BoxSizer(wx.HORIZONTAL)

            label = wx.StaticText(self.switches_scrolled, wx.ID_ANY, switch)
            switch_sizer.Add(label, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)

            initial_label = "1" if state == 1 else "0"
            toggle = wx.ToggleButton(self.switches_scrolled, wx.ID_ANY, initial_label)
            toggle.SetValue(state == 1)
            toggle.SetBackgroundColour(self.light_button_color)
            toggle.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle_switch)

            if self.theme == "light":
                label.SetForegroundColour(self.light_text_color)
                toggle.SetForegroundColour(self.light_text_color)
                toggle.SetBackgroundColour(self.light_button_color)
            elif self.theme == "dark":
                label.SetForegroundColour(self.dark_text_color)
                toggle.SetForegroundColour(self.dark_text_color)
                toggle.SetBackgroundColour(self.dark_button_color)

            self.toggle_button_switch_name[toggle.GetId()] = switch

            switch_sizer.Add(toggle, 0, wx.ALIGN_CENTER_VERTICAL)

            self.switches_scrolled_sizer.Add(switch_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.switches_scrolled.SetSizer(self.switches_scrolled_sizer)
        self.switches_scrolled.Layout()
        self.switches_scrolled_sizer.FitInside(self.switches_scrolled)
        self.switches_scrolled_sizer.Layout()

    def on_toggle_switch(self, event) -> None:
        """Handle the event when the user toggles a switch."""
        button = event.GetEventObject()
        is_on = button.GetValue()  # toggle button is on when clicked (value 1)
        switch_name = self.toggle_button_switch_name[button.GetId()]
        switch_id = self.names.query(switch_name)

        if is_on:
            button.SetLabel("1")
            self.switches_dict[switch_name] = 1
            self.devices.set_switch(switch_id, 1)
        else:
            button.SetLabel("0")
            self.switches_dict[switch_name] = 0
            self.devices.set_switch(switch_id, 0)
        self.Refresh()

    def run_simulation(self) -> bool:
        """Runs the simulation and plot the monitored traces."""
        self.monitors.reset_monitors()

        # Running the simulation
        self.devices.cold_startup()
        for _ in range(self.num_cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                self.terminal.SetDefaultStyle(wx.TextAttr(self.terminal_error_color))
                self.terminal.AppendText(f"\n\nError: network oscillating!!")
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
                print("Error! Network oscillating.")
                return False

        self.signals_dictionary = self.monitors.get_all_monitor_signal()
        self.total_cycles += self.num_cycles
        self.canvas.update_cycle(self.total_cycles)
        self.canvas.render("", self.signals_dictionary)
        return True
    
    def on_run_button(self, event) -> None:
        """Handle the event when the user clicks the run button."""
        self.canvas.reset_display()

        self.run_simulation()

        self.terminal.SetDefaultStyle(wx.TextAttr(self.terminal_text_color))
        self.terminal.AppendText("\n\nRunning simulation...")
        #self.run_button.SetBackgroundColour(self.color_disabled)
        #self.run_button.Disable()
        self.continue_button.Enable()
        self.continue_button.SetBackgroundColour(self.color_primary)

    def on_continue_button(self, event) -> None:
        """Handle the event when the user continue button."""
        self.canvas.reset_display()

        self.continue_simulation()

        self.terminal.SetDefaultStyle(wx.TextAttr(self.terminal_text_color))
        self.terminal.AppendText("\n\nUpdated parameters, continuing simulation...")

    def toggle_theme(self, event) -> None:
        """Handle the event when the user presses the toggle switch menu item to switch between colour themes."""
        if self.theme == "light":
            self.canvas.update_theme(self.theme)
            self.SetBackgroundColour(self.dark_background_color)
            self.cycles_text.SetForegroundColour(self.dark_text_color)
            self.cycles_spin.SetBackgroundColour(self.dark_background_secondary)
            self.cycles_spin.SetForegroundColour(self.dark_text_color)
            self.monitors_text.SetForegroundColour(self.dark_text_color)
            self.monitors_scrolled.SetForegroundColour(self.dark_background_secondary)
            self.monitors_scrolled.SetBackgroundColour(self.dark_background_secondary)
            self.add_monitor_button.SetBackgroundColour(self.dark_button_color)
            self.add_monitor_button.SetForegroundColour(self.dark_text_color)
            self.remove_monitor_button.SetBackgroundColour(self.dark_button_color)
            self.remove_monitor_button.SetForegroundColour(self.dark_text_color)
            self.switches_text.SetForegroundColour(self.dark_text_color)
            self.switches_scrolled.SetBackgroundColour(self.dark_background_secondary)
            self.switches_scrolled.SetForegroundColour(self.dark_background_secondary)

            for child in self.monitors_scrolled.GetChildren():
                if isinstance(child, wx.StaticText):
                    child.SetForegroundColour(self.dark_text_color)
            self.monitors_scrolled.Layout()

            for child in self.switches_scrolled.GetChildren():
                if isinstance(child, wx.StaticText):
                    child.SetForegroundColour(self.dark_text_color)
                elif isinstance(child, wx.ToggleButton):
                    child.SetBackgroundColour(self.dark_button_color)
                    child.SetForegroundColour(self.dark_text_color)

            self.theme = "dark"  # update theme

        elif self.theme == "dark":
            self.canvas.update_theme(self.theme)
            self.SetBackgroundColour(self.light_background_color)
            self.cycles_text.SetForegroundColour(self.light_text_color)
            self.cycles_spin.SetBackgroundColour(self.light_background_secondary)
            self.cycles_spin.SetForegroundColour(self.light_text_color)
            self.monitors_text.SetForegroundColour(self.light_text_color)
            self.monitors_scrolled.SetForegroundColour(self.light_background_secondary)
            self.monitors_scrolled.SetBackgroundColour(self.light_background_secondary)
            self.add_monitor_button.SetBackgroundColour(self.light_button_color)
            self.add_monitor_button.SetForegroundColour(self.light_text_color)
            self.remove_monitor_button.SetBackgroundColour(self.light_button_color)
            self.remove_monitor_button.SetForegroundColour(self.light_text_color)
            self.switches_text.SetForegroundColour(self.light_text_color)
            self.switches_scrolled.SetBackgroundColour(self.light_background_secondary)
            self.switches_scrolled.SetForegroundColour(self.light_background_secondary)

            for child in self.monitors_scrolled.GetChildren():
                if isinstance(child, wx.StaticText):
                    child.SetForegroundColour(self.light_text_color)
            self.monitors_scrolled.Layout()

            for child in self.switches_scrolled.GetChildren():
                if isinstance(child, wx.StaticText):
                    child.SetForegroundColour(self.light_text_color)
                elif isinstance(child, wx.ToggleButton):
                    child.SetBackgroundColour(self.light_button_color)
                    child.SetForegroundColour(self.light_text_color)

            self.theme = "light"  # update theme

        self.Refresh()

    def fetch_cycle(self) -> int:
        """Tracks the total number of simulation cycles."""
        return self.total_cycles
