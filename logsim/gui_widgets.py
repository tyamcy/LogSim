import wx

class CustomDialogBox(wx.Dialog):
    """Custom dialog box for the add and remove buttons.

    Parameters
    ----------
    parent: parent window.
    title: title of the dialog box.
    message: message to display on the dialog box.
    choices: options listed in the dialog box. 
    theme: colour theme of the GUI.

    Public methods
    --------------
    getSelectedItem(self): 
    """

    def __init__(self, parent, title, message, choices, theme):
        super().__init__(parent, title=title)
        self.selection = None

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

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        text = wx.StaticText(self, label=message)
        sizer.Add(text, flag=wx.ALL, border=5)

        self.list_box = wx.ListBox(self, choices=choices, style=wx.LB_SINGLE | wx.LB_NEEDED_SB)
        self.list_box.SetSizeHints(minSize=(250, 150))

        if theme == "light":
            self.list_box.SetBackgroundColour(self.light_background_secondary)
            self.list_box.SetForegroundColour(self.light_text_color)
            self.SetBackgroundColour(self.light_background_color)
            self.SetForegroundColour(self.light_text_color)
            text.SetForegroundColour(self.light_text_color)
        elif theme == "dark":
            self.list_box.SetBackgroundColour(self.dark_background_secondary)
            self.list_box.SetForegroundColour(self.dark_text_color)
            self.SetBackgroundColour(self.dark_background_color)
            self.SetForegroundColour(self.dark_text_color)
            text.SetForegroundColour(self.dark_text_color)

        sizer.Add(self.list_box, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        sizer.Add(button_sizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(sizer)
        self.Fit()

    def getSelectedItem(self):
        selection_index = self.list_box.GetSelection()
        if selection_index != wx.NOT_FOUND:
            return self.list_box.GetString(selection_index)
        return None