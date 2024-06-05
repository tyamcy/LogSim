"""Implement the menu bar for the GUI.

Used in the Logic Simulator project to enable the user to access different option via the menu bar.

Classes:
--------
FileMenu - configures the file menu.
HelpMenu - configures the help menu.
MenuBar - configures the entire menu bar.
"""
import wx
import os


from logsim.names import Names
from logsim.devices import Devices
from logsim.network import Network
from logsim.monitors import Monitors
from logsim.scanner import Scanner
from logsim.parse import Parser

from logsim.gui_widgets.color import Color
from logsim.internationalization import _


class FileMenu(wx.Menu):
    """Configure the file sub-menu.

    This class configures the file sub-menu.

    Parameters
    ----------

    Public methods
    --------------
    """

    def __init__(self):
        """Initializes the file menu."""
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
    """Configure the help sub-menu.

    This class configures the help sub-menu.

    Parameters
    ----------

    Public methods
    --------------
    """

    def __init__(self):
        """Initializes the help menu."""
        super().__init__()
        help_icon = wx.ArtProvider.GetBitmap(wx.ART_HELP, wx.ART_MENU, (16, 16))
        help_item = wx.MenuItem(self, wx.ID_HELP, _(u"Quick Guide"))
        help_item.SetBitmap(help_icon)
        self.Append(help_item)


class MenuBar(wx.MenuBar):
    """Configure the menu bar.

    This class configures the menu bar by adding all sub-menus and binds the functionality of each option.

    Parameters
    ----------
    parent: parent window.

    Public methods
    --------------
    on_menu(self, event): Handle the event when the user selects a menu item.

    on_upload(self, event): Handles the event when the user clicks the upload button to select the
    specification file.
    """

    def __init__(self, parent):
        """Initializes the menu bar."""
        super().__init__()
        self.Append(FileMenu(), _(u"Menu"))
        self.Append(HelpMenu(), _(u"Help"))

        self.gui = parent
        self.gui.SetMenuBar(self)
        self.gui.Bind(wx.EVT_MENU, self.on_menu)

    def on_menu(self, event) -> None:
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
            self.on_upload(wx.EVT_BUTTON)
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
            
    def on_upload(self, event) -> None:
        """Handles the event when the user clicks the upload button to select the specification file."""
        wildcard = "Text files (*.txt)|*.txt"
        with wx.FileDialog(self.gui, _(u"Open Specification File"), wildcard=wildcard,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            # Canceling the action
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            path = fileDialog.GetPath()  # extracting the file path
            filename = os.path.basename(path)  # extracting the file name

            # Check if file is a text file
            if not path.lower().endswith(".txt"):
                wx.MessageBox(_(u"Please select a valid .txt file"), _(u"Error"), wx.OK | wx.ICON_ERROR)
                return

            # clear display
            self.gui.canvas.clear_display()

            # Processing the file
            progress_dialog = wx.ProgressDialog(_(u"Processing file"),
                                                _(u"Specification file is being processed..."),
                                                maximum=100,
                                                parent=self.gui,
                                                style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE)

            self.gui.terminal.reset_terminal()
            self.gui.reset_gui_display()

            try:
                # Initialise instances of the inner simulator classes
                names = Names()
                devices = Devices(names)
                network = Network(names, devices)
                monitors = Monitors(names, devices, network)

                try:
                    scanner = Scanner(path, names)
                except UnicodeDecodeError:
                    self.gui.terminal.append_text(Color.terminal_error_color,
                                                  f"\nError: file '{path}' is not a unicode text file")

                    self.gui.disable_monitor_buttons()
                    self.gui.disable_simulation_buttons()
                    return
                parser = Parser(names, devices, network, monitors, scanner)

                # Progress bar mock progress
                for i in range(100):
                    wx.MilliSleep(10)
                    progress_dialog.Update(i + 1)

                if self.gui.check_errors(filename, parser):
                    # Instantiate the circuit for the newly uploaded file
                    self.gui.update_parser(parser)

                    # Update the GUI with new canvas, monitors and switches
                    self.gui.monitors_list.update_monitors_list()
                    self.gui.switch.update_switches_display()

            except IOError:
                progress_dialog.Destroy()
                self.gui.terminal.append_text(Color.terminal_error_color, f"File {filename} upload failed.")

            finally:
                progress_dialog.Update(100)
                progress_dialog.Destroy()
