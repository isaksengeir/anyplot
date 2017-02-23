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


from Tkinter import Entry, Spinbox, Button, Frame, Scrollbar, Label, Menu, DISABLED, NORMAL, GROOVE, END, TOP, PhotoImage,\
    HORIZONTAL, NONE, PhotoImage, Canvas, BOTH, NW, Listbox, EXTENDED, FALSE, OptionMenu, StringVar, _setit, BOTTOM
from tkFileDialog import askdirectory
from tkSimpleDialog import askstring
import os
import tkFont
from tkFileDialog import askopenfilename, asksaveasfilename
from tkColorChooser import askcolor
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata
from matplotlib import cm
from math import ceil
import cPickle as pickle
import copy


class MainWindow(Frame):
    """
    Creates the main window.
    """

    def __init__(self, app, root):
        Frame.__init__(self, root)
        self.root = root
        self.app = app



        #path to AnyPlot code
        self.anyplot_path = os.path.dirname(os.path.abspath(__file__))

        #Get plot layout settings:

        self.titles = dict()
        self.titles_order = dict()

        self.selected_x = StringVar()
        self.selected_y = StringVar()
        self.selected_z = StringVar()

        self.plot_3d = False
        self.plot_grid = False

        self.selected_linetype = StringVar()
        self.selected_markertype = StringVar()
        self.selected_bartype = StringVar()
        self.selected_legend = StringVar()
        self.linewidth = StringVar()
        self.markersize = StringVar()
        self.barsize = StringVar()

        self.make_grid()
        self.menubar()

        self.selected_x.set('NA')
        self.selected_y.set('NA')
        self.selected_z.set('NA')

        self.selected_x.trace('w', lambda x,y,z: self.set_xyz('x', self.selected_x.get()))
        self.selected_y.trace('w', lambda x,y,z: self.set_xyz('y', self.selected_y.get()))
        self.selected_z.trace('w', lambda x,y,z: self.set_xyz('z', self.selected_z.get()))

        self.selected_linetype.set('None')
        self.selected_markertype.set('o')
        self.selected_bartype.set('None')
        self.selected_legend.set('best')
        self.linewidth.set('2')
        self.markersize.set('7')
        self.barsize.set('0.50')

        self.selected_linetype.trace('w', self.set_linetype)
        self.selected_markertype.trace('w', self.set_markertype)
        self.linewidth.trace('w', self.set_linewidth)
        self.markersize.trace('w', self.set_markersize)
        self.selected_bartype.trace('w', self.set_bartype)
        self.barsize.trace('w', self.set_barsize)

        self.load_preferences()
        self.update_settings()

        #Automatically save AnyPlot preferences when window is closed
        root.protocol("WM_DELETE_WINDOW", self.save_preferences)

    def update_settings(self, *args):
        # matplotlib.rc global settings
        rcparams = dict()

        trans_int = {True: 1, False: 0, 'True': 1, 'False': 0}

        for l1 in self.settings.keys():
            for l2 in self.settings[l1].keys():
                setting = self.settings[l1][l2]

                #Check if setting is a boolen and convert to int type
                if isinstance(setting, bool):
                    setting = trans_int[setting]
                if setting == 'False' or setting == 'True':
                    setting = trans_int[setting]

                rcparams['%s.%s' % (l1, l2)] = setting

        matplotlib.rcParams.update(rcparams)

        try:
            self.fig.canvas.draw()
        except:
            pass
        else:
            print 'An error ococured in update settings'

    def save_preferences(self):
        name = self.anyplot_path + '/.anyplot_preferences'
        pickle.dump(self.settings, open('%s' % name, 'wb'))
        print 'AnyPlot preferences saved.'
        self.root.destroy()

    def load_preferences(self):
        try:
            self.settings = pickle.load(open(self.anyplot_path+'/.anyplot_preferences', 'rb'))
            print 'AnyPlot preferences loaded successfully!'
        except:
            print 'Using default AnyPlot preferences.'
            self.default_settings()


    def default_settings(self):
        #antialised True/False has to be 1/0
        self.settings = {'font': {
                                'family': 'sans-serif',
                                'style': 'normal',
                                'variant': 'normal',
                                'weight': 'medium',
                                'size': 12},
                         'nbagg': {'transparent': 'True'},
                         'axes': {'labelsize': 12,
                                  'linewidth': 2.0,
                                  'titlesize': 12,
                                  'labelpad': 5.0,
                                  'axisbelow': 'False'},
                         'legend': {'fontsize': 12,
                                    'fancybox': 'True',
                                    'numpoints': 1,
                                    'markerscale': 1.0,
                                    'borderpad': 0.5,
                                    'shadow': 'True',
                                    'framealpha': 0,
                                    'frameon': 'True',
                                    'isaxes': 'True'},
                         'figure': {'titlesize': 'None',
                                    'dpi': 100},
                         'lines': {'markeredgewidth': 0.5,
                                   'dash_jointstyle': 'miter',
                                   'dash_capstyle': 'butt',
                                   'solid_jointstyle': 'miter',
                                   'solid_capstyle': 'projecting',
                                   'antialiased': 1},
                         'markers': {'fillstyle': 'full'}

                         }
        print 'Default AnyPlot settings loaded'

    def set_bartype(self, *args):
        selections = map(int, self.titles_listbox.curselection())
        if len(selections) < 1:
            return
        for i in selections:
            title = self.titles_listbox.get(i)
            self.titles[title]['bartype'] = self.selected_bartype.get()

    def set_barsize(self, *args):
        selections = map(int, self.titles_listbox.curselection())
        if len(selections) < 1:
            return
        for i in selections:
            title = self.titles_listbox.get(i)
            try:
                self.titles[title]['barsize'] = float(self.barsize.get())
            except:
                continue

    def fit_linear(self):
        selections = map(int, self.titles_listbox.curselection())
        if len(selections) < 1:
            return
        for i in selections:
            title = self.titles_listbox.get(i)
            x,y = self.get_xyz(title)[0:2]

            try:
                x = map(float, x)
            except:
                print 'Could not convert X-list into floats!'
                return

            if len(x) < 1 or len(y) < 1:
                print 'x and y values not complete...'
            a, b, r2 = self.lin_reg(x,y)

            print 'LINEAR FIT: f(x) = %f*x %+f' % (a,b)
            print 'COD: %f' % r2

            fit = '%s_fit1' % title
            self.titles[fit] = dict()
            self.titles_order[max(self.titles_order.keys()) + 1] = fit

            #Generate model data
            self.titles[fit]['data'] = dict()
            s_mod = 0

            i = 1
            for j in range(len(x)):
                val_x = x[j]
                val_y = y[j]
                mod_y = (a * val_x) + b
                s_mod += (val_y - mod_y)**2

                self.titles[fit]['data'][i] = '%.6f  %.6f' % (val_x, mod_y)
                i += 1
            #standard error squared of the model (remove 2 degrees of freedom <-- linear regression parameters)
            s_mod /= (float(len(y)) - 2.0)
            s_mod = np.sqrt(s_mod)

            for i in self.titles[fit]['data'].keys():
                self.titles[fit]['data'][i] += '  %.6f' % s_mod

            self.titles[fit]['x'] = 1
            self.titles[fit]['y'] = 2
            self.titles[fit]['z'] = 'NA'
            self.titles[fit]['columns'] = 3
            self.titles[fit]['linetype'] = '-'
            self.titles[fit]['linewidth'] = '2'
            self.titles[fit]['markertype'] = 'None'
            self.titles[fit]['markersize'] = '7'
            self.titles[fit]['color'] = 'black'
            self.titles[fit]['bartype'] = 'None'
            self.titles[fit]['barsize'] = 0.1

        self.update_tables()

    def lin_reg(self, x, y):
        _y = np.array(y)
        _x = np.array(x)
        _A = np.vstack([_x,np.ones(len(_x))]).T        #Vector matrix for linear algebra least sq.

        model, resid = np.linalg.lstsq(_A, _y)[:2]     #generate model and residuals
        r2 = 1 - resid / (_y.size * _y.var())         # R^2

        #Remove this:
        print model
        print r2

        a = model[0]
        b = model[1]
        r2 = r2[0]

        return a, b, r2

    def set_linewidth(self, *args):
        selections = map(int, self.titles_listbox.curselection())
        if len(selections) < 1:
            return
        try:
            lw = float(self.linewidth.get())
        except:
            return

        for i in selections:
            title = self.titles_listbox.get(i)
            self.titles[title]['linewidth'] = lw

    def set_markersize(self, *args):
        selections = map(int, self.titles_listbox.curselection())
        if len(selections) < 1:
            return
        try:
            ms = float(self.markersize.get())
        except:
            return

        for i in selections:
            title = self.titles_listbox.get(i)
            self.titles[title]['markersize'] = ms

    def set_xyz(self, xyz, var, *args):
        selections = map(int, self.titles_listbox.curselection())

        if len(selections) < 1:
            return

        for selected in selections:
            title = self.titles_listbox.get(selected)
            self.titles[title][xyz] = var

    def set_linetype(self, *args):
        lt = self.selected_linetype.get()
        selections = self.titles_listbox.curselection()
        if len(selections) < 1:
            return
        for i in selections:
            title = self.titles_listbox.get(i)
            self.titles[title]['linetype'] = lt

    def set_markertype(self, *args):
        marker = self.selected_markertype.get()
        selections = self.titles_listbox.curselection()
        if len(selections) < 1:
            return
        for i in selections:
            title = self.titles_listbox.get(i)
            self.titles[title]['markertype'] = marker

    def add_title(self):
        """
        add a new project title (main name for plot)
        """

        title = askstring('Add title', 'Line title:', parent=self)
        if not title:
            return
        if title in self.titles_listbox.get(0, END):
            self.app.errorBox('Warning', 'Title already exist in Titles.')
            return

        self.titles_listbox.insert(END, title)

        self.titles[title] = dict()
        nr = 1
        if len(self.titles_order.keys()) > 0:
            nr = max(self.titles_order.keys()) + 1
        self.titles_order[nr] = title

        for i in ['x','y','z']:
                self.titles[title][i] = 'NA'
        self.get_settings(title)

        #Highlight latest title in listbox
        self.titles_listbox.select_clear(0, END)
        titles = self.titles_listbox.get(0, END)
        for ind_ in range(len(titles)):
            if titles[ind_] == title:
                self.titles_listbox.selection_set(ind_)
        self.list_titles_event()

    def get_settings(self, title):
        self.titles[title]['linetype'] = self.selected_linetype.get()
        self.titles[title]['linewidth'] =  float(self.linewidth.get())
        self.titles[title]['markertype'] = self.selected_markertype.get()
        self.titles[title]['markersize'] = float(self.markersize.get())
        self.titles[title]['bartype'] = self.selected_bartype.get()
        self.titles[title]['barsize'] = float(self.barsize.get())

    def shift_up(self):
        selection = map(int, self.titles_listbox.curselection())
        if len(selection) != 1:
            print 'select one item to move up or down!'
            return
        ind = selection[0]
        if ind == 0:
            return

        title = self.titles_listbox.get(ind)

        for nr in sorted(self.titles_order.keys()):
            if self.titles_order[nr] == title:
                new_nr = nr - 1
                self.titles_order[nr] = self.titles_order.pop(new_nr)
                self.titles_order[new_nr] = title
                self.update_tables()
                self.titles_listbox.selection_set(new_nr-1)
                break

    def shift_down(self):
        selection = map(int, self.titles_listbox.curselection())
        if len(selection) != 1:
            print 'select one item to move up or down!'
            return
        ind = selection[0]
        if ind == len(self.titles) - 1:
            return

        title = self.titles_listbox.get(ind)

        for nr in sorted(self.titles_order.keys()):
            if self.titles_order[nr] == title:
                new_nr = nr + 1
                self.titles_order[nr] = self.titles_order.pop(new_nr)
                self.titles_order[new_nr] = title
                self.update_tables()
                self.titles_listbox.selection_set(new_nr-1)
                break


    def del_title(self):
        selections = map(int, self.titles_listbox.curselection())

        for selected in selections:
            title = self.titles_listbox.get(selected)
            del self.titles[title]


            for nr in sorted(self.titles_order.keys()):
                title_ = self.titles_order[nr]
                if title_ == title:
                    print 'I deleted correctly nr %d' % nr
                    del self.titles_order[nr]

        #renumber order-list:
        new_nr = 1
        for nr in sorted(self.titles_order.keys()):
            self.titles_order[new_nr] = self.titles_order.pop(nr)
            new_nr += 1

        self.update_tables()

    def edit_title(self):
        selections = map(int, self.titles_listbox.curselection())
        for selected in selections:
            old_title = self.titles_listbox.get(selected)

            new_title = askstring('Edit title', 'Line title', parent=self, initialvalue=old_title)

            if not new_title:
                return

            if new_title == old_title:
                return

            if new_title in self.titles.keys():
                self.app.errorBox('Warning', 'Title already exist.')
                return

            self.titles[new_title] = self.titles.pop(old_title)

            for nr in self.titles_order.keys():
                if self.titles_order[nr] == old_title:
                    self.titles_order[nr] = new_title

            self.update_tables()

    def add_data(self):
        selections = map(int, self.titles_listbox.curselection())
        if len(selections) == 0:
            title = 'dataset_1'
            self.titles[title] = dict()

            nr = 1
            if len(self.titles_order.keys()) > 0:
                nr = max(self.titles_order.keys()) + 1
            self.titles_order[nr] = title

            self.get_settings(title)
            self.titles_listbox.insert(END, title)
            selections.append(len(self.titles_listbox.get(0, END)) - 1)

        filename = askopenfilename(parent=self)
        if not filename:
                return

        for selected in selections:
            title = self.titles_listbox.get(selected)

            i = 1
            col = 0
            self.titles[title]['columns'] = col
            if not 'data' in self.titles[title].keys():
                self.titles[title]['data'] = dict()
                for xyz in ['x', 'y', 'z']:
                    self.titles[title][xyz] = 'NA'
            else:
                try:
                    i = 1 + max(self.titles[title]['data'].keys())
                except:
                    i = 1

            with open(filename, 'r') as data:
                for line in data:
                    if line.strip():
                        if len(line.split()) > col:
                            col = len(line.split())
                        self.titles[title]['data'][i] = line
                        #self.data_listbox.insert(END, line)
                        i += 1

            self.titles[title]['columns'] = col
        self.list_titles_event()

    def del_data(self):
        selections = map(int, self.data_listbox.curselection())
        if len(selections) == 0:
            return
        title = self.titles_listbox.get(int(self.titles_listbox.curselection()[0]))
        for i in reversed(selections):
            if i != 0:
                self.data_listbox.delete(i)

        self.titles[title]['data'].clear()

        i = 1
        col = 0
        for line in self.data_listbox.get(1, END):
            self.titles[title]['data'][i] = line
            if len(line.split()) > col:
                col = len(line.split())
            i += 1
        self.titles[title]['columns'] = col
        self.list_titles_event()

    def edit_data(self):
        try:
            title = self.titles_listbox.get(int(self.titles_listbox.curselection()[0]))
        except:
            return
        selections = map(int, self.data_listbox.curselection())
        for selected in selections:
            if selected == 0:
                print 'Can not edit header.'
                return

            old_data = self.data_listbox.get(selected)

            new_data = askstring('Edit data', 'Data line', parent=self, initialvalue=old_data)

            if not new_data:
                return

            self.titles[title]['data'][selected] = new_data

        self.list_titles_event()

    def button_style(self, button):
        c1 = "#%02x%02x%02x" % (252, 183, 20)
        button.config(highlightbackground='gray', highlightcolor=c1, activebackground=c1, activeforeground=c1)

    def update_tables(self):
        self.titles_listbox.delete(0, END)
        self.data_listbox.delete(0, END)

        for nr in sorted(self.titles_order.keys()):
            title = self.titles_order[nr]
            self.titles_listbox.insert(END, title)
            if 'color' in self.titles[title].keys():
                color = self.titles[title]['color']
                self.titles_listbox.itemconfig(nr - 1, fg=color)

    def list_titles_event(self, *args):
        selections = map(int, self.titles_listbox.curselection())
        if len(selections) == 0:
            return

        self.data_listbox.delete(0, END)
        if len(selections) > 1:
            return

        for selected in selections:
            title = self.titles_listbox.get(selected)
            if not 'data' in self.titles[title].keys():
                self.update_xyz()
                return

            head = ''

            for col in range(1,self.titles[title]['columns'] + 1):
                col = '#%d' % col
                head += '%12s' % col

            self.data_listbox.insert(END, head)

            for i in sorted(self.titles[title]['data'].keys()):
                line = self.titles[title]['data'][i].split()
                newline = ''
                for j in line:
                    newline += '%12s' % j

                self.data_listbox.insert(END, newline)

        self.update_xyz()
        #self.update_plot_settings()

    def update_xyz(self):
        xyz = {self.x_dropdown: [self.selected_x, 'x'], self.y_dropdown: [self.selected_y, 'y'],
               self.z_dropdown: [self.selected_z, 'z']}

        max_col = 0
        options = ['NA']
        selections = map(int, self.titles_listbox.curselection())
        for selected in selections:
            title = self.titles_listbox.get(selected)
            if 'columns' in self.titles[title].keys():
                    col = self.titles[title]['columns']
                    if col > max_col:
                        max_col = col

        if max_col > 0:
            for i in range(1, max_col + 1):
                options.append(str(i))

        for menu in xyz.keys():
            var = xyz[menu][0]
            xyz_sel = xyz[menu][1]
            var.set(self.titles[title][xyz_sel])

            menu['menu'].delete(0, END)
            for choice in options:
                menu['menu'].add_command(label=choice, command=_setit(var, choice))

    def update_plot_settings(self):
        settings = {self.linetype_menu: [self.selected_linetype, 'linetype'],
                    self.markertype_menu: [self.selected_markertype, 'markertype'],
                    self.linewidth_spinbox: [self.linewidth, 'linewidth'],
                    self.markersize_spinbox: [self.markersize, 'markersize'],
                    self.barsize_spinbox: [self.barsize, 'barsize'],
                    self.bartype_menu: [self.selected_bartype, 'bartype']}

        title = self.titles_listbox.get(self.titles_listbox.curselection()[0])
        for setting in settings.keys():
            var = settings[setting][0]
            sel_var = settings[setting][1]
            var.set(self.titles[title][sel_var])

    def plotit(self):

        selections = map(int, self.titles_listbox.curselection())
        if len(selections) < 1:
            return

        #Bar plot requires special handling, collect titles:
        titles = dict()

        #General settings
        plot_title = self.z_label_entry.get()
        x_label = self.x_label_entry.get()
        y_label = self.y_label_entry.get()

        self.fig = plt.figure()
        self.fig.set_facecolor('white')


        if self.plot_3d:
            self.ax = self.fig.add_subplot(111, projection='3d')
            self.ax.set_zlabel(plot_title)

        else:
            self.ax = self.fig.add_subplot(111)
            self.ax.set_title(plot_title, fontweight='bold')

        if self.plot_grid:
            self.ax.grid(True)
        else:
            self.ax.grid(False)

        self.fig.subplots_adjust(top=0.85)

        self.ax.set_ylabel(r'%s' % y_label)
        self.ax.set_xlabel(x_label)


        #Send to correct plotter
        for selected in selections:
            title = self.titles_listbox.get(selected)

            #Line and marker settings for title:
            if 'color' not in self.titles[title].keys():
                sel_col = self.ax._get_lines.color_cycle.next()
            else:
                sel_col = self.titles[title]['color']

            sel_lt = self.titles[title]['linetype']
            sel_marker = self.titles[title]['markertype']
            linewidth = self.titles[title]['linewidth']
            markersize = self.titles[title]['markersize']
            bartype = self.titles[title]['bartype']

            plot_what = [self.titles[title]['x'], self.titles[title]['y'], self.titles[title]['z']]


            if plot_what == ['NA', 'NA', 'NA']:
                print 'SELECT COLUMN(S) TO PLOT!'
                return
            elif 'NA' not in plot_what:
                if self.plot_3d:
                    self.make_3d_plot(title)
                else:
                    if (sel_lt != 'None') or (sel_marker != 'None'):
                        self.plot_xy_err(title, sel_col, sel_lt, linewidth, sel_marker, markersize)
                    if bartype != 'None':
                        titles[title] = 'xy_err'
            elif plot_what.count('NA') == 2:
                if plot_what[0] != 'NA':
                    if (sel_lt != 'None') or (sel_marker != 'None'):
                        self.plot_x(title, sel_col, sel_lt, linewidth, sel_marker, markersize)
                    if bartype != 'None':
                        titles[title] = 'x'
                elif plot_what[1] != 'NA':
                    if (sel_lt != 'None') or (sel_marker != 'None'):
                        self.plot_y(title, sel_col, sel_lt, linewidth, sel_marker, markersize)
                    if bartype != 'None':
                        titles[title] = 'y'
                else:
                    print 'Can not plot Z-value alone. Specify X or Y!'
            elif plot_what.count('NA') == 1:
                if plot_what[2] != 'NA':
                    print 'Can not plot against Z. Select X and Y!'
                else:
                    if (sel_lt != 'None') or (sel_marker != 'None'):
                        self.plot_xy(title, sel_col, sel_lt, linewidth, sel_marker, markersize)
                    if bartype != 'None':
                        titles[title] = 'xy'

        if len(titles.keys()) > 0:
            self.plot_bars(titles)

        plt.tight_layout()

        if not self.plot_3d:
            loc = self.selected_legend.get()

            if loc != 'None':
                if loc == 'outside':
                    box = self.ax.get_position()
                    self.ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
                    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
                    self.fig.subplots_adjust(right=0.75)
                else:
                    plt.legend(loc=loc)


        #self.ax.axhline(y=0, linestyle='-', color='k')

        plt.show()

    def get_xyz(self, title):
        """
        returns lists X, Y and Z for title
        """
        x = list()
        y = list()
        z = list()

        try:
            xi = int(self.titles[title]['x']) - 1
        except:
            xi = 0

        try:
            yi = int(self.titles[title]['y']) - 1
        except:
            yi = 0

        try:
            zi = int(self.titles[title]['z']) - 1
        except:
            zi = 0

        for i in range(1, len(self.titles[title]['data'])+1):
            line = self.titles[title]['data'][i]
            try:
                y.append(float(line.split()[yi]))
            except:
                y.append(line.split()[yi])
            try:
                z.append(float(line.split()[zi]))
            except:
                z.append(line.split()[zi])

            #X is a bit special, because it can contain text (x-tics)
            try:
                x.append(line.split()[xi])
            except:
                continue

        return np.array(x), np.array(y), np.array(z)

    def takespread(self, sequence, num):
        length = float(len(sequence))
        for i in range(num):
            yield sequence[int(ceil(i * length / num))]

    def plot_bars(self, titles):

        #Shift ticks i * width
        i = 0

        N = len(titles)
        dx = 9999999999999.

        xlabels = list()
        xticks = False

        align='center'
        if N > 1:
            align='edge'

        for title in titles.keys():
            plot = titles[title]
            width = self.titles[title]['barsize']
            bartype = self.titles[title]['bartype']
            if 'color' not in self.titles[title].keys():
                sel_col = self.ax._get_lines.color_cycle.next()
            else:
                sel_col = self.titles[title]['color']

            if plot == 'y':
                y = self.get_xyz(title)[1]
                x_ax = np.arange(len(y))
            elif plot == 'x':
                x_ax = self.get_xyz(title)[0]
                y = np.arange(len(x))
            elif plot == 'xy':
                x_ax, y = self.get_xyz(title)[0:2]
            elif plot == 'xy_err':
                x_ax, y, z = self.get_xyz(title)

            for t in x_ax:
                if t not in xlabels:
                    xlabels.append(t)

            if xticks:
                x = np.arange(len(y))
            else:
                try:
                    x = map(float, x_ax)
                except:
                    xticks = True
                    x = np.arange(len(y))


            if bartype == 'clean':
                bartype = ''

            #find minimum delta(x), dx and make barwidth:
            for j in range(1, len(x)):
                if abs(x[j] - x[j-1]) < dx:
                    dx = abs(x[j] - x[j-1])
                    w = dx / float(N)

            width *= w

            #create new x values
            x = [k + (w * i) for k in x]


            if plot == 'xy_err':
                #lw = self.titles[title]['linewidth']
                self.ax.bar(x, y, width=width, align=align, color=sel_col, yerr=z, hatch=bartype,
                            label=r'%s' % title)
            else:
                self.ax.bar(x, y, width=width, align=align, color=sel_col, hatch=bartype, label=r'%s' % title)
            i += 1


        if xticks:
            ind = np.arange(len(xlabels))
        else:
            ind = map(float, xlabels)

        #Create a dictionary to keep track of x-labels
        x_dict = dict()

        for i in range(len(ind)):
            x_dict[ind[i]] = xlabels[i]


        if xticks or N > 1:
            x_ticks_generator = self.takespread(ind, 6)
            ind = list()
            xlabels = list()
            for i in x_ticks_generator:
                ind.append(i)
                xlabels.append(x_dict[i])

            ind.append(max(x_dict.keys()))
            xlabels.append(x_dict[max(x_dict.keys())])
            ind = [l + (dx/2.) for l in ind]
            self.ax.set_xticks(ind)
            self.ax.set_xticklabels(xlabels)


    def make_3d_plot(self, title):


        x, y, z = self.get_xyz(title)

        try:
            x = map(float, x)
        except:
            return

        X = np.array(x)
        Y = np.array(y)
        Z = np.array(z)

        Z = griddata((X, Y), Z, (X[None, :], Y[:, None]), method='nearest')

        X,Y = np.meshgrid(X, Y)



        #self.ax.plot_wireframe(X, Y, Z)
        self.ax.plot_surface(X, Y, Z,  rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0, antialiased=False)


    def plot_xy_err(self, title, sel_col, sel_lt, lw, sel_marker, ms):
        if sel_marker == 'None':
            sel_marker = 'o'
        x_ticks = False

        x, y, y_err = self.get_xyz(title)

        #If x array is not values, use it as x-ticks labels:
        try:
            x = map(float, x)
        except:
            x_ticks = True

        if not x_ticks:
            self.ax.errorbar(x, y, yerr=y_err, ls=sel_lt, lw=lw, fmt=sel_marker, ms=ms, color=sel_col, label=r'%s' % title)
        else:
            ind = np.arange(len(y))
            self.ax.errorbar(ind, y, yerr=y_err, ls=sel_lt, lw=lw, fmt=sel_marker, ms=ms, color=sel_col, label=r'%s' % title)
            plt.xticks(ind, x)


    def plot_xy(self, title, sel_col, sel_lt, lw, sel_marker, ms):
        x_ticks = False
        x, y = self.get_xyz(title)[0:2]

        print x
        print y
        print (len(x), len(y))

        #If x list is not values, use it as x-ticks labels:
        try:
            x = map(float, x)
        except:
            x_ticks = True

        if not x_ticks:
            self.ax.plot(x, y, ls=sel_lt, lw=lw, marker=sel_marker, ms=ms, color=sel_col, label=r'%s' % title)
        else:
            ind = np.arange(len(y))
            self.ax.plot(ind, y, ls=sel_lt, lw=lw, marker=sel_marker, ms=ms, color=sel_col, label=r'%s' % title)
            plt.xticks(ind, x)

    def plot_y(self, title, sel_col, sel_lt, lw, sel_marker, ms):
        y = self.get_xyz(title)[1]
        ind = np.arange(len(y))
        self.ax.plot(ind, y, ls=sel_lt, lw=lw, marker=sel_marker, ms=ms, color=sel_col, label=r'%s' % title)

    def plot_x(self, title, sel_col, sel_lt, lw, sel_marker, ms):
        x = self.get_xyz(title)[0]
        ind = np.arange(len(x))
        self.ax.plot(x, ind, ls=sel_lt, lw=lw, marker=sel_marker, ms=ms, color=sel_col, label=r'%s' % title)


    def get_color(self):
        color = askcolor()
        if not color:
            return
        self.modify_color(color[1])

    def modify_color(self, color):
        selections = self.titles_listbox.curselection()
        for i in selections:
            self.titles_listbox.itemconfig(i, fg=color)
            title = self.titles_listbox.get(i)
            self.titles[title]['color'] = color

        self.titles_listbox.selection_clear(0, END)

    def toggle_3d(self):
        if not self.plot_3d:
            self.plot_3d = True
            on = PhotoImage(file=self.anyplot_path + '/pics/on.gif')
            on.img = on
            self.on_off_3d.config(image=on)
        else:
            self.plot_3d = False
            off = PhotoImage(file=self.anyplot_path + '/pics/off.gif')
            off.img = off
            self.on_off_3d.config(image=off)

    def toggle_grid(self):
        if not self.plot_grid:
            self.plot_grid = True
            on = PhotoImage(file=self.anyplot_path + '/pics/on.gif')
            on.img = on
            self.on_off_grid.config(image=on)
        else:
            self.plot_grid = False
            off = PhotoImage(file=self.anyplot_path + '/pics/off.gif')
            off.img = off
            self.on_off_grid.config(image=off)

    def save_project(self):
        name = asksaveasfilename(defaultextension='.p')
        if not name:
            return

        titles = copy.deepcopy(self.titles)
        titles_order = copy.deepcopy(self.titles_order)
        xlabel = self.x_label_entry.get()
        ylabel = self.y_label_entry.get()
        zlabel = self.z_label_entry.get()
        plot_3d = self.plot_3d
        legend = self.selected_legend.get()
        grid = self.plot_grid


        save_dict = {'titles': titles,
                     'titles order': titles_order,
                     'x label': xlabel,
                     'y label': ylabel,
                     'z label': zlabel,
                     '3d': plot_3d,
                     'legend': legend,
                     'grid': grid,
                     }


        pickle.dump(save_dict, open('%s' % name, 'wb'))
        print 'Project saved to %s' % name

    def import_project(self):
        name = askopenfilename(defaultextension='.p')
        if not name:
            return
        save_dict = pickle.load(open(name, 'rb'))

        titles = save_dict['titles']
        for title in titles.keys():
            self.titles[title] = titles[title]

        max_nr = 0
        if len(self.titles_order.keys()) > 0:
            max_nr = max(self.titles_order.keys())

        titles_order = save_dict['titles order']
        for nr in sorted(titles_order.keys()):
            title = titles_order[nr]
            self.titles_order[nr + max_nr] = title

        self.x_label_entry.delete(0, END)
        self.x_label_entry.insert(0, save_dict['x label'])

        self.y_label_entry.delete(0, END)
        self.y_label_entry.insert(0, save_dict['y label'])

        self.z_label_entry.delete(0, END)
        self.z_label_entry.insert(0, save_dict['z label'])

        self.plot_3d = save_dict['3d']
        if self.plot_3d:
            self.plot_3d = False
        else:
            self.plot_3d = True
        self.toggle_3d()

        self.plot_grid = save_dict['grid']
        if self.plot_grid:
            self.plot_grid = False
        else:
            self.plot_grid = True
        self.toggle_grid()

        self.selected_legend.set(save_dict['legend'])

        self.update_tables()

    def make_grid(self):
        """
        Make maine frame
        """
        self.root.title('AnyPlot v0.1')

        bg_image=PhotoImage(file=self.anyplot_path + "/pics/fibers.gif")
        w = bg_image.width()
        h = bg_image.height()

        self.root.geometry('%dx%d+100+100' % (w, h))
        self.root.resizable(width=FALSE, height=FALSE)

        bg = Canvas(self.root)
        bg.pack(expand=True, fill=BOTH)
        bg.img = bg_image
        bg.create_image(0, 0, anchor=NW, image=bg_image)

        down_image = PhotoImage(file=self.anyplot_path + '/pics/arrow_down.gif')
        down_image.img = down_image
        up_image = PhotoImage(file=self.anyplot_path + '/pics/arrow_up.gif')
        up_image.img = up_image

        move_up = Button(bg, image=up_image, command=self.shift_up, width=30, height=30)
        self.button_style(move_up)
        move_up.grid(row=2, column=0, sticky='w', padx=(3,0))

        move_down = Button(bg, image=down_image, command=self.shift_down, width=30, height=30)
        self.button_style(move_down)
        move_down.grid(row=3, column=0, sticky='w', padx=(3,0))

        titles_yscroll = Scrollbar(bg)
        titles_yscroll.grid(row = 1, rowspan=10, column = 3, sticky = 'nsw', padx=(0,0), pady=(50,0))
        titles_xscroll = Scrollbar(bg, orient=HORIZONTAL)
        titles_xscroll.grid(row=11, column=0, columnspan=3, sticky='we', padx=(40, 0))

        self.titles_listbox = Listbox(bg, yscrollcommand = titles_yscroll.set,
                                      xscrollcommand=titles_xscroll.set,
                                      width=18, height=15, highlightthickness=0, relief=GROOVE, selectmode=EXTENDED,
                                      exportselection=False)
        titles_yscroll.config(command=self.titles_listbox.yview)
        titles_xscroll.config(command=self.titles_listbox.xview)
        self.titles_listbox.grid(row=1, rowspan=10, column = 0, columnspan=3, sticky='e', padx=(40,0), pady=(50,0))
        self.titles_listbox.config(font=tkFont.Font(family="Courier", size=12))
        self.titles_listbox.bind('<<ListboxSelect>>', self.list_titles_event)


        add_image = PhotoImage(file=self.anyplot_path + '/pics/add.gif')
        add_image.img = add_image
        add_titles = Button(bg, image=add_image, command=self.add_title, width=30, height=30)
        self.button_style(add_titles)
        add_titles.grid(row=1, column=4, pady=(50,0))

        del_image = PhotoImage(file=self.anyplot_path + '/pics/del.gif')
        del_image.img = del_image
        del_titles = Button(bg, image=del_image, command=self.del_title, width=30, height=30)
        self.button_style(del_titles)
        del_titles.grid(row=2, column=4)

        edit_image = PhotoImage(file=self.anyplot_path + '/pics/edit.gif')
        edit_image.img = edit_image
        edit_titles = Button(bg, image=edit_image, command=self.edit_title, width=30, height=30)
        self.button_style(edit_titles)
        edit_titles.grid(row=3, column=4)

        ## DATA LIST ##
        data_yscroll = Scrollbar(bg)
        data_yscroll.grid(row = 1, rowspan=10, column = 8, sticky = 'nsw', padx=(0,0), pady=(50,0))
        data_xscroll = Scrollbar(bg, orient=HORIZONTAL)
        data_xscroll.grid(row=11, column=5, columnspan=3, sticky='we', padx=(14,0))

        self.data_listbox = Listbox(bg, yscrollcommand = data_yscroll.set,
                                      xscrollcommand=data_xscroll.set,
                                      width=50, height=15, highlightthickness=0, relief=GROOVE, selectmode=EXTENDED,
                                      exportselection=False)
        data_yscroll.config(command=self.data_listbox.yview)
        data_xscroll.config(command=self.data_listbox.xview)
        self.data_listbox.config(font=tkFont.Font(family="Courier", size=12))
        self.data_listbox.grid(row=1, rowspan=10, column = 5, columnspan=3, sticky='e', padx=(14,0), pady=(50,0))




        add_image = PhotoImage(file=self.anyplot_path + '/pics/add.gif')
        add_image.img = add_image
        add_titles = Button(bg, image=add_image, command=self.add_data, width=30, height=30)
        self.button_style(add_titles)
        add_titles.grid(row=1, column=9, pady=(50,0))

        del_image = PhotoImage(file=self.anyplot_path + '/pics/del.gif')
        del_image.img = del_image
        del_titles = Button(bg, image=del_image, command=self.del_data, width=30, height=30)
        self.button_style(del_titles)
        del_titles.grid(row=2, column=9)

        edit_image = PhotoImage(file=self.anyplot_path + '/pics/edit.gif')
        edit_image.img = edit_image
        edit_titles = Button(bg, image=edit_image, command=self.edit_data, width=30, height=30)
        self.button_style(edit_titles)
        edit_titles.grid(row=3, column=9)

        grid_image = PhotoImage(file=self.anyplot_path + '/pics/grid.gif')
        grid_image.img = grid_image
        use_grid = Button(bg, image=grid_image, command=self.toggle_grid, width=30, height=30)
        self.button_style(use_grid)
        use_grid.grid(row=4, column=9)

        cube_image = PhotoImage(file=self.anyplot_path + '/pics/3d_cube.gif')
        cube_image.img = cube_image
        plot_3d = Button(bg, image=cube_image, command=self.toggle_3d, width=30, height=30)
        self.button_style(plot_3d)
        plot_3d.grid(row=5, column=9)

        ## DROP DOWN MENUS X Y ERROR ##
        self.x_dropdown = OptionMenu(bg, self.selected_x, 'NA')
        self.x_dropdown.config(highlightbackground='gray', highlightthickness=0, borderwidth=0, bg='gray', width=6)
        self.x_dropdown.grid(row=1, column=10, pady=(50,0), padx=(10,0))

        self.y_dropdown = OptionMenu(bg, self.selected_y, 'NA')
        self.y_dropdown.config(highlightbackground='gray', highlightthickness=0, borderwidth=0, bg='gray', width=6)
        self.y_dropdown.grid(row=2, column=10, pady=(0,0), padx=(10,0))

        self.z_dropdown = OptionMenu(bg, self.selected_z, 'NA')
        self.z_dropdown.config(highlightbackground='gray', highlightthickness=0, borderwidth=0, bg='gray', width=6)
        self.z_dropdown.grid(row=3, column=10, pady=(0,0), padx=(10,0))


        off = PhotoImage(file=self.anyplot_path + '/pics/off.gif')
        off.img = off

        self.on_off_3d = Label(bg, image=off)
        self.on_off_3d.config(highlightthickness=0, borderwidth=0)
        self.on_off_3d.grid(row=5, column=10)

        self.on_off_grid = Label(bg, image=off)
        self.on_off_grid.config(highlightthickness=0, borderwidth=0)
        self.on_off_grid.grid(row=4, column=10)

        ##X, Y and Z labels ##
        self.x_label_entry = Entry(bg, width=15, highlightthickness=0, borderwidth=5, bg='white')
        self.x_label_entry.grid(row=12, column=0, columnspan=5, padx=(10,0), pady=(5,0), sticky='e')
        self.x_label_entry.insert(0, 'X axis label')

        self.y_label_entry = Entry(bg, width=15, highlightthickness=0, borderwidth=5, bg='white')
        self.y_label_entry.grid(row=13, column=0, columnspan=5, padx=(10,0), pady=(5,0), sticky='e')
        self.y_label_entry.insert(0, 'Y axis label')
        
        self.z_label_entry = Entry(bg, width=15, highlightthickness=0, borderwidth=5, bg='white')
        self.z_label_entry.grid(row=14, column=0, columnspan=5, padx=(10,0), pady=(10,0), sticky='e')
        self.z_label_entry.insert(0, 'Z axis / title')

        ## Line and marker settings
        color_image = PhotoImage(file=self.anyplot_path + '/pics/color-wheel.gif')
        color_image.img = color_image
        line_color = Button(bg, image=color_image, width=35, height=35, command=self.get_color)
        self.button_style(line_color)
        line_color.config(highlightbackground='gray', highlightthickness=0, borderwidth=0, bg='gray')
        line_color.grid(row=4, column=4)

        self.linetype_menu = OptionMenu(bg, self.selected_linetype, 'None', '-','--', '-.', ':')
        self.linetype_menu.config(highlightbackground='gray', highlightthickness=0, borderwidth=0, bg='gray', width=8)
        self.linetype_menu.grid(row=12, column=6, pady=(0,0), padx=(0,0))

        self.linewidth_spinbox = Spinbox(bg, width=4, from_=1, to=20, highlightthickness=0, relief=GROOVE,
                                          textvariable=self.linewidth)
        self.linewidth_spinbox.grid(row=12, column=7, padx=(0,0))

        self.markertype_menu = OptionMenu(bg, self.selected_markertype, 'None', 'o', '.', 's', 'x', '+', '*','D','d',
                                          'v', '^', '<', '>', '8','h', 'H', 'p')
        self.markertype_menu.config(highlightbackground='gray', highlightthickness=0, borderwidth=0, bg='gray', width=8)
        self.markertype_menu.grid(row=13, column=6, pady=(0,0), padx=(0,0))

        self.markersize_spinbox = Spinbox(bg, width=4, from_=1, to=20, highlightthickness=0, relief=GROOVE,
                                           textvariable=self.markersize)
        self.markersize_spinbox.grid(row=13, column=7, padx=(0,0))

        self.bartype_menu = OptionMenu(bg, self.selected_bartype, 'None','', '-', '+', 'x', '\\', '*', 'o', 'O',
                                       '.')
        self.bartype_menu.config(highlightbackground='gray', highlightthickness=0, borderwidth=0, bg='gray', width=8)
        self.bartype_menu.grid(row=14, column=6, pady=(0,0), padx=(0,0))

        self.barsize_spinbox = Spinbox(bg, width=4, from_=0, to=1, highlightthickness=0, relief=GROOVE,
                                           textvariable=self.barsize, increment=0.05)
        self.barsize_spinbox.grid(row=14, column=7, padx=(0,0))

        ## LEGEND OPTIONS
        legend_menu = OptionMenu(bg, self.selected_legend, 'None', 'best','upper right', 'upper left', 'lower left',
                                 'lower right', 'right', 'center left' , 'center right', 'lower center' ,'upper center',
                                 'center', 'outside')
        legend_menu.config(highlightbackground='gray', highlightthickness=0, borderwidth=0, bg='gray', width=13)
        legend_menu.grid(row=14, column=8, columnspan=3, sticky='e')


        ## PLOT BUTTON ##
        plot_image = PhotoImage(file=self.anyplot_path + '/pics/power_button.gif')
        plot_image.img = plot_image
        plot = Button(bg, image=plot_image, command=self.plotit, width=50, height=50)
        self.button_style(plot)
        plot.config(highlightbackground='gray', highlightthickness=0, borderwidth=0, bg='gray')
        plot.grid(row=100, column=0, columnspan=20, pady=(20,0), sticky='s')


    def menubar(self):
        """
        Top menubar
        """
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        #File menu definiton
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label = 'Import', command = self.import_project)
        filemenu.add_command(label = 'Export', command = self.save_project)
        filemenu.add_command(label = 'Preferences', command = self.app.open_preferences)
        filemenu.add_separator()
        filemenu.add_command(label = 'Close', command = None)
        menubar.add_cascade(label = 'File', menu = filemenu)

        fitmenu = Menu(menubar, tearoff=0)
        fitmenu.add_command(label = 'Linear', command = self.fit_linear)
        menubar.add_cascade(label = 'Fit', menu = fitmenu)
