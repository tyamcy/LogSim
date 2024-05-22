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
    """

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # Draw a sample signal trace
        GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(10):
            x = (i * 20) + 10
            x_next = (i * 20) + 30
            if i % 2 == 0:
                y = 75
            else:
                y = 100
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y)
        GL.glEnd()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
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
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))


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

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Color styles 
        self.primary_color = "#4DA2B4"
        self.primary_color_shade = "#397E8D"

        # Terminal colors
        self.terminal_background_color = "#222222"
        self.terminal_text_color = "#FFFFFF"
        self.success = "#16C60C"
        self.warning = "#F9F1A5"
        self.error = "#E74856"
        
        # Light mode
        self.text_primary = "#000000"
        self.background_color = "#DDDDDD"
        self.background_color_secondary = "#FAFAFA"
        self.canvas_background_color = "#FAFAFA"

        # Dark mode
        self.text_primary_dark = "#FFFFFF"
        self.background_color_dark = "#333333"
        self.background_color_secondary_dark = "#444444"
        self.canvas_background_color_dark = "#444444" 

        # Initial styling (default as light mode)
        self.theme = "light"
        self.SetBackgroundColour(self.background_color)
        self.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Roboto'))


        # Menu bar
        # Configure the menu bar
        menuBar = wx.MenuBar()

        # File menu
        fileMenu = wx.Menu()

        upload_icon = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU, (16, 16))
        theme_icon = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_MENU, (16, 16))
        about_icon = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_MENU, (16, 16))
        exit_icon = wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_MENU, (16, 16))
        
        upload_file_item = wx.MenuItem(fileMenu, wx.ID_FILE, "&Upload file")
        toggle_theme_item = wx.MenuItem(fileMenu, wx.ID_PAGE_SETUP, "&Toggle theme")
        about_item = wx.MenuItem(fileMenu, wx.ID_ABOUT, "&About")
        exit_item = wx.MenuItem(fileMenu, wx.ID_EXIT, "&Exit")
        
        upload_file_item.SetBitmap(upload_icon)
        toggle_theme_item.SetBitmap(theme_icon)
        about_item.SetBitmap(about_icon)
        exit_item.SetBitmap(exit_icon)
        
        fileMenu.Append(upload_file_item)
        fileMenu.AppendSeparator()
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
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")
        self.SetMenuBar(menuBar)

        # Bind event to menuBar
        self.Bind(wx.EVT_MENU, self.on_menu)


        # Main UI layout
        # Canvas for drawing / plotting signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Defining sizers for layout
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL) # Main sizer with everything
        self.left_sizer = wx.BoxSizer(wx.VERTICAL) # Left sizer for the canvas and terminal
        self.right_sizer = wx.BoxSizer(wx.VERTICAL) # Right sizer for the controls
        
        # Terminal
        self.border_panel = wx.Panel(self)
        self.border_panel.SetBackgroundColour(self.terminal_background_color)
        self.terminal_panel = wx.Panel(self.border_panel)
        self.terminal_panel.SetBackgroundColour(self.terminal_background_color)

        self.terminal = wx.TextCtrl(self.terminal_panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.BORDER_NONE )
        self.terminal.SetBackgroundColour(self.terminal_background_color)
        self.terminal.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Consolas'))
        self.terminal.SetForegroundColour(self.terminal_text_color)
        self.terminal.AppendText("Welcome to Logic Simulator")

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

        # Upload file section
        self.upload_file_button = wx.Button(self, wx.ID_ANY, "Upload file")
        self.upload_file_button.SetBackgroundColour(self.primary_color)

        self.upload_file_button.Bind(wx.EVT_BUTTON, self.on_upload_file)

        self.right_sizer.Add(self.upload_file_button, 0, wx.ALL | wx.EXPAND, 10)

        # No of cycles section
        self.cycles_sizer = wx.BoxSizer(wx.VERTICAL)
        self.cycles_text = wx.StaticText(self, wx.ID_ANY, "No. of Cycles")
        self.cycles_spin = wx.SpinCtrl(self, wx.ID_ANY | wx.BORDER_NONE, "10")
        self.cycles_spin.SetRange(1, 250)

        self.cycles_spin.Bind(wx.EVT_SPINCTRL, self.on_cycles_spin)

        self.cycles_sizer.Add(self.cycles_text, 0, wx.EXPAND | wx.ALL, 5)
        self.cycles_sizer.Add(self.cycles_spin, 0, wx.EXPAND | wx.ALL, 5)
        self.right_sizer.Add(self.cycles_sizer, 0, wx.EXPAND | wx.ALL, 5)


        # Monitors section
        self.monitors_sizer = wx.BoxSizer(wx.VERTICAL)
        self.monitors_text = wx.StaticText(self, wx.ID_ANY, "Monitors")
        self.monitors_scrolled = wx.ScrolledWindow(self, style=wx.VSCROLL) 
        self.monitors_scrolled.SetScrollRate(10, 10)
        monitors_scrolled_sizer = wx.BoxSizer(wx.VERTICAL) 

        for i in range(1, 16):
            check = wx.CheckBox(self.monitors_scrolled, label=f"D{i}")  
            monitors_scrolled_sizer.Add(check, 2, wx.ALL, 5) 

        self.monitors_scrolled.SetSizer(monitors_scrolled_sizer)  
        self.monitors_scrolled.SetMinSize((250, 150))
        self.monitors_scrolled.SetBackgroundColour(self.background_color_secondary)
        self.monitors_sizer.Add(self.monitors_text, 0, wx.ALL, 5)  
        self.monitors_sizer.Add(self.monitors_scrolled, 1, wx.EXPAND | wx.ALL, 5)  

        self.right_sizer.Add(self.monitors_sizer, 1, wx.EXPAND | wx.ALL, 5)


        # Switches section
        self.switches_sizer = wx.BoxSizer(wx.VERTICAL)
        self.switches_text = wx.StaticText(self, wx.ID_ANY, "Switches")
        self.switches_scrolled = wx.ScrolledWindow(self, style=wx.VSCROLL) 
        self.switches_scrolled.SetScrollRate(10, 10)
        switches_scrolled_sizer = wx.BoxSizer(wx.VERTICAL) 

        for i in range(1, 8):
            check = wx.CheckBox(self.switches_scrolled, label=f"SW{i}")  
            switches_scrolled_sizer.Add(check, 0, wx.ALL, 5) 

        self.switches_scrolled.SetSizer(switches_scrolled_sizer)  
        self.switches_scrolled.SetMinSize((250, 150))
        self.switches_scrolled.SetBackgroundColour(self.background_color_secondary)

        self.switches_sizer.Add(self.switches_text, 0, wx.ALL, 5)  
        self.switches_sizer.Add(self.switches_scrolled, 1, wx.EXPAND | wx.ALL, 5)  

        self.right_sizer.Add(self.switches_sizer, 1, wx.EXPAND | wx.ALL, 5)


        # Run and continue button
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.run_button.SetBackgroundColour(self.primary_color)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.right_sizer.Add(self.run_button, 0, wx.ALL | wx.EXPAND, 8)

        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue")
        self.continue_button.SetBackgroundColour(self.primary_color)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.right_sizer.Add(self.continue_button, 0, wx.ALL | wx.EXPAND, 8)

        
        # Set main sizer and size of GUI
        self.SetSizeHints(1080, 720)
        self.SetSizer(self.main_sizer)









    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017\n\nModified by Thomas Yam, Maxwell Li, Chloe Yiu\n2024",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)
        if Id == wx.ID_FILE:
            wx.MessageBox("Uploading file")
        if Id == wx.ID_PAGE_SETUP:
            self.toggle_theme()
        if Id == wx.ID_HELP:
            wx.MessageBox("Help")

    def on_cycles_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.cycles_spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""        
        self.canvas.render("Run button pressed.")
        self.terminal.SetDefaultStyle(wx.TextAttr(wx.WHITE))
        self.terminal.AppendText("\nRunning simulation...")
        self.run_button.Disable()

    def on_continue_button(self, event):
        """Handle the event when the user continue button."""
        self.canvas.render("Continue button pressed.")
        self.terminal.SetDefaultStyle(wx.TextAttr(wx.WHITE))
        self.terminal.AppendText("\nRunning simulation...")

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        text_box_value = self.text_box.GetValue()
        text = "".join(["New text box value: ", text_box_value])
        self.canvas.render(text)

    def on_upload_file(self, event):
        """Handle the event when the user presses the upload file button."""
        text = "Uploading file..."
        self.canvas.render(text)
        self.terminal.SetDefaultStyle(wx.TextAttr("#E12CAD"))
        self.terminal.AppendText(f"\n{text}")
    
    def toggle_theme(self):
        """Handle the event when the user presses the toggle switch menu item to switch between colour themes."""
        if self.theme == "light":  
            self.SetBackgroundColour(self.background_color_dark)
            self.cycles_text.SetForegroundColour(self.text_primary_dark)
            self.cycles_spin.SetBackgroundColour(self.background_color_secondary_dark)
            self.cycles_spin.SetForegroundColour(self.text_primary_dark)
            self.monitors_text.SetForegroundColour(self.text_primary_dark)
            self.monitors_scrolled.SetForegroundColour(self.background_color_secondary_dark)
            self.monitors_scrolled.SetBackgroundColour(self.background_color_secondary_dark)
            self.switches_text.SetForegroundColour(self.text_primary_dark)
            self.switches_scrolled.SetBackgroundColour(self.background_color_secondary_dark)
            self.switches_scrolled.SetForegroundColour(self.background_color_secondary_dark)

            self.theme = "dark" # Update theme

        elif self.theme == "dark":
            self.SetBackgroundColour(self.background_color)
            self.cycles_text.SetForegroundColour(self.text_primary)
            self.cycles_spin.SetBackgroundColour(self.background_color_secondary)
            self.cycles_spin.SetForegroundColour(self.text_primary)
            self.monitors_text.SetForegroundColour(self.text_primary)
            self.monitors_scrolled.SetForegroundColour(self.background_color_secondary)
            self.monitors_scrolled.SetBackgroundColour(self.background_color_secondary)
            self.switches_text.SetForegroundColour(self.text_primary)
            self.switches_scrolled.SetBackgroundColour(self.background_color_secondary)
            self.switches_scrolled.SetForegroundColour(self.background_color_secondary)

            self.theme = "light" # Update theme

        self.Refresh()