import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

from names import Names
from devices import Devices
from monitors import Monitors
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

    clear_display(self): Clear the canvas.
    """

    def __init__(self, parent, parser: Parser):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        self.parser = parser
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
            identifier_dict = self.parser.monitors.fetch_identifier_to_device_port_name()
            for index, (identifier, (device_name, port_name)) in enumerate(identifier_dict.items()):
                device_id = self.parser.names.query(device_name)
                port_id = self.parser.names.query(port_name) if port_name else None
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

    def clear_display(self) -> None:
        """Clear all content from the canvas."""
        self.SetCurrent(self.context)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self.signals.clear()
        self.init = False
        self.Refresh()

    def reset_canvas(self, parser: Parser):
        """Reset canvas when new file is uploaded"""
        self.parser = parser
        self.signals = {}
        self.signals_dictionary = {}
        self.clear_display()
