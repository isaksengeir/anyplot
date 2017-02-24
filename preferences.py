# This file is part of AnyPlot

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

from Tkinter import Toplevel, Frame, FALSE, GROOVE, Scrollbar, HORIZONTAL, Listbox, SINGLE, END, Button
import tkFont
import numpy as np
import matplotlib
from matplotlib import font_manager

class Preferences(Toplevel):
    def __init__(self, app, root):         #Receives app and root from Qgui-class.
        """
        :param app:
        :param root:
        """
        Toplevel.__init__(self, root)
        self.app = app
        self.root = root

        self.window()

        self.settings = self.root.settings
        #self.update_prms = dict()

        #for key in self.update_prms.keys():
        #    l1, l2 = key.split('.')
        #    if l1 not in self.settings:
        #        self.settings[l1] = dict()
        #    self.settings[l1][l2] = self.update_prms[key]

        fonts = ['sans-serif', 'serif']
        for font in sorted([f.name for f in matplotlib.font_manager.fontManager.ttflist]):
            if not font.startswith('.'):
                if font not in fonts:
                    fonts.append(str(font))
        fonts = sorted(fonts, key=str.lower)

        float_format= "%.1f"
        self.options = {'font': {'family': fonts,
                                'style': ['normal', 'italic', 'oblique'],
                                'variant': ['normal', 'small-caps'],
                                'weight': ['ultralight', 'light', 'normal', 'regular', 'book', 'medium', 'roman',
                                        'semibold', 'demibold', 'demi', 'bold', 'heavy', 'extra bold', 'black'],
                                'size': np.arange(1, 51, 1)},
                        'nbagg': {'transparent': ['True', 'False']},
                        'axes': {'labelsize': np.arange(1, 51, 1),
                                 'linewidth': np.arange(0, 25.5, 0.5),
                                 'titlesize': np.arange(1, 51, 1),
                                 'labelpad': np.arange(0, 25.5, 0.5),
                                 'axisbelow': ['False', 'True']},
                        'legend': {'fontsize': np.arange(1, 51, 1),
                                   'fancybox': ['True', 'False'],
                                   'numpoints': np.arange(0, 10, 1),
                                   'markerscale': [float_format % i for i in np.arange(0, 1, 0.1)],
                                   'borderpad': [float_format % i for i in np.arange(0, 10, 0.1)],
                                   'shadow': ['True', 'False'],
                                   'framealpha': [float_format % i for i in np.arange(0, 1, 0.1)],
                                   'frameon': ['True', 'False'],
                                   'isaxes': ['True', 'False']},
                        'figure': {'titlesize': np.arange(0, 51, 1),
                                   'dpi': np.arange(10, 510, 10)},
                        'lines': {'markeredgewidth': [float_format % i for i in np.arange(0, 10.1, 0.1)],
                                  'dash_joinstyle': ['miter', 'round', 'bevel'],
                                  'dash_capstyle': ['butt', 'round', 'projecting'],
                                  'solid_joinstyle': ['miter','round','bevel'],
                                  'solid_capstyle': ['butt', 'round', 'projecting'],
                                  'antialiased': ['True', 'False']},
                        'markers': {'fillstyle': ['full', 'left', 'right', 'bottom', 'top', 'none']}
                        }

        self.fill_list()

    def fill_list(self):
        for parent in sorted(self.settings.keys()):
            self.rcparams.insert(END, parent)

    def list1_event(self, *args):
        sel1 = self.rcparams.get(self.rcparams.curselection()[0])

        self.rcparams2.delete(0, END)
        self.rcparams3.delete(0, END)

        for option in sorted(self.options[sel1].keys()):
            self.rcparams2.insert(END, option)

    def list2_event(self, *args):
        sel1 = self.rcparams.get(self.rcparams.curselection()[0])
        sel2 = self.rcparams2.get(self.rcparams2.curselection()[0])
        current_sel = str(self.settings[sel1][sel2])

        self.rcparams3.delete(0, END)

        ind = 0
        i = 0
        for option in self.options[sel1][sel2]:
            self.rcparams3.insert(END, option)
            if str(option) == current_sel:
                ind = i
            i += 1

        self.rcparams3.selection_set(ind)
        self.rcparams3.yview_scroll(ind, 'units')

    def list3_event(self, *args):
        sel1 = self.rcparams.get(self.rcparams.curselection()[0])
        sel2 = self.rcparams2.get(self.rcparams2.curselection()[0])
        current_sel = self.rcparams3.get(self.rcparams3.curselection()[0])

        if str(current_sel)[0].isdigit():
            if str(current_sel).isdigit():
                current_sel = int(current_sel)
            else:
                current_sel = float(current_sel)

        self.settings[sel1][sel2] = current_sel

        if current_sel == 'True':
            current_sel = True
        if current_sel == 'False':
            current_sel = False
        #self.update_prms['%s.%s' % (sel1, sel2)] = current_sel

        self.root.update_settings()
        print 'AnyPlot preference changed: %s.%s: %s' % (sel1, sel2, str(current_sel))

    def restore_settings(self):
        self.root.default_settings()
        self.root.update_settings()

        self.rcparams2.delete(0, END)
        self.rcparams3.delete(0, END)

        self.settings = self.root.settings


    def window(self):
        self.geometry('550x300+100+100')
        self.resizable(width=FALSE, height=FALSE)

        self.title('AnyPlot preferences')

        frame=Frame(self)
        frame.grid(row=0, column=0, padx=(10,10), pady=(10,10))

        #### LEVEL 1 LIST ####
        vbar = Scrollbar(frame)
        vbar.grid(row = 1, column = 2, sticky = 'nsw', padx=(0,0), pady=(0,0))
        hbar = Scrollbar(frame, orient=HORIZONTAL)
        #hbar.grid(row=2, column=1, sticky='we', padx=(0, 0))

        self.rcparams = Listbox(frame, width=20, height=15, yscrollcommand=vbar.set, xscrollcommand=hbar.set,
                                 highlightthickness=0, relief=GROOVE, selectmode=SINGLE,
                                exportselection=False)
        vbar.config(command=self.rcparams.yview)
        hbar.config(command=self.rcparams.xview)
        self.rcparams.grid(row=1,column=1)
        self.rcparams.config(font=tkFont.Font(family="Courier", size=12))
        self.rcparams.bind('<<ListboxSelect>>', self.list1_event)

        #### LEVEL 2 LIST ####
        vbar2 = Scrollbar(frame)
        vbar2.grid(row = 1, column = 4, sticky = 'nsw', padx=(0,0), pady=(0,0))

        self.rcparams2 = Listbox(frame, width=20, height=15, yscrollcommand=vbar2.set,
                                 highlightthickness=0, relief=GROOVE, selectmode=SINGLE,
                                exportselection=False)
        vbar.config(command=self.rcparams2.yview)
        self.rcparams2.grid(row=1,column=3)
        self.rcparams2.config(font=tkFont.Font(family="Courier", size=12))
        self.rcparams2.bind('<<ListboxSelect>>', self.list2_event)

        #### LEVEL 3 LIST ####
        vbar3 = Scrollbar(frame)
        vbar3.grid(row = 1, column = 6, sticky = 'nsw', padx=(0,0), pady=(0,0))

        self.rcparams3 = Listbox(frame, yscrollcommand=vbar3.set, width=28, height=15,
                                 highlightthickness=0, relief=GROOVE, selectmode=SINGLE,
                                exportselection=False)
        vbar3.config(command=self.rcparams3.yview)

        self.rcparams3.grid(row=1,column=5)
        self.rcparams3.config(font=tkFont.Font(family="Courier", size=12))
        self.rcparams3.bind('<<ListboxSelect>>', self.list3_event)

        restore = Button(frame, text='Restore default settings', command=self.restore_settings)
        restore.grid(row=2, column=0, columnspan=10)

        






