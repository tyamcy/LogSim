import wx
import wx.glcanvas as wxcanvas
import math
import numpy as np
from OpenGL import GL, GLU, GLUT


class Canvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    plot_grid(self, x_start, no_of_monitors, cycles): Adds grid lines to the plot in 2D.

    plot_grid_3d(self, x_start, z_start, no_of_monitors, cycles): Adds grid planes to the plot in 3D.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.

    render_text_3d(self, text, x_pos, y_pos, z_pos): Handle text drawing operations for 3D.

    update_theme(self, theme): Updates the colour palette.

    reset_display(self): Return to the initial viewpoint at the origin.

    update_cycle(self, cycle): Keeps track of the total number of simulation cycles.

    clear_display(self): Clear the canvas.

    change_mode(self): Switching between 2D and 3D.

    toggle_grid(self): Handles the event of turning the grids on and off.
    """

    def __init__(self, parent):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)
        self.gui = parent

        self.no_cycles = 0
        self.total_cycles = 0
        self.signals = {}

        self.mode = "2D" # 2D or 3D
        self.theme = "light"

        # Colour themes
        self.light_color_background = (0.98, 0.98, 0.98, 1)
        self.light_color_text = (0, 0, 0)
        self.light_color_trace = (0, 0, 0)
        self.light_color_grid = (0.8, 0.8, 0.8)
        self.light_color_grid_adaptive = (0.6, 0.6, 0.6)

        self.dark_color_background = (0.267, 0.267, 0.267, 1)
        self.dark_color_text = (1, 1, 1)
        self.dark_color_trace = (1, 1, 1)
        self.dark_color_grid = (0.4, 0.4, 0.4)
        self.dark_color_grid_adaptive = (0.6, 0.6, 0.6)

        # Initialise colours
        self.color_background = self.light_color_background
        self.color_text = self.light_color_text
        self.color_trace = self.light_color_trace
        self.color_trace_3d_high = (0.3, 0.63, 0.706)
        self.color_trace_3d_low = (0.22, 0.49, 0.553)
        self.color_grid = self.light_color_grid
        self.color_grid_adaptive = self.light_color_grid_adaptive

        # Trace widths
        self.width_grid = 0.5
        self.width_grid_adaptive = 1.5
        self.width_trace = 3

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1
        self.zoom_current = 1

        # Flag to turn grid on and off
        self.grid_on = True

        # Constants for OpenGL materials and lights
        self.mat_diffuse = [0.0, 0.0, 0.0, 1.0]
        self.mat_no_specular = [0.0, 0.0, 0.0, 0.0]
        self.mat_no_shininess = [0.0]
        self.mat_specular = [0.5, 0.5, 0.5, 1.0]
        self.mat_shininess = [50.0]
        self.top_right = [1.0, 1.0, 1.0, 0.0]
        self.straight_on = [0.0, 0.0, 1.0, 0.0]
        self.no_ambient = [0.0, 0.0, 0.0, 1.0]
        self.dim_diffuse = [0.5, 0.5, 0.5, 1.0]
        self.bright_diffuse = [1.0, 1.0, 1.0, 1.0]
        self.med_diffuse = [0.75, 0.75, 0.75, 1.0]
        self.full_specular = [0.5, 0.5, 0.5, 1.0]
        self.no_specular = [0.0, 0.0, 0.0, 1.0]

        # Initialise the scene rotation matrix
        self.scene_rotate = np.identity(4, "f")
        self.scene_origin = np.array([[9.9997663e-01, 6.9979425e-03, -6.0286466e-03, 0],
                             [9.6203759e-05, 6.4476335e-01, 7.6438475e-01, 0],
                             [9.2356848e-03, -0.67397875, 0.7387122, 0],
                             [0, 0, 0, 1]], "f")

        self.scene_rotate = self.scene_origin.copy()

        # Initialise variables for zooming
        self.zoom_3d = 1

        # Offset between viewpoint and origin of the scene
        self.depth_offset = 1000

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        print("run")
        size = self.GetClientSize()
        self.SetCurrent(self.context)

        GL.glClearColor(*self.color_background)

        if self.mode == "2D":
            GL.glDrawBuffer(GL.GL_BACK)
            GL.glViewport(0, 0, size.width, size.height)
            GL.glMatrixMode(GL.GL_PROJECTION)
            GL.glLoadIdentity()
            GL.glOrtho(0, size.width, 0, size.height, -1, 1)
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glLoadIdentity()
            GL.glTranslated(self.pan_x, self.pan_y, 0.0)
            GL.glScaled(self.zoom, self.zoom, self.zoom)

        elif self.mode == "3D":
            GL.glViewport(0, 0, size.width, size.height)

            GL.glMatrixMode(GL.GL_PROJECTION)
            GL.glLoadIdentity()
            GLU.gluPerspective(45, size.width / size.height, 10, 10000)
 
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glLoadIdentity()  # lights positioned relative to the viewer
            GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, self.no_ambient)
            GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, self.med_diffuse)
            GL.glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, self.no_specular)
            GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, self.top_right)
            GL.glLightfv(GL.GL_LIGHT1, GL.GL_AMBIENT, self.no_ambient)
            GL.glLightfv(GL.GL_LIGHT1, GL.GL_DIFFUSE, self.dim_diffuse)
            GL.glLightfv(GL.GL_LIGHT1, GL.GL_SPECULAR, self.no_specular)
            GL.glLightfv(GL.GL_LIGHT1, GL.GL_POSITION, self.straight_on)

            GL.glMaterialfv(GL.GL_FRONT, GL.GL_SPECULAR, self.mat_specular)
            GL.glMaterialfv(GL.GL_FRONT, GL.GL_SHININESS, self.mat_shininess)
            GL.glMaterialfv(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE,
                            self.mat_diffuse)
            GL.glColorMaterial(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE)
 
            GL.glDepthFunc(GL.GL_LEQUAL)
            GL.glShadeModel(GL.GL_SMOOTH)
            GL.glDrawBuffer(GL.GL_BACK)
            GL.glCullFace(GL.GL_BACK)
            GL.glEnable(GL.GL_COLOR_MATERIAL)
            GL.glEnable(GL.GL_CULL_FACE)
            GL.glEnable(GL.GL_DEPTH_TEST)
            GL.glEnable(GL.GL_LIGHTING)
            GL.glEnable(GL.GL_LIGHT0)
            GL.glEnable(GL.GL_LIGHT1)
            GL.glEnable(GL.GL_NORMALIZE)

            # Viewing transformation - set the viewpoint back from the scene
            GL.glTranslatef(0.0, 0.0, -self.depth_offset)

            # Modelling transformation - pan, zoom and rotate
            GL.glTranslatef(self.pan_x, self.pan_y, 0.0)
            GL.glMultMatrixf(self.scene_rotate)
            GL.glScalef(self.zoom, self.zoom, self.zoom)
        self.init = True
 
    def render(self, text: str, signals={}) -> None:
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        if signals:
            self.signals = signals  # updating the dictionary of signal values

        if self.signals:
            identifier_dict = self.gui.monitors.fetch_identifier_to_device_port_name()
            no_of_monitors = len(identifier_dict.keys())
            self.no_cycles = len(list(self.signals.values())[0])

            if self.mode == "2D":
                x_start = 60
                y_start = 50
                width = 30  # width of a cycle
                height = 30  # height of a pulse
                y_diff = 75  # distance between different plots 

                # Plot x-axis, no of cycles
                self.render_text("0", x_start, y_start - 20)

                if self.grid_on:
                   self.plot_grid(x_start, no_of_monitors, self.no_cycles)
                else:
                   self.render_text(str(self.no_cycles), x_start + width * self.no_cycles, y_start - 20)

                for index, (identifier, (device_name, port_name)) in enumerate(identifier_dict.items()):
                    device_id = self.gui.names.query(device_name)
                    port_id = self.gui.names.query(port_name) if port_name else None
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
                    GL.glLineWidth(self.width_trace)
                    GL.glBegin(GL.GL_LINE_STRIP)

                    for value in trace:
                        if value == 0:
                            y_curr = y
                        elif value == 1:
                            y_curr = y + height
                            
                        GL.glVertex2f(x, y_curr)
                        GL.glVertex2f(x_next, y_curr)

                        # Update x
                        x = x_next
                        x_next += width

                    GL.glEnd()
                    x_start = 60

            elif self.mode == "3D":
                x_start = 60
                z_start = 50
                width = 30  
                height_low = 1  
                height_high = 25  
                z_spacing = 75  # spacing between different signal plots in depth

                self.render_text_3d("0", x_start - 15, -8, z_start + 55)

                if self.grid_on:
                   self.plot_grid_3d(x_start, z_start, no_of_monitors, self.no_cycles)
                else:
                   self.render_text_3d(str(self.no_cycles), x_start + width * self.no_cycles - 15, -8, z_start + 55)

                for index, (identifier, (device_name, port_name)) in enumerate(identifier_dict.items()):
                    device_id = self.gui.names.query(device_name)
                    port_id = self.gui.names.query(port_name) if port_name else None
                    trace = self.signals[(device_id, port_id)]

                    # Initialize z position for the current trace
                    z_pos = z_start - index * z_spacing

                    # Render the identifier name in 3D
                    self.render_text_3d(identifier, 20, -8, z_pos)

                    # Check x starting position
                    if self.total_cycles > len(trace):
                        x_start += (self.total_cycles - len(trace)) * width

                    # Initialize x position
                    x = x_start

                    # Loop through each value in the trace to plot cuboids
                    for value in trace:
                        if value == 0:
                            height = height_low
                            GL.glColor3f(*self.color_trace_3d_low)
                        elif value == 1:
                            height = height_high
                            GL.glColor3f(*self.color_trace_3d_high)

                        # Draw cuboid for the signal value
                        self._draw_cuboid(x, z_pos, width // 2, width // 2, height)

                        # Move x position for the next cycle
                        x += width

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def plot_grid(self, x_start: int, no_of_monitors: int, cycles: int) -> None:
        """Adds grid lines to the plot in 2D."""
        width = 30
        x = x_start + width
        y_start = 40
        y_end = y_start + no_of_monitors * 75  - 20

        for i in range(1, cycles + 1):
            # Thicker grid lines for multiples of 5 and annotate
            if i % 5 == 0:
                self.render_text(str(i), x, 30)

                GL.glColor3f(*self.color_grid_adaptive)
                GL.glLineWidth(self.width_grid_adaptive)
                GL.glBegin(GL.GL_LINE_STRIP)

                GL.glVertex2f(x, y_start)
                GL.glVertex2f(x, y_end)

                GL.glEnd()
            else:
                GL.glColor3f(*self.color_grid)
                GL.glLineWidth(self.width_grid)
                GL.glBegin(GL.GL_LINE_STRIP)

                GL.glVertex2f(x, y_start)
                GL.glVertex2f(x, y_end)

                GL.glEnd()

            x += width

    def _setup_3d_grid_material(self) -> None:
        """Setup material properties to emulate a glassy material."""
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthMask(False)  
        GL.glEnable(GL.GL_COLOR_MATERIAL)
        GL.glColorMaterial(GL.GL_FRONT_AND_BACK, GL.GL_AMBIENT_AND_DIFFUSE)

        # Define material properties for a glass-like look
        ambient = [0.1, 0.1, 0.1, 0.5]
        diffuse = [0.6, 0.6, 0.6, 0.5]  
        specular = [0.9, 0.9, 0.9, 0.5] 
        shininess = 30.0  

        GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_AMBIENT, ambient)
        GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_DIFFUSE, diffuse)
        GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_SPECULAR, specular)
        GL.glMaterialf(GL.GL_FRONT_AND_BACK, GL.GL_SHININESS, shininess)

    def plot_grid_3d(self, x_start: int, z_start: int, no_of_monitors: int, cycles: int) -> None:
        """Adds grid planes to the plot in 3D."""
        self._setup_3d_grid_material()

        width = 30
        z_depth = 75 * (no_of_monitors - 1)

        x = x_start + 15
        y_grid_bottom = -15 
        y_grid_top = 45  
        z_offset = 30
        z_start += z_offset
        z_end = z_start - z_depth - z_offset * 2

        for i in range(1, cycles + 1):
            if i % 5 == 0:
                if self.theme == "light":
                    color = (*self.color_grid_adaptive, 0.5)  
                elif self.theme == "dark":
                    color = (0.7, 0.7, 0.2, 0.8)
                self.render_text_3d(str(i), x, -8, z_start + 25)
            else:
                if self.theme == "light":
                    color = (*self.color_grid, 0.2)
                elif self.theme == "dark":
                    color = (0.7, 0.7, 0.5, 0.4)

            # Draw grid planes
            GL.glColor4f(*color) 
            GL.glBegin(GL.GL_QUADS)
            # Front face
            GL.glVertex3f(x, y_grid_bottom, z_start)
            GL.glVertex3f(x, y_grid_top, z_start)
            GL.glVertex3f(x, y_grid_top, z_end)
            GL.glVertex3f(x, y_grid_bottom, z_end)
            # Back face 
            GL.glVertex3f(x, y_grid_bottom, z_end)
            GL.glVertex3f(x, y_grid_top, z_end)
            GL.glVertex3f(x, y_grid_top, z_start)
            GL.glVertex3f(x, y_grid_bottom, z_start)
            GL.glEnd()

            # Update x for the next cycle
            x += width
        
    def _draw_cuboid(self, x_pos, z_pos, half_width, half_depth, height) -> None:
        """Draw a cuboid.

        Draw a cuboid at the specified position, with the specified
        dimensions.
        """
        GL.glBegin(GL.GL_QUADS)
        GL.glNormal3f(0, -1, 0)
        GL.glVertex3f(x_pos - half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos + half_depth)
        GL.glNormal3f(0, 1, 0)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos + half_depth)
        GL.glNormal3f(-1, 0, 0)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos + half_depth)
        GL.glNormal3f(1, 0, 0)
        GL.glVertex3f(x_pos + half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos + half_depth)
        GL.glNormal3f(0, 0, -1)
        GL.glVertex3f(x_pos - half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos - half_depth)
        GL.glNormal3f(0, 0, 1)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos + half_depth)
        GL.glEnd()

    def on_paint(self, event) -> None:
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        self.render("")

    def on_size(self, event) -> None:
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event) -> None:
        """Handle mouse events."""
        if self.mode == "2D":
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

            self.Refresh()  # triggers the paint event

        elif self.mode == "3D":
            self.SetCurrent(self.context)

            if event.ButtonDown():
                self.last_mouse_x = event.GetX()
                self.last_mouse_y = event.GetY()

            if event.Dragging():
                GL.glMatrixMode(GL.GL_MODELVIEW)
                GL.glLoadIdentity()
                x = event.GetX() - self.last_mouse_x
                y = event.GetY() - self.last_mouse_y
                if event.LeftIsDown():
                    GL.glRotatef(math.sqrt((x * x) + (y * y)), y, x, 0)
                if event.MiddleIsDown():
                    GL.glRotatef((x + y), 0, 0, 1)
                if event.RightIsDown():
                    self.pan_x += x
                    self.pan_y -= y
                GL.glMultMatrixf(self.scene_rotate)
                GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX, self.scene_rotate)
                self.last_mouse_x = event.GetX()
                self.last_mouse_y = event.GetY()
                self.init = False

            if event.GetWheelRotation() < 0:
                self.zoom *= (1.0 + (
                    event.GetWheelRotation() / (20 * event.GetWheelDelta())))
                self.init = False

            if event.GetWheelRotation() > 0:
                self.zoom /= (1.0 - (
                    event.GetWheelRotation() / (20 * event.GetWheelDelta())))
                self.init = False

            self.Refresh()  # triggers the paint event

    def render_text(self, text: str, x_pos: int, y_pos: int) -> None:
        """Handle text drawing operations for 2D."""
        GL.glDisable(GL.GL_LIGHTING)
        GL.glColor3f(*self.color_text)
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))
    
    def render_text_3d(self, text:str, x_pos:int, y_pos:int, z_pos:int) -> None:
        """Handle text drawing operations for 3D."""
        GL.glDisable(GL.GL_LIGHTING)
        GL.glColor3f(*self.color_text) 
        GL.glRasterPos3f(x_pos, y_pos, z_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_10

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos3f(x_pos, y_pos, z_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

        GL.glEnable(GL.GL_LIGHTING)

    def update_theme(self, theme: str) -> None:
        """Handle background colour update."""
        self.SetCurrent(self.context)
        if theme == "dark":
            self.theme = "light"
            self.color_background = self.light_color_background
            self.color_text = self.light_color_text
            self.color_trace = self.light_color_trace
            self.color_grid = self.light_color_grid
            self.color_grid_adaptive = self.light_color_grid_adaptive
            GL.glClearColor(*self.light_color_background)
            GL.glColor3f(*self.light_color_text)
        elif theme == "light":
            self.theme = "dark"
            self.color_background = self.dark_color_background
            self.color_text = self.dark_color_text
            self.color_trace = self.dark_color_trace
            self.color_grid = self.dark_color_grid
            self.color_grid_adaptive = self.dark_color_grid_adaptive
            GL.glClearColor(*self.dark_color_background) 
            GL.glColor3f(*self.dark_color_text)

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self.SwapBuffers()

    def reset_display(self) -> None:
        """Return to the initial viewpoint at the origin."""
        # Reset location parameters
        if self.mode == "2D":
            self.pan_x = 0
            self.pan_y = 0
            self.zoom = 1
        elif self.mode == "3D":
            self.pan_x = -400
            self.pan_y = -90
            self.zoom = 2
            self.scene_rotate = self.scene_origin.copy()
      
        self.init = False
        self.on_paint(None)
        self.render("")

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

    def change_mode(self) -> None:
        """Switching between 2D and 3D."""
        if self.mode == "2D":
            self.mode = "3D"
        elif self.mode == "3D":
            self.mode = "2D"
        self.reset_display()
        self.render("")

    def toggle_grid(self) -> None:
        """Handles the event of turning the grids on and off."""
        if self.grid_on:
            self.grid_on = False 
        else:
            self.grid_on = True
        self.render("")
