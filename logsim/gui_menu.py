import wx

from base_app import _



class FileMenu(wx.Menu):
    def __init__(self):
        super().__init__()
        file_icon = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU, (16, 16))
        theme_icon = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_MENU, (16, 16))
        about_icon = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_MENU, (16, 16))
        exit_icon = wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_MENU, (16, 16))
        file_item = wx.MenuItem(self, wx.ID_FILE, _(u"Open file"))
        toggle_theme_item = wx.MenuItem(self, wx.ID_PAGE_SETUP, _(u"Toggle theme"))
        about_item = wx.MenuItem(self, wx.ID_ABOUT, _(u"About"))
        exit_item = wx.MenuItem(self, wx.ID_EXIT, _(u"Exit"))
        file_item.SetBitmap(file_icon)
        toggle_theme_item.SetBitmap(theme_icon)
        about_item.SetBitmap(about_icon)
        exit_item.SetBitmap(exit_icon)
        self.Append(file_item)
        self.AppendSeparator()
        self.Append(toggle_theme_item)
        self.AppendSeparator()
        self.Append(about_item)
        self.Append(exit_item)


class HelpMenu(wx.Menu):
    def __init__(self):
        super().__init__()
        help_icon = wx.ArtProvider.GetBitmap(wx.ART_HELP, wx.ART_MENU, (16, 16))
        help_item = wx.MenuItem(self, wx.ID_HELP, _(u"Quick Guide"))
        help_item.SetBitmap(help_icon)
        self.Append(help_item)


class MenuBar(wx.MenuBar):
    def __init__(self, parent):
        super().__init__()
        self.Append(FileMenu(), _(u"File"))
        self.Append(HelpMenu(), _(u"Help"))

        self.gui = parent
        self.gui.SetMenuBar(self)
        self.gui.Bind(wx.EVT_MENU, self.on_menu)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.gui.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox(_(u"Logic Simulator\n"
                            "\nCreated by Mojisola Agboola\n2017\n"
                            "\nModified by Thomas Yam, Maxwell Li, Chloe Yiu\n2024"),
                          _(u"About Logsim"), wx.ICON_INFORMATION | wx.OK)
        if Id == wx.ID_FILE:
            return
        if Id == wx.ID_PAGE_SETUP:
            self.gui.toggle_theme(wx.EVT_BUTTON)
        if Id == wx.ID_HELP:
            wx.MessageBox(_(u"Controls\n"
                            "\nUpload: Choose the specification file.\n"
                            "\nNo. of Cycles: Change the number of simulation cycles.\n"
                            "\nMonitor: The monitor section displays active monitor points.\n"
                            "\nAdd: Add monitor points.\n"
                            "\nRemove: Delete monitor points.\n"
                            "\nSwitch: Toggle the button to turn the switch on and off.\n"
                            "\nRun: Runs the simulation.\n"
                            "\nContinue: Continues the simulation with updated paramaters."),
                          _(u"Controls"), wx.ICON_INFORMATION | wx.OK)
