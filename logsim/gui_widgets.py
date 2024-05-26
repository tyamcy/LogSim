import wx

class CustomDialogBox(wx.Dialog):
    """Custom dialog box for the add and remove buttons.

    Parameters
    ----------
    parent: parent window.
    title: title of the dialog box.
    message: message to display on the dialog box.
    choices: options listed in the dialog box. 

    Public methods
    --------------
    getStringSelection(self): 
    """

    def __init__(self, parent, title, message, choices):
        super().__init__(parent, title=title)
        self.selection = None

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        text = wx.StaticText(self, label=message)
        sizer.Add(text, flag=wx.ALL, border=5)

        self.list_box = wx.ListBox(self, choices=choices, style=wx.LB_SINGLE | wx.LB_NEEDED_SB)
        self.list_box.SetSizeHints(minSize=(150, 150))
        sizer.Add(self.list_box, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        sizer.Add(button_sizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(sizer)
        self.Fit()

    def getStringSelection(self):
        selection_index = self.list_box.GetSelection()
        if selection_index != wx.NOT_FOUND:
            return self.list_box.GetString(selection_index)
        return None