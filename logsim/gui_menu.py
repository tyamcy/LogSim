import wx


class FileMenu(wx.Menu):
    def __init__(self):
        super().__init__()
        theme_icon = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_MENU, (16, 16))
        about_icon = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_MENU, (16, 16))
        exit_icon = wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_MENU, (16, 16))
        toggle_theme_item = wx.MenuItem(self, wx.ID_PAGE_SETUP, "&Toggle theme")
        about_item = wx.MenuItem(self, wx.ID_ABOUT, "&About")
        exit_item = wx.MenuItem(self, wx.ID_EXIT, "&Exit")
        toggle_theme_item.SetBitmap(theme_icon)
        about_item.SetBitmap(about_icon)
        exit_item.SetBitmap(exit_icon)
        self.Append(toggle_theme_item)
        self.AppendSeparator()
        self.Append(about_item)
        self.Append(exit_item)


class HelpMenu(wx.Menu):
    def __init__(self):
        super().__init__()
        help_icon = wx.ArtProvider.GetBitmap(wx.ART_HELP, wx.ART_MENU, (16, 16))
        help_item = wx.MenuItem(self, wx.ID_HELP, "&Quick Guide")
        help_item.SetBitmap(help_icon)
        self.Append(help_item)


class MenuBar(wx.MenuBar):
    def __init__(self, parent, function):
        super().__init__()
        self.Append(FileMenu(), "&Menu")
        self.Append(HelpMenu(), "&Help")

        parent.SetMenuBar(self)
        parent.Bind(wx.EVT_MENU, function)


