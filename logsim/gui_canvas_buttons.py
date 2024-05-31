import wx
import os

from gui_color import Color

class CanvasSettingButtons:
    def __init__(self, parent):
        self.canvas_buttons_panel = wx.Panel(parent)
        self.canvas_buttons_panel.SetBackgroundColour(Color.light_background_color)

        self.container_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # self.zoom_to_fit_button = wx.Button(self.canvas_buttons_panel, label="Fit")
        self.toggle_mode_button = wx.Button(self.canvas_buttons_panel, label="2D/3D")
        
        self.container_sizer.AddStretchSpacer()  
        # self.container_sizer.Add(self.zoom_to_fit_button, flag=wx.RIGHT, border=5) 
        self.container_sizer.Add(self.toggle_mode_button, flag=wx.RIGHT, border=5) 

        self.canvas_buttons_panel.SetSizer(self.container_sizer)
        self.canvas_buttons_panel.Layout()
    
    def on_toggle_canvas_mode(self, event, mode:str) -> None:
        """Handle the event of changing between 2D and 3D display."""
        if mode == "2D":
            mode == "3D"
        elif mode == "3D":
            mode == "2D"

