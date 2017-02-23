#!/usr/bin/env python2.7

__author__ = "Geir Villy Isaksen"
__copyright__ = "Copyright (C) 2015 Geir Villy Isaksen"
__license__ = "GPL v3"
__version__ = "0.0.3"
__maintainer__ = "Geir Villy Isaksen"
__email__ = "geir.isaksen@uit.no"
__status__ = "Production"

# Copyright 2015 Geir Villy Isaksen, all rights reserved


# AnyPlot source file is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# AnyPlot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with AnyPlot.  If not, see <http://www.gnu.org/licenses/>.

from Tkinter import Tk
from mainwindow import MainWindow
from preferences import Preferences
import tkMessageBox

class AnyPlot(object):
    """
    blablabla
    """

    def __init__(self, root):
        self.root = root

        self.main_window = MainWindow(self, self.root)

    def errorBox(self, tit ='Error', msg=''):
        if tit == 'Error':
            tkMessageBox.showerror(tit, msg)
        elif tit == 'Info':
            tkMessageBox.showinfo(tit, msg)
        else:
            tkMessageBox.showwarning(tit, msg)

    def open_preferences(self):
        self.preferences = Preferences(self, self.main_window)






if __name__ == '__main__':
    root = Tk()
    app = AnyPlot(root)
    root.mainloop()
