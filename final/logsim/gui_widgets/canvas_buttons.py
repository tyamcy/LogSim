"""Implement the buttons for changing the OpenGL canvas settings.

Used in the Logic Simulator project to enable the user to adjust the plot display canvas.

Classes:
--------
CanvasSettingButtons - contains all buttons for adjusting the canvas.
"""
import wx

from logsim.gui_widgets.color import Color
from logsim.internationalization import _


class CanvasSettingButtons:
    """
    A class responsible for managing the interactive buttons that control settings
    on a GLCanvas.

    This class creates a panel with buttons that allow the user to reset the canvas
    to its origin, toggle grid visibility, and switch between 2D and 3D display modes.

    Parameters
    ----------
    parent: parent window.

    Public methods
    --------------
    on_toggle_canvas_mode(self, event): Handles switching between 2D and 3D display modes.

    on_toggle_grids(self, event): Toggles the grid visibility on the canvas.

    reset_origin(self, event): Resets the view of the canvas to the origin point.

    save_screenshot(self, event): Handles the event of taking a screen capture of the current canvas.
    """
    def __init__(self, parent):
        """Initialize buttons and layout."""
        self.gui = parent

        self.canvas = parent.canvas

        self.canvas_buttons_panel = wx.Panel(parent)
        self.canvas_buttons_panel.SetBackgroundColour(Color.light_background_color)

        self.container_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.screenshot_button = wx.Button(self.canvas_buttons_panel, label=_(u"Capture"))
        self.origin_button = wx.Button(self.canvas_buttons_panel, label=_(u"Origin"))
        self.grid_button = wx.Button(self.canvas_buttons_panel, label=_(u"Grid"))
        self.toggle_mode_button = wx.Button(self.canvas_buttons_panel, label=_(u"2D/3D"))

        self.screenshot_button.Bind(wx.EVT_BUTTON, self.save_screenshot)
        self.origin_button.Bind(wx.EVT_BUTTON, self.reset_origin)
        self.grid_button.Bind(wx.EVT_BUTTON, self.on_toggle_grids)
        self.toggle_mode_button.Bind(wx.EVT_BUTTON, self.on_toggle_canvas_mode)
        
        self.container_sizer.Add(self.screenshot_button, flag=wx.LEFT, border = 5)
        self.container_sizer.AddStretchSpacer()  
        self.container_sizer.Add(self.origin_button, flag=wx.RIGHT, border=5) 
        self.container_sizer.Add(self.grid_button, flag=wx.RIGHT, border=5)
        self.container_sizer.Add(self.toggle_mode_button, flag=wx.RIGHT, border=5) 

        self.canvas_buttons_panel.SetSizer(self.container_sizer)
        self.canvas_buttons_panel.Layout()

    def on_toggle_canvas_mode(self, event) -> None:
        """Handle the event of changing between 2D and 3D display."""
        self.canvas.change_mode()

    def on_toggle_grids(self, event) -> None:
        """Handles the event of toggling the grids on and off."""
        self.canvas.toggle_grid()

    def reset_origin(self, event) -> None:
        """Handles the event of setting the view point back to the origin."""
        self.canvas.reset_display()

    def save_screenshot(self, event) -> None:
        """Handles the event of taking a screen capture of the current canvas."""
        image = self.canvas.screenshot()

        wildcard = "PNG files (*.png)|*.png"
        with wx.FileDialog(self.gui, _(u"Save PNG image"), wildcard=wildcard,
                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            # Set the default file path to user's Documents directory
            fileDialog.SetDirectory(wx.StandardPaths.Get().GetDocumentsDir())
            fileDialog.SetFilename("capture.png")  # default file name

            # Cancel 
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return 

            # Save the image
            pathname = fileDialog.GetPath()
            try:
                text = _(u"\n\nScreen capture saved")
                self.gui.terminal.append_text(Color.terminal_text_color, text)
                if not image.SaveFile(pathname, wx.BITMAP_TYPE_PNG):
                    wx.LogError(_(u"Cannot save current data in file '{pathname}'.").format(pathname=pathname))
            except Exception as e:
                wx.LogError(_(u"Failed to save file: {}").format(e))
                return

