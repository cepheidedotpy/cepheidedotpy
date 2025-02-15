# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 14:31:59 2022
This Tkinter app can get S3P & S2P files in a directory and display them
after selection
@author: T0188303
_version :8
"""
import os
import tkinter as tk
from os import listdir
from os.path import isfile, join
from tkinter import Menu
from tkinter import Toplevel
from tkinter import font
from tkinter import scrolledtext
from tkinter import ttk

# Implement the default Matplotlib key bindings.
import matplotlib.pyplot as plt
import numpy as np
import skrf as rf
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)  # , NavigationToolbar2Tk)
from matplotlib.widgets import Cursor

# ==============================================================================
# Imports#%matplotlib inline
# ==============================================================================
import Rstest

# %matplotlib inline

""" This GUI is used to display S Parameters inside a Folder chosen by the user."""
_version = '8'


class AnnotatedCursor(Cursor):
    """
    A crosshair cursor like `~matplotlib.widgets.Cursor` with a text_file_name_s3p_test showing \
    the current coordinates.
    For the cursor to remain responsive you must keep a reference to it.
    The data of the axis specified as *dataaxis* must be in ascending
    order. Otherwise, the `numpy.searchsorted` call might fail and the text_file_name_s3p_test
    disappears. You can satisfy the requirement by sorting the data you figure.
    Usually the data is already sorted (if it was created e.g. using
    `numpy.linspace`), but e.g. scatter plots might cause this problem.
    The cursor sticks to the plotted line.
    Parameters
    ----------
    line : `matplotlib.lines.Line2D`
        The figure line from which the data coordinates are displayed.
    numberformat : `python format string <https://docs.python.org/3/\
    library/string.html#formatstrings>`_, optional, default: "{0:.4g};{1:.4g}"
        The displayed text_file_name_s3p_test is created by calling *format()* on this string
        with the two coordinates.

    offset : (float, float) default: (5, 5)
        The offset in display (pixel) coordinates of the text_file_name_s3p_test position
        relative to the cross hair.

    dataaxis : {"x", "y"}, optional, default: "x"
        If "x" is specified, the vertical cursor line sticks to the mouse
        pointer. The horizontal cursor line sticks to *line*
        at that x value. The text_file_name_s3p_test shows the data coordinates of *line*
        at the pointed x value. If you specify "y", it works in the opposite
        manner. But: For the "y" value, where the mouse points to, there might
        be multiple matching x values, if the plotted function is not biunique.
        Cursor and text_file_name_s3p_test coordinate will always refer to only one x value.
        So if you use the parameter value "y", ensure that your function is
        biunique.

    Other Parameters
    ----------------
    textprops : `matplotlib.text_file_name_s3p_test` properties as dictionary
        Specifies the appearance of the rendered text_file_name_s3p_test object.

    **cursorargs : `matplotlib.widgets.Cursor` properties
        Arguments passed to the internal `~matplotlib.widgets.Cursor` instance.
        The `matplotlib.axes.Axes` argument is mandatory! The parameter
        *useblit* can be set to *True* in order to achieve faster rendering.

    """

    def __init__(self, line, numberformat="{0:.4g};{1:.4g}", offset=(5, 5),
                 dataaxis='x', textprops=None, **cursorargs):
        if textprops is None:
            textprops = {}
        # The line object, for which the coordinates are displayed
        self.line = line
        # The format string, on which .format() is called for creating the text_file_name_s3p_test
        self.numberformat = numberformat
        # Text position offset
        self.offset = np.array(offset)
        # The axis in which the cursor position is looked up
        self.dataaxis = dataaxis

        # First call baseclass constructor.
        # Draws cursor and remembers background for blitting.
        # Saves ax_s3p as class attribute.
        super().__init__(**cursorargs)

        # Default value for position of text_file_name_s3p_test.
        self.set_position(self.line.get_xdata()[0], self.line.get_ydata()[0])
        # Create invisible animated text_file_name_s3p_test
        self.text = self.ax.text(
            self.ax.get_xbound()[0],
            self.ax.get_ybound()[0],
            "0, 0",
            animated=bool(self.useblit),
            visible=False, **textprops)
        # The position at which the cursor was last drawn
        self.lastdrawnplotpoint = None

    def onmove(self, event):
        """
        Overridden draw callback for cursor. Called when moving the mouse.
        """

        # Leave method under the same conditions as in overridden method
        if self.ignore(event):
            self.lastdrawnplotpoint = None
            return
        if not self.canvas.widgetlock.available(self):
            self.lastdrawnplotpoint = None
            return

        # If the mouse left drawable area, we now make the text_file_name_s3p_test invisible.
        # Baseclass will redraw complete s3p_canvas after, which makes both text_file_name_s3p_test
        # and cursor disappear.
        if event.inaxes != self.ax:
            self.lastdrawnplotpoint = None
            self.text.set_visible(False)
            super().onmove(event)
            return

        # Get the coordinates, which should be displayed as text_file_name_s3p_test,
        # if the event coordinates are valid.
        plotpoint = None
        if event.xdata is not None and event.ydata is not None:
            # Get figure point related to current x position.
            # These coordinates are displayed in text_file_name_s3p_test.
            plotpoint = self.set_position(event.xdata, event.ydata)
            # Modify event, such that the cursor is displayed on the
            # plotted line, not at the mouse pointer,
            # if the returned figure point is valid
            if plotpoint is not None:
                event.xdata = plotpoint[0]
                event.ydata = plotpoint[1]

        # If the plotpoint is given, compare to last drawn plotpoint and
        # return if they are the same.
        # Skip even the call of the base class, because this would restore the
        # background, draw the cursor lines and would leave us the job to
        # re-draw the text_file_name_s3p_test.
        if plotpoint is not None and plotpoint == self.lastdrawnplotpoint:
            return

        # Baseclass redraws s3p_canvas and cursor. Due to blitting,
        # the added text_file_name_s3p_test is removed in this call, because the
        # background is redrawn.
        super().onmove(event)

        # Check if the display of text_file_name_s3p_test is still necessary.
        # If not, just return.
        # This behaviour is also cloned from the base class.
        if not self.get_active() or not self.visible:
            return

        # Draw the widget, if event coordinates are valid.
        if plotpoint is not None:
            # Update position and displayed text_file_name_s3p_test.
            # Position: Where the event occurred.
            # Text: Determined by set_position() method earlier
            # Position is transformed to pixel coordinates,
            # an offset is added there and this is transformed back.
            temp = [event.xdata, event.ydata]
            temp = self.ax.transData.transform(temp)
            temp = temp + self.offset
            temp = self.ax.transData.inverted().transform(temp)
            self.text.set_position(temp)
            self.text.set_text(self.numberformat.format(*plotpoint))
            self.text.set_visible(self.visible)

            # Tell base class, that we have drawn something.
            # Baseclass needs to know, that it needs to restore a clean
            # background, if the cursor leaves our figure context.
            self.needclear = True

            # Remember the recently drawn cursor position, so events for the
            # same position (mouse moves slightly between two figure points)
            # can be skipped
            self.lastdrawnplotpoint = plotpoint
        # otherwise, make text_file_name_s3p_test invisible
        else:
            self.text.set_visible(False)

        # Draw changes. Cannot use _update method of baseclass,
        # because it would first restore the background, which
        # is done already and is not necessary.
        if self.useblit:
            self.ax.draw_artist(self.text)
            self.canvas.blit(self.ax.bbox)
        else:
            # If blitting is deactivated, the overridden _update call made
            # by the base class immediately returned.
            # We still have to draw the changes.
            self.canvas.draw_idle()

    def set_position(self, xpos, ypos):
        """
        Finds the coordinates, which have to be shown in text_file_name_s3p_test.

        The behaviour depends on the *dataaxis* attribute. Function looks
        up the matching figure coordinate for the given mouse position.

        Parameters
        ----------
        xpos : float
            The current x position of the cursor in data coordinates.
            Important if *dataaxis* is set to 'x'.
        ypos : float
            The current y position of the cursor in data coordinates.
            Important if *dataaxis* is set to 'y'.

        Returns
        -------
        ret : {2D array-like, None}
            The coordinates which should be displayed.
            *None* is the fallback value.
        """

        # Get figure line data
        xdata = self.line.get_xdata()
        ydata = self.line.get_ydata()

        # The dataaxis attribute decides, in which axis we look up which cursor
        # coordinate.
        if self.dataaxis == 'x':
            pos = xpos
            data = xdata
            lim = self.ax.get_xlim()
        elif self.dataaxis == 'y':
            pos = ypos
            data = ydata
            lim = self.ax.get_ylim()
        else:
            raise ValueError(f"The data axis specifier {self.dataaxis} should "
                             f"be 'x' or 'y'")

        # If position is valid and in valid figure data range.
        if pos is not None and lim[0] <= pos <= lim[-1]:
            # Find closest x value in sorted x vector.
            # This requires the plotted data to be sorted.
            index = np.searchsorted(data, pos)
            # Return none, if this index is out of range.
            if index < 0 or index >= len(data):
                return None
            # Return figure point as tuple.
            return (xdata[index], ydata[index])

        # Return none if there is no good related point for this x position.
        return None

    def clear(self, event):
        """
        Overridden clear callback for cursor, called before drawing the figure.
        """

        # The base class saves the clean background for blitting.
        # Text and cursor are invisible,
        # until the first mouse move event occurs.
        super().clear(event)
        if self.ignore(event):
            return
        self.text.set_visible(False)

    def _update(self):
        """
        Overridden method for either blitting or drawing the widget s3p_canvas.

        Passes call to base class if blitting is activated, only.
        In other cases, one draw_idle call is enough, which is placed
        explicitly in this class (see *onmove()*).
        In that case, `~matplotlib.widgets.Cursor` is not supposed to draw
        something using this method.
        """

        if self.useblit:
            super()._update()


# ==============================================================================
# Globals
# ==============================================================================
tab_padx = 5
tab_pady = 5
plt.style.use('default')
plt.rcParams["legend.fontsize"] = 10
plt.rcParams["axes.labelsize"] = 10
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 15


class Window(tk.Tk, Toplevel):
    def __init__(self, master=None, *args, **kwargs):
        tk.Tk.__init__(self, master)
        s = ttk.Style()
        # s.theme_use('default')
        s.configure('.', font=('Bahnschrift Light', 10))
        self.title(f"SUMMIT 11K Machine Interface v{_version}")
        self.menubar()
        self.resizable(True, True)
        self.tabControl = ttk.Notebook(self)  # Create Tab Control

        # self.fig_s3p = plt.figure(num=1, visible=True, dpi=100, tight_layout=True, figsize=(14, 4.2), frameon=True)
        self.fig = plt.figure(num=1, dpi=100, tight_layout=True, figsize=(13, 4.1), frameon=True)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax.grid()

        # self.fig_s2p = plt.figure(num=2, visible=True, dpi=100, tight_layout=True, figsize=(14, 4.2), frameon=True)
        self.fig2 = plt.figure(num=2, dpi=100, tight_layout=True, figsize=(13, 4.1), frameon=True)
        self.ax2 = self.fig2.add_subplot(1, 1, 1)
        self.ax2.grid()

        # self.fig_pull_in = plt.figure(num=3, visible=True, dpi=100, tight_layout=True, figsize=(14, 4.2), frameon=True)
        self.fig3 = plt.figure(num=3, dpi=100, tight_layout=True, figsize=(13, 3.5), frameon=True)
        self.ax3 = self.fig3.add_subplot(1, 1, 1)
        self.ax3.grid()

        self.fig4 = plt.figure(num=4, dpi=100, tight_layout=True, figsize=(6.5, 6), frameon=True)
        self.ax4 = self.fig4.add_subplot(1, 1, 1)
        self.ax4.grid()

        self.sparmeter_s3p = tk.StringVar(value='S11')
        self.sparmeter_s2p = tk.StringVar(value='S11')

        self.scale_amplitude_value = tk.DoubleVar(value=-20)
        self.scale_voltage_value = tk.DoubleVar(value=40)
        self.scale_isolation_value = tk.DoubleVar(value=-20)
        self.scale_frequency_upper_value = tk.DoubleVar(value=2 * 10e9)
        self.scale_frequency_lower_value = tk.DoubleVar(value=0.1 * 10e9)

        self.ax.set_ylim(ymin=self.scale_amplitude_value.get(), ymax=0)
        self.ax.set_xlim(xmin=0, xmax=self.scale_frequency_upper_value.get())

        tab1 = self.add_Tab(tab_name=' S3P Files ', notebook=self.tabControl, col=0, row=1)  # s3p Tab display
        tab2 = self.add_Tab(tab_name=' S2P Files ', notebook=self.tabControl, col=0, row=1)  # s2p Tab display
        tab3 = self.add_Tab(tab_name=' Pull-in Files ', notebook=self.tabControl, col=0, row=1)  # Pull-in Tab display
        tab4 = self.add_Tab(tab_name=' Pull-in Test ', notebook=self.tabControl, col=0, row=1)  # Pull-in Test Tab
        tab5 = self.add_Tab(tab_name=' SNP Test ', notebook=self.tabControl, col=0, row=1)  # s3p test Tab
        tab6 = self.add_Tab(tab_name=' Power Test ', notebook=self.tabControl, col=0, row=1)  # s3p test Tab
        tab7 = self.add_Tab(tab_name=' Ressource Page ', notebook=self.tabControl, col=0, row=1)  # s3p test Tab
        # ==============================================================================
        # TAB1 S3P parameter display
        # ==============================================================================
        # This TAB is for S3P parameter display
        frame1 = self.add_Label_frame(tab1, 's3p Directory', 0, 0)  # s3p Frame
        # s3p_dir_name is the directory variable used in the entry entereded_var_s3p
        self.s3p_dir_name = tk.StringVar(
            value=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\S3P')  # Entry variable for s3p dir
        # Adding labels and frame_s3p_display
        self.add_Label(frame1, 'Directory', col=1, row=1).grid(sticky='e', ipadx=tab_padx,
                                                               ipady=tab_padx)  # Directory frame label
        self.add_Label(frame1, 'File', col=1, row=2).grid(sticky='e', ipadx=tab_padx,
                                                          ipady=tab_padx)  # File frame label
        self.add_Label(frame1, 'S parameter', col=1, row=3).grid(sticky='e', ipadx=tab_padx,
                                                                 ipady=tab_padx)  # File frame label
        self.frame3 = self.add_Label_frame(tab1, 's3p Display', 0, 1)
        #  Adding entry for file directory
        self.entered_var_s3p = self.add_entry(frame1, textvar=self.s3p_dir_name, width=70, col=2, row=1)

        file_s3p = self.filetypes_dir(self.entered_var_s3p.get())[0]

        self.s3p_file_name_combobox = self.add_combobox(frame1, text=file_s3p, col=2, row=2, width=100)

        self.sparmeter_chosen_s3p = self.add_combobox(frame1, text=self.sparmeter_s3p, col=2, row=3, width=100)
        self.sparmeter_chosen_s3p['values'] = ('S11', 'S12', 'S13', 'S21', 'S22', 'S23', 'S31', 'S32', 'S33')

        self.button1 = self.add_Button(tab=frame1, button_name=' Update Files ',
                                       command=lambda: [self.update_entries_s3p_v2(),
                                                        self.clicked_Button(self.button1)], col=3,
                                       row=1)  # (self.update_entries_s3p_v2), (self.update_button)

        self.add_Button(tab=frame1, button_name='Exit', command=self._quit, col=5, row=1)
        self.add_Button(frame1, 'Plot', command=self.plot_s3p, col=3, row=3)
        self.add_Button(frame1, 'Delete graphs', command=self.delete_axs_s3p, col=3, row=2)

        self.canvas = self.create_canvas_s3p(col=2, row=5, frame=self.frame3)

        self.slider_amplitude = self.add_slider(frame=self.frame3, _from=0, to=-40, name="Amplitude (dB)",
                                                variable=self.scale_amplitude_value, step=5)
        self.slider_frequency = self.add_slider(frame=self.frame3, _from=1e9, to=40e9,
                                                name="Upper Frequency Limit (Hz)",
                                                variable=self.scale_frequency_upper_value, step=10e9)
        self.slider_lower_frequency = self.add_slider(frame=self.frame3, _from=1e9, to=40e9,
                                                      name=" Lower Frequency Limit (Hz)",
                                                      variable=self.scale_frequency_lower_value, step=10e9)

        self.slider_amplitude.pack(side='left')
        self.slider_frequency.pack(side='right')
        self.slider_lower_frequency.pack(side='right')
        # ==============================================================================
        # TAB2 S2P parameter display
        # ==============================================================================
        # This TAB is for S2P parameter display
        frame2 = self.add_Label_frame(tab2, 's2p Directory', 0, 0)  # s2p Frame

        self.s2p_dir_name = tk.StringVar(value=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\S2P')
        self.add_Label(frame2, 'Directory', col=1, row=1).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame2, 'File', col=1, row=2).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame2, 'S parameter', col=1, row=3).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)

        self.frame4 = self.add_Label_frame(tab2, 's2p Display', 0, 1)

        self.entered_var_s2p = self.add_entry(frame2, textvar=self.s2p_dir_name, width=70, col=2, row=1)

        file_s2p = self.filetypes_dir(self.entered_var_s2p.get())[1]
        self.s2p_file_name_combobox = self.add_combobox(frame2, text=file_s2p, col=2, row=2, width=100)
        self.sparmeter_chosen_s2p = self.add_combobox(frame2, text=self.sparmeter_s2p, col=2, row=3, width=100)
        self.sparmeter_chosen_s2p['values'] = ('S11', 'S12', 'S21', 'S22')

        self.button2 = self.add_Button(tab=frame2, button_name=' Update Files ',
                                       command=lambda: [self.update_entries_s2p_v2(),
                                                        self.clicked_Button(self.button2)], col=3, row=1)
        self.add_Button(frame2, 'Exit', command=self._quit, col=5, row=1).grid_anchor('e')
        self.add_Button(frame2, 'Plot', command=self.plot_s2p, col=3, row=3)
        self.add_Button(frame2, 'Delete Graphs', command=self.delete_axs_s2p, col=3, row=2)

        self.canvas2 = self.create_canvas_s2p(col=2, row=5, frame=self.frame4)

        self.slider_amplitude_s2p = self.add_slider(frame=self.frame4, _from=0, to=-40, name="Amplitude (dB)",
                                                    variable=self.scale_amplitude_value, step=5)
        self.slider_frequency_s2p = self.add_slider(frame=self.frame4, _from=1e9, to=40e9,
                                                    name="Upper Frequency limit (Hz)",
                                                    variable=self.scale_frequency_upper_value, step=10e9)
        self.slider_lower_frequency_s2p = self.add_slider(frame=self.frame4, _from=1e9, to=40e9,
                                                          name=" Lower Frequency Limit (Hz)",
                                                          variable=self.scale_frequency_lower_value, step=10e9)

        self.slider_amplitude_s2p.pack(side='left')
        self.slider_frequency_s2p.pack(side='right')
        self.slider_lower_frequency_s2p.pack(side='right')
        # ==============================================================================
        # TAB3 Pull voltage vs isolation display
        # ==============================================================================
        # This TAB is for Pull voltage vs isolation display
        frame5 = self.add_Label_frame(tab3, 'Vpull-in Directory', 0, 0)  # s2p Frame
        self.pullin_dir_name = tk.StringVar(
            value=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\Pullin voltage')
        self.add_Label(frame5, 'Directory', col=1, row=1).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame5, 'File', col=1, row=2).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)

        self.frame6 = self.add_Label_frame(tab3, 'Pull-in Display', 0, 1)

        self.entered_var_txt = self.add_entry(frame5, textvar=self.pullin_dir_name, width=70, col=2, row=1)

        file_txt = self.filetypes_dir(self.entered_var_txt.get())[2]
        self.txt_file_name_combobox = self.add_combobox(frame5, text=file_txt, col=2, row=2, width=100)

        self.button3 = self.add_Button(tab=frame5, button_name=' Update Files ',
                                       command=lambda: [self.update_entries_txt(), self.clicked_Button(self.button3)],
                                       col=3, row=1)
        self.add_Button(frame5, 'Exit', command=self._quit, col=5, row=1).grid_anchor('e')
        self.add_Button(frame5, 'Plot', command=lambda: [self.plot_vpullin(), self.calculate_pullin_out_voltage()],
                        col=3, row=3)
        self.add_Button(frame5, 'Delete Graphs', command=self.delete_axs_vpullin, col=3, row=2)
        self.add_Button(frame5, 'Calculate Pull-in and Pull-out voltages', command=self.calculate_pullin_out_voltage,
                        col=2, row=3).configure(width=40)
        self.textscroll = self.add_scrolledtext(tab=self.frame6, text='', col=1, row=2, scrol_w=100, scrol_h=3)

        self.canvas3 = self.create_canvas_txt(col=2, row=5, frame=self.frame6)

        self.slider_isolation = self.add_slider(frame=self.frame6, _from=0, to=-40, name="Isolation (dB)",
                                                variable=self.scale_isolation_value, step=5)
        self.slider_voltage = self.add_slider(frame=self.frame6, _from=0, to=50, name="Voltage upper limit (V)",
                                              variable=self.scale_voltage_value, step=5)

        self.slider_isolation.pack(side='left')
        self.slider_voltage.pack(side='right')
        # ==============================================================================
        # TAB4 Pull down voltage vs isolation measurement
        # ==============================================================================
        # This TAB is for Pull down voltage vs isolation measurement
        frame14 = self.add_Label_frame(tab4, 'Component information', 0, 0)

        self.add_Label(frame14, 'DIR', col=0, row=0).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame14, 'Project', col=0, row=1).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame14, 'Cell', col=0, row=2).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame14, 'Reticule', col=0, row=3).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame14, 'Device', col=0, row=4).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame14, 'Bias Voltage', col=0, row=5).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)

        self.testpullin_dir = tk.StringVar(value=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\Pullin '
                                                 r'voltage')
        self.testpullin_project = tk.StringVar(value=r'Project_Name')
        self.testpullin_cell = tk.StringVar(value=r'Cell_Name')
        self.testpullin_reticule = tk.StringVar(value=r'Reticule')
        self.testpullin_device = tk.StringVar(value=r'Device_name')
        self.testpullin_filecreated = tk.StringVar(value=r'EMPTY')
        self.bias_voltage = tk.StringVar(value=r'Bias_Voltage')
        self.add_Button(tab=frame14, button_name='Create-file', command=self.create_testpullin_file, col=2, row=0)

        self.add_entry(tab=frame14, textvar=self.testpullin_dir, width=20, col=1, row=0)
        self.add_entry(tab=frame14, textvar=self.testpullin_project, width=20, col=1, row=1)
        self.add_entry(tab=frame14, textvar=self.testpullin_cell, width=20, col=1, row=2)
        self.add_entry(tab=frame14, textvar=self.testpullin_reticule, width=20, col=1, row=3)
        self.add_entry(tab=frame14, textvar=self.testpullin_device, width=20, col=1, row=4)
        self.add_entry(tab=frame14, textvar=self.bias_voltage, width=20, col=1, row=5)

        # Signal Generator-------------------------------------------------------------
        frame15 = self.add_Label_frame(tab=tab4, frame_name='Signal Generator', col=0, row=1)

        self.pullin_v_bias = tk.DoubleVar(value=10)  # Peak bias voltage for ramp funtion
        self.ramp_width = tk.DoubleVar(value=100)  # Ramp length for ramp funtion

        self.chosen_bias_voltage_pullin = self.add_entry(tab=frame14, textvar=self.pullin_v_bias, width=20, col=1,
                                                         row=5)

        self.add_Label(frame15, 'Bias Voltage', col=0, row=0).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame15, 'Ramp length', col=0, row=1).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.entered_ramp_volt = self.add_entry(frame15, textvar=self.pullin_v_bias, width=10, col=1, row=0)
        self.entered_ramp_width = self.add_entry(frame15, textvar=self.ramp_width, width=10, col=1, row=1)
        self.add_Label(frame15, '(V)', col=2, row=0).grid(sticky='w', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame15, '(µs)', col=2, row=1).grid(sticky='w', ipadx=tab_padx, ipady=tab_padx)

        self.add_Button(tab=frame15, button_name='Set Bias Voltage', command=self.set_bias_pullin, col=3, row=0).grid(
            sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Button(tab=frame15, button_name='Set Ramp Width', command=self.set_ramp_width, col=3, row=1).grid(
            sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Button(tab=frame15, button_name='Set Pulse Gen', command=self.set_pulse_gen_ramp, col=3, row=3).grid(
            sticky='e', ipadx=tab_padx, ipady=tab_padx)

        # General controls---------------------------------------------------------------
        frame16 = self.add_Label_frame(tab=tab4, frame_name='General controls', col=2, row=0)

        self.text3 = tk.Text(frame16, width=40, height=1, wrap=tk.WORD, border=4, borderwidth=2, relief=tk.SUNKEN,
                             font=('Bahnschrift Light', 10))  # Filename
        self.text3.grid(column=0, row=0, sticky='n', columnspan=5)
        self.text4 = tk.Text(frame16, width=40, height=10, wrap=tk.WORD, border=4, borderwidth=2, relief=tk.SUNKEN,
                             font=('Bahnschrift Light', 10))  # Debug text_file_name_s3p_test display
        self.text4.grid(column=0, row=3, sticky='n', columnspan=4)

        self.add_Button(tab=frame16, button_name='Reset Signal Generator', command=self.reset_sig_gen, col=0,
                        row=1).grid(ipadx=tab_padx, ipady=tab_padx)
        self.add_Button(tab=frame16, button_name='Exit', command=lambda: [self._quit(), self.close_ressources()], col=1,
                        row=1).grid(ipadx=tab_padx, ipady=tab_padx)
        self.add_Button(tab=frame16, button_name='Plot IsovsV',
                        command=lambda: [self.trace_pulldown(), self.acquire_pulldown_data()], col=1, row=5).grid(
            ipadx=tab_padx, ipady=tab_padx)
        # self.add_button(tab=frame16, button_name='Plot IsovsV',command=self.trace_pull_down, col=1, row=5).grid(ipadx=tab_pad_x,ipady=tab_pad_x)
        # ------------------------------------------------------------------------------
        frame13 = self.add_Label_frame(tab=tab4, frame_name='Oscilloscope Tecktronix', col=1, row=0, rowspan=2)
        self.canvas4 = self.create_canvas_pullin(col=2, row=5, frame=frame13)

        frame15 = self.add_Label_frame(tab=tab4, frame_name='Measurement', col=2, row=1, rowspan=2)

        self.add_Label(frame15, 'Positive-Pull-in', col=0, row=0).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.text5 = tk.Text(frame15, width=15, height=1, wrap=tk.WORD, border=4, borderwidth=2, relief=tk.SUNKEN,
                             font=('Bahnschrift Light', 10))  # Positive Pull-in
        self.text5.grid(column=1, row=0, sticky='n', columnspan=5)

        self.add_Label(frame15, 'Negative-Pull-in', col=0, row=1).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.text6 = tk.Text(frame15, width=15, height=1, wrap=tk.WORD, border=4, borderwidth=2, relief=tk.SUNKEN,
                             font=('Bahnschrift Light', 10))  # Negative Pull-in
        self.text6.grid(column=1, row=1, sticky='n', columnspan=5)

        self.add_Label(frame15, 'Positive-Pull-out', col=0, row=2).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.text7 = tk.Text(frame15, width=15, height=1, wrap=tk.WORD, border=4, borderwidth=2, relief=tk.SUNKEN,
                             font=('Bahnschrift Light', 10))  # Positive Pull-out
        self.text7.grid(column=1, row=2, sticky='n', columnspan=5)

        self.add_Label(frame15, 'Negative-Pull-out', col=0, row=3).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.text8 = tk.Text(frame15, width=15, height=1, wrap=tk.WORD, border=4, borderwidth=2, relief=tk.SUNKEN,
                             font=('Bahnschrift Light', 10))  # Negative Pull-out
        self.text8.grid(column=1, row=3, sticky='n', columnspan=5)

        self.add_Label(frame15, 'Isolation at PI(+)', col=0, row=4).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.text9 = tk.Text(frame15, width=15, height=1, wrap=tk.WORD, border=4, borderwidth=2, relief=tk.SUNKEN,
                             font=('Bahnschrift Light', 10))  # Isolation at PI (+)
        self.text9.grid(column=1, row=4, sticky='n', columnspan=5)

        self.add_Label(frame15, 'Isolation at PO (+)', col=0, row=5).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.text10 = tk.Text(frame15, width=15, height=1, wrap=tk.WORD, border=4, borderwidth=2, relief=tk.SUNKEN,
                              font=('Bahnschrift Light', 10))  # Isolation at PO (+)
        self.text10.grid(column=1, row=5, sticky='n', columnspan=5)

        self.add_Label(frame15, 'Isolation at PI (-)', col=0, row=6).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.text11 = tk.Text(frame15, width=15, height=1, wrap=tk.WORD, border=4, borderwidth=2, relief=tk.SUNKEN,
                              font=('Bahnschrift Light', 10))  # Isolation at PI (-)
        self.text11.grid(column=1, row=6, sticky='n', columnspan=5)

        self.add_Label(frame15, 'Isolation at PO (-)', col=0, row=7).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.text12 = tk.Text(frame15, width=15, height=1, wrap=tk.WORD, border=4, borderwidth=2, relief=tk.SUNKEN,
                              font=('Bahnschrift Light', 10))  # Isolation at PO (-)
        self.text12.grid(column=1, row=7, sticky='n', columnspan=5)
        # ==============================================================================
        # TAB5 S-parameters test
        # ==============================================================================
        frame8 = self.add_Label_frame(tab5, 'Component information', 0, 0)  # s3p frame

        self.add_Label(frame8, 'DIR', col=0, row=0).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame8, 'Project', col=0, row=1).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame8, 'Cell', col=0, row=2).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame8, 'Reticule', col=0, row=3).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame8, 'Device', col=0, row=4).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame8, 'Status', col=0, row=5).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame8, 'Bias Voltage', col=0, row=6).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)

        self.tests3p_dir = tk.StringVar(value=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\S3P')
        self.tests3p_project = tk.StringVar(value=r'Project_Name')
        self.tests3p_cell = tk.StringVar(value=r'Cell_Name')
        self.tests3p_reticule = tk.StringVar(value=r'Reticule')
        self.tests3p_device = tk.StringVar(value=r'Device_name')
        self.tests3p_filecreated = tk.StringVar(value=r'EMPTY')
        self.component_state = self.add_combobox(frame8, text='Active', col=1, row=5, width=20)
        self.bias_voltage = tk.StringVar(value=r'Bias_Voltage')

        self.chosen_component_state = self.add_combobox(frame8, text=self.component_state, col=1, row=5, width=20)
        self.chosen_component_state['values'] = ('Active', 'Frozen')
        self.chosen_component_state.current(0)

        self.add_entry(tab=frame8, textvar=self.tests3p_dir, width=20, col=1, row=0)
        self.add_entry(tab=frame8, textvar=self.tests3p_project, width=20, col=1, row=1)
        self.add_entry(tab=frame8, textvar=self.tests3p_cell, width=20, col=1, row=2)
        self.add_entry(tab=frame8, textvar=self.tests3p_reticule, width=20, col=1, row=3)
        self.add_entry(tab=frame8, textvar=self.tests3p_device, width=20, col=1, row=4)

        self.add_Button(tab=frame8, button_name='Create-file', command=self.create_tests3p_file, col=2, row=0)

        # ------------------------------------------------------------------------------
        frame9 = self.add_Label_frame(tab=tab5, frame_name='Signal Generator', col=0, row=2)

        self.pullin_v = tk.DoubleVar(value=10)
        self.pulse_width = tk.DoubleVar(value=5)
        self.pulse_freq = tk.DoubleVar(value=0.1)
        self.chosen_bias_voltage = self.add_entry(tab=frame8, textvar=self.pullin_v, width=20, col=1, row=6)

        self.add_Label(frame9, 'Bias Voltage', col=0, row=0).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame9, 'Pulse Width', col=0, row=1).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.entered_pullin_volt = self.add_entry(frame9, textvar=self.pullin_v, width=10, col=1, row=0)
        self.entered_pulse_width = self.add_entry(frame9, textvar=self.pulse_width, width=10, col=1, row=1)
        self.add_Label(frame9, '(V)', col=2, row=0).grid(sticky='w', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame9, '(s)', col=2, row=1).grid(sticky='w', ipadx=tab_padx, ipady=tab_padx)

        self.add_Label(frame9, 'Pulse Frequency', col=0, row=2).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.entered_pulse_freq = self.add_entry(frame9, textvar=self.pulse_freq, width=10, col=1, row=2)
        self.add_Label(frame9, '(Hz)', col=2, row=2).grid(sticky='w', ipadx=tab_padx, ipady=tab_padx)

        self.add_Button(tab=frame9, button_name='Set Bias Voltage', command=self.set_Bias_Voltage, col=3, row=0).grid(
            sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Button(tab=frame9, button_name='Set Pulse Width', command=self.set_ramp_width, col=3, row=1).grid(
            sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Button(tab=frame9, button_name='Set prf', command=self.set_PRF, col=3, row=2).grid(sticky='e',
                                                                                                    ipadx=tab_padx,
                                                                                                    ipady=tab_padx)
        self.add_Button(tab=frame9, button_name='Set Pulse Gen', command=self.set_pulse_gen, col=3, row=3).grid(
            sticky='e', ipadx=tab_padx, ipady=tab_padx)
        # ------------------------------------------------------------------------------
        frame10 = self.add_Label_frame(tab=tab5, frame_name='ZVA', col=1, row=2)

        self.fstart = tk.DoubleVar(value=1)
        self.fstop = tk.DoubleVar(value=10)
        self.nb_points = tk.DoubleVar(value=100)

        self.add_Label(frame10, 'Fstart', col=0, row=0).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame10, 'Fstop', col=0, row=1).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame10, 'Nb Points', col=0, row=2).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.entered_fstart = self.add_entry(frame10, textvar=self.fstart, width=10, col=1, row=0)
        self.entered_fstop = self.add_entry(frame10, textvar=self.fstop, width=10, col=1, row=1)
        self.entered_nb_points = self.add_entry(frame10, textvar=self.nb_points, width=10, col=1, row=2)
        self.add_Label(frame10, '(GHz)', col=2, row=0).grid(sticky='w', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame10, '(GHz)', col=2, row=1).grid(sticky='w', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame10, '(Pts)', col=2, row=2).grid(sticky='w', ipadx=tab_padx, ipady=tab_padx)

        self.add_Button(tab=frame10, button_name='Set Fstart', command=self.set_fstart, col=3, row=0).grid(sticky='e',
                                                                                                           ipadx=tab_padx,
                                                                                                           ipady=tab_padx)
        self.add_Button(tab=frame10, button_name='Set Fstop', command=self.set_fstop, col=3, row=1).grid(sticky='e',
                                                                                                         ipadx=tab_padx,
                                                                                                         ipady=tab_padx)
        self.add_Button(tab=frame10, button_name='Set Nb points', command=self.set_nb_points, col=3, row=2).grid(
            sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Button(tab=frame10, button_name='Set ZVA', command=self.set_zva, col=3, row=3).grid(sticky='e',
                                                                                                     ipadx=tab_padx,
                                                                                                     ipady=tab_padx)
        self.add_Button(tab=frame10, button_name='Capture S3P', command=self.data_acquire, col=1, row=4).grid(
            sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Button(tab=frame10, button_name='Capture S2P', command=self.data_acquire_s2p, col=2, row=4).grid(
            sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Button(tab=frame10, button_name='Capture S1P', command=self.data_acquire_s1p, col=3, row=4).grid(
            sticky='e', ipadx=tab_padx, ipady=tab_padx)

        # ------------------------------------------------------------------------------
        frame12 = self.add_Label_frame(tab=tab5, frame_name='General controls', col=1, row=0)

        self.text = tk.Text(frame12, width=40, height=1, wrap=tk.WORD, border=4, borderwidth=2, relief=tk.SUNKEN,
                            font=('Bahnschrift Light', 10))
        self.text.grid(column=0, row=0, sticky='n', columnspan=5)
        self.text2 = tk.Text(frame12, width=40, height=10, wrap=tk.WORD, border=4, borderwidth=2, relief=tk.SUNKEN,
                             font=('Bahnschrift Light', 10))
        self.text2.grid(column=0, row=3, sticky='n', columnspan=4)

        self.add_Button(tab=frame12, button_name='Comms prep', command=Rstest.comprep_zva, col=0, row=1).grid(
            ipadx=tab_padx, ipady=tab_padx)
        self.add_Button(tab=frame12, button_name='Reset ZVA', command=self.reset_zva, col=0, row=2).grid(ipadx=tab_padx,
                                                                                                         ipady=tab_padx)
        self.add_Button(tab=frame12, button_name='Exit', command=lambda: [self._quit(), self.close_ressources()], col=1,
                        row=1).grid(ipadx=tab_padx, ipady=tab_padx)
        # ==============================================================================
        # TAB7 Power measurement TAB
        # ==============================================================================
        frame17 = self.add_Label_frame(tab6, 'Component information', 0, 0)  # power sweep frame

        self.add_Label(frame17, 'DIR', col=0, row=0).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame17, 'Project', col=0, row=1).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame17, 'Cell', col=0, row=2).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame17, 'Reticule', col=0, row=3).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame17, 'Device', col=0, row=4).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame17, 'Status', col=0, row=5).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame17, 'Bias Voltage', col=0, row=6).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)

        self.test_pow_dir = tk.StringVar(value=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\Power handling')
        self.test_pow_project = tk.StringVar(value=r'Project_Name')
        self.test_pow_cell = tk.StringVar(value=r'Cell_Name')
        self.test_pow_reticule = tk.StringVar(value=r'Reticule')
        self.test_pow_device = tk.StringVar(value=r'Device_name')
        self.test_pow_filecreated = tk.StringVar(value=r'EMPTY')
        self.component_state_pow = self.add_combobox(frame17, text='Active', col=1, row=5, width=20)
        self.bias_voltage_pow = tk.StringVar(value=r'Bias_Voltage')

        self.chosen_component_state_pow = self.add_combobox(frame17, text=self.component_state, col=1, row=5, width=20)
        self.chosen_component_state_pow['values'] = ('Active', 'Frozen')
        self.chosen_component_state_pow.current(0)

        self.add_entry(tab=frame17, textvar=self.test_pow_dir, width=20, col=1, row=0)
        self.add_entry(tab=frame17, textvar=self.test_pow_project, width=20, col=1, row=1)
        self.add_entry(tab=frame17, textvar=self.test_pow_cell, width=20, col=1, row=2)
        self.add_entry(tab=frame17, textvar=self.test_pow_reticule, width=20, col=1, row=3)
        self.add_entry(tab=frame17, textvar=self.test_pow_device, width=20, col=1, row=4)
        self.add_entry(tab=frame17, textvar=self.bias_voltage_pow, width=20, col=1, row=6)

        self.add_Button(tab=frame17, button_name='Create-file', command=self.create_test_pow_file, col=2, row=0)
        self.add_Button(tab=frame17, button_name='Send trigger', command=Rstest.send_trig, col=2, row=1)
        # General controls---------------------------------------------------------------
        frame18 = self.add_Label_frame(tab=tab6, frame_name='General controls', col=2, row=0)

        self.text13 = tk.Text(frame18, width=40, height=1, wrap=tk.WORD, border=4, borderwidth=2, relief=tk.SUNKEN,
                              font=('Bahnschrift Light', 10))  # Filename
        self.text13.grid(column=0, row=0, sticky='n', columnspan=5)
        self.text14 = tk.Text(frame18, width=40, height=10, wrap=tk.WORD, border=4, borderwidth=2, relief=tk.SUNKEN,
                              font=('Bahnschrift Light', 10))  # Debug text_file_name_s3p_test display
        self.text14.grid(column=0, row=3, sticky='n', columnspan=4)

        self.add_Button(tab=frame18, button_name='Reset Signal Generator', command=self.set_pulse_gen_pulsemode, col=0,
                        row=1).grid(ipadx=tab_padx, ipady=tab_padx)
        self.add_Button(tab=frame18, button_name='Exit', command=lambda: [self._quit(), self.close_ressources()], col=1,
                        row=1).grid(ipadx=tab_padx, ipady=tab_padx)
        self.add_Button(tab=frame18, button_name='Launch Test', command=None, col=1, row=5).grid(ipadx=tab_padx,
                                                                                                 ipady=tab_padx)
        # ==============================================================================
        # TAB7 Ressource SCPI configuration
        # ==============================================================================
        frame7 = self.add_Label_frame(tab7, 'Ressouce Configuration', 0, 0)  # Ressource frame

        self.zva_inst = tk.StringVar(value=r'TCPIP0::ZNA67-101810::inst0::INSTR')
        self.sig_gen_inst = tk.StringVar(value=r'TCPIP0::A-33521B-00526::inst0::INSTR')
        self.osc_inst = tk.StringVar(value=r'TCPIP0::DPO5054-C011738::inst0::INSTR')
        self.powermeter_inst = tk.StringVar(value=u'TCPIP0::192.168.0.6::inst0::INSTR')
        self.rf_gen_inst = tk.StringVar(value=u'TCPIP0::192.168.0.5::inst0::INSTR')

        self.add_Label(frame7, 'ZVA', col=1, row=1).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame7, 'Signal Generator', col=1, row=2).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame7, 'Oscilloscope', col=1, row=3).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame7, 'Powermeter', col=1, row=4).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)
        self.add_Label(frame7, 'RF Generator', col=1, row=5).grid(sticky='e', ipadx=tab_padx, ipady=tab_padx)

        self.entered_var_zva_address = self.add_entry(frame7, textvar=self.zva_inst, width=70, col=2, row=1)
        self.entered_var_sig_gen_address = self.add_entry(frame7, textvar=self.sig_gen_inst, width=70, col=2, row=2)
        self.entered_var_osc_address = self.add_entry(frame7, textvar=self.osc_inst, width=70, col=2, row=3)
        self.entered_var_powermeter_address = self.add_entry(frame7, textvar=self.powermeter_inst, width=70, col=2,
                                                             row=4)
        self.entered_var_rf_gen_address = self.add_entry(frame7, textvar=self.rf_gen_inst, width=70, col=2, row=5)

        self.wm_resizable(width=True, height=True)
        self.protocol(name='WM_RESIZABLE')
        self.tabControl.pack()

    # ==============================================================================
    # Methods
    # ==============================================================================
    # General APP functions -------------------------------------------------------

    def menubar(self):  # Adds a menu_bar [IN WORK]
        menu_bar = Menu(self)
        self.config(menu=menu_bar)
        # Create  menu and add menu items
        file_menu = Menu(menu_bar, tearoff=0)  # Create File menu
        file_menu.add_command(label="New")  # Add New menu item
        file_menu.add_separator()  # Add New menu item
        file_menu.add_command(label="Exit", command=self._quit)  # Add Exit menu item
        menu_bar.add_cascade(label="File", menu=file_menu)  # Add File menu to menu bar
        return (file_menu)

    def _quit(self):  # Exit GUI cleanly (used in all TABS)
        self.quit()
        plt.close()
        self.destroy()

    def add_Tab(self, tab_name, notebook, col,
                row):  # Adds a tab to notebook at defined column and row and returns the tab instance
        tab_inst = ttk.Frame(notebook, relief='ridge', borderwidth=10)  # Create a tab
        notebook.add(tab_inst, text='{}'.format(tab_name))  # Add the tab
        notebook.grid(column=col, row=row)
        return (tab_inst)

    def add_Button(self, tab, button_name, command, col,
                   row):  # Adds a button with a button_name, command, column and row
        action = ttk.Button(tab, text=button_name, command=command, width=12, padding=0)
        action.configure(state='enabled')
        action.grid(column=col, row=row)
        return (action)

    def clicked_Button(self, button):  # Changes text_file_name_s3p_test to 'updated' on button press
        button.configure(text=' Updated ')
        return (button)

    def add_Label(self, tab, label_name, col,
                  row):  # Adds a label in tab named label_name at the designated column and row
        label = ttk.Label(tab, text=label_name)
        label.grid(column=col, row=row)
        return (label)

    def add_Label_frame(self, tab, frame_name, col, row,
                        rowspan=1):  # Adds a label_frame in tab named label_name at the designated column and row (label anchor set to North West)
        frame = ttk.LabelFrame(tab, text=frame_name, borderwidth=5, relief=tk.RIDGE, labelanchor='nw')
        frame.grid(column=col, row=row, sticky=tk.N + tk.S + tk.W + tk.E, rowspan=rowspan)
        return (frame)

    def add_entry(self, tab, textvar, width, col,
                  row):  # Adds an entry in the tab with a specified textvariable at the designated column and row
        entered = ttk.Entry(tab, width=width, textvariable=textvar, validate='focus', font=('Bahnschrift Light', 10))
        entered.grid(column=col, row=row, sticky="WE")
        return (entered)

    def add_combobox(self, tab, text, col, row,
                     width):  # Adds a Combobox in the tab with a specified textvariable text_file_name_s3p_test at the designated column and row
        self.combobox = ttk.Combobox(tab, textvariable=text, state='readonly',
                                     values='', validate='focus', width=width, height=10,
                                     font=('Bahnschrift Light', 10))
        self.combobox.grid(column=col, row=row)
        return (self.combobox)

    def add_scrolledtext(self, tab, text, col, row, scrol_w,
                         scrol_h):  # Adds a ScrolledText instance in tab with a textvariable text_file_name_s3p_test at row/col location and with scrol_w/scrolled_height dimensions
        scroll = scrolledtext.ScrolledText(tab, width=scrol_w, height=scrol_h, wrap=tk.WORD, border=2, relief=tk.SUNKEN,
                                           pady=0)
        scroll.pack(side='top')
        return (scroll)

    def extension_detector(self, file, path):  # Seprate file name and extension
        file, extension = os.path.splitext(file)
        return (extension, file)

    def filetypes_dir(self,
                      path):  # Calls extension_detector to separate different file types at set path and returns s3p, s2p and txt file tuples
        if path == '':
            return ('empty', 'empty')
            pass
        else:
            file_list = [f for f in listdir(path) if isfile(join(path, f))]
            # Separating file types
            nb_files = 0
            nb_txt = 0
            nb_s3p = 0
            nb_s2p = 0
            nb_other = 0
            txt_file = []
            s3p_file = []
            s2p_file = []
            other_file = []
            for nb_files in range(len(file_list)):
                if self.extension_detector(file_list[nb_files], path)[0] == '.txt':
                    nb_txt += 1
                    txt_file.append(file_list[nb_files])
                elif self.extension_detector(file_list[nb_files], path)[0] == '.s3p':
                    nb_s3p += 1
                    s3p_file.append(file_list[nb_files])
                elif self.extension_detector(file_list[nb_files], path)[0] == '.s2p':
                    nb_s2p += 1
                    s2p_file.append(file_list[nb_files])
                else:
                    nb_other += 1
                    other_file.append(file_list[nb_files])
            s3p_file_as_tuple = tuple(s3p_file)
            s2p_file_as_tuple = tuple(s2p_file)
            txt_file_as_tuple = tuple(txt_file)
            return (s3p_file_as_tuple, s2p_file_as_tuple, txt_file_as_tuple)

    def update_entries_s3p_v2(self):  # Updates directory entries
        entry_s3p = self.filetypes_dir(self.entered_var_s3p.get())[0]
        if entry_s3p == 'empty':
            self.s3p_file_name_combobox.set('empty_directory')
        else:
            self.s3p_file_name_combobox['values'] = entry_s3p
        return (self.s3p_file_name_combobox)

    def update_entries_s2p_v2(self):  # Updates directory entries
        entry_s2p = self.filetypes_dir(self.entered_var_s2p.get())[1]
        if entry_s2p == ('empty') or (''):
            self.s2p_file_name_combobox.set('empty_directory')
        else:
            self.s2p_file_name_combobox['values'] = entry_s2p
        return (self.s2p_file_name_combobox)

    def update_entries_txt(self):  # Updates directory entries
        entry_txt = self.filetypes_dir(self.entered_var_txt.get())[2]
        if entry_txt == 'empty':
            self.txt_file_name_combobox.set('empty_directory')
        else:
            self.txt_file_name_combobox['values'] = entry_txt
        return (self.txt_file_name_combobox)

    def create_canvas_s3p(self, col, row, frame):  # Creates s3p display Canvas in the frame and at col and row location
        canvas = FigureCanvasTkAgg(self.fig, master=frame)
        canvas._tkcanvas.pack(ipady=2, ipadx=2)
        # toolbar = NavigationToolbar2Tk(s3p_canvas = s3p_canvas, window = frame, pack_toolbar = True)
        return (canvas)

    def create_canvas_s2p(self, col, row, frame):  # Creates s2p display Canvas in the frame and at col and row location
        canvas = FigureCanvasTkAgg(self.fig2, master=frame)
        canvas._tkcanvas.pack(ipady=2, ipadx=2)
        # toolbar = NavigationToolbar2Tk(s3p_canvas = s3p_canvas, window = frame, pack_toolbar = True)
        return (canvas)

    def create_canvas_txt(self, col, row,
                          frame):  # Creates pull in and pull out display Canvas in the frame and at col and row location
        canvas = FigureCanvasTkAgg(self.fig3, master=frame)
        canvas._tkcanvas.pack(ipady=2, ipadx=2)
        # toolbar = NavigationToolbar2Tk(s3p_canvas = s3p_canvas, window = frame, pack_toolbar = True)
        return (canvas)

    def create_canvas_pullin(self, col, row,
                             frame):  # Creates pull in and pull out display (in measurement frame) Canvas in the frame and at col and row location
        canvas = FigureCanvasTkAgg(self.fig4, master=frame)
        canvas._tkcanvas.pack(ipady=2, ipadx=2)
        # toolbar = NavigationToolbar2Tk(s3p_canvas = s3p_canvas, window = frame, pack_toolbar = True)
        return (canvas)

    def create_tests3p_file(
            self):  # Gets the different entered strings at the set entries to construct a filename for the .s3p measurement
        self.text.delete(index1="%d.%d" % (1, 0), index2="%d.%s" % (1, 'end'))
        filename = '{}-{}-{}-{}-{}-{}V'.format(self.tests3p_project.get(),
                                               self.tests3p_cell.get(),
                                               self.tests3p_reticule.get(),
                                               self.tests3p_device.get(),
                                               self.chosen_component_state.get(),
                                               self.chosen_bias_voltage.get())
        print(filename)
        self.text.insert(index="%d.%d" % (1, 0), chars=filename)
        return (filename)

    def create_test_pow_file(
            self):  # Gets the different entered strings at the set entries to construct a filename for the power sweep measurement
        self.text13.delete(index1="%d.%d" % (1, 0), index2="%d.%s" % (1, 'end'))
        filename = '{}-{}-{}-{}-{}-{}V'.format(self.test_pow_project.get(),
                                               self.test_pow_cell.get(),
                                               self.test_pow_reticule.get(),
                                               self.test_pow_device.get(),
                                               self.chosen_component_state_pow.get(),
                                               self.bias_voltage_pow.get())
        print(filename)
        self.text13.insert(index="%d.%d" % (1, 0), chars=filename)
        return (filename)

    def create_testpullin_file(
            self):  # Gets the different entered strings at the set entries to construct a filename for the pull in measurement
        self.text3.delete(index1="%d.%d" % (1, 0), index2="%d.%s" % (1, 'end'))
        filename = '{}-{}-{}-{}-{}V'.format(self.testpullin_project.get(),
                                            self.testpullin_cell.get(),
                                            self.testpullin_reticule.get(),
                                            self.testpullin_device.get(),
                                            self.entered_ramp_volt.get())
        print(filename)
        self.text3.insert(index="%d.%d" % (1, 0), chars=filename)
        return (filename)

    # ZVA Functions ---------------------------------------------------------------
    def reset_zva(self):  # Reset zva using the IP address at Ressource Page (used in TAB5)
        ip = self.zva_inst.get()
        Rstest.setup_zva_with_rst(ip)

    def set_fstart(self):  # Configure ZVA f_start (used in TAB5)
        fstart = self.fstart.get()
        Rstest.set_fstart(fstart)
        self.error_log(Rstest.zva)

    def set_fstop(self):  # Configure ZVA f_stop (used in TAB5)
        fstop = self.fstop.get()
        Rstest.set_fstop(fstop)
        self.error_log(Rstest.zva)

    def set_nb_points(self):  # Configure ZVA number of points (used in TAB5)
        nb_points = self.nb_points.get()
        Rstest.number_of_points(nb_points)
        self.error_log(Rstest.zva)

    def set_zva(self):  # Configure ZVA f_start/f_stop/nbpoints (used in TAB5)
        self.set_fstart()
        self.set_fstop()
        self.set_nb_points()
        self.text2.delete("1.0", "end")
        self.text2.insert(index="%d.%d" % (0, 0), chars=Rstest.zva_set_output_log())

    def data_acquire(
            self):  # Calls inst_command module function triggered_data_acquisition() to acquire data and create a S3P file
        Rstest.sig_gen.write("TRIG")
        Rstest.triggered_data_acquisition(filename=self.text.get(index1="1.0", index2="end-1c"),
                                          zva_file_dir=r"C:\Users\Public\Documents\Rohde-Schwarz\ZNA\Traces",
                                          pc_file_dir=self.tests3p_dir.get(),
                                          file_format='s3p')
        Rstest.print_error_log()
        self.set_txt()

    def data_acquire_s2p(self):
        Rstest.sig_gen.write("TRIG")
        Rstest.triggered_data_acquisition(filename=self.text.get(index1="1.0", index2="end-1c"),
                                          zva_file_dir=r"C:\Users\Public\Documents\Rohde-Schwarz\ZNA\Traces",
                                          pc_file_dir=self.tests3p_dir.get(),
                                          file_format='s2p')
        Rstest.print_error_log()
        self.set_txt()

    def data_acquire_s1p(self):
        Rstest.sig_gen.write("TRIG")
        Rstest.triggered_data_acquisition(filename=self.text.get(index1="1.0", index2="end-1c"),
                                          zva_file_dir=r"C:\Users\Public\Documents\Rohde-Schwarz\ZNA\Traces",
                                          pc_file_dir=self.tests3p_dir.get(),
                                          file_format='s1p')
        Rstest.print_error_log()
        self.set_txt()

    # signal_Generator Functions -----------------------------------------------------------
    def reset_sig_gen(self):  # Reset signal_Generator using the IP address at Ressource Page (used in TAB4)
        ip = self.sig_gen_inst.get()
        Rstest.setup_sig_gen_ramp_with_rst(ip)

    def acquire_pulldown_data(
            self):  # Calls inst_command module measure_pull_down_voltage() to acquire pull down voltage (used in TAB5)
        try:
            Rstest.measure_pull_down_voltage(filename=self.text3.get(index1="1.0", index2="end-1c"))
            Rstest.print_error_log()
            self.set_txt()
        except:
            print("Error")

    def set_pulse_gen(self):  # Configure signal_Generator bias voltage, pulse width and prf (used in TAB5)
        self.set_Bias_Voltage()
        self.set_PRF()
        self.set_pulse_width()
        self.text2.delete("1.0", "end")
        self.text2.insert(index="%d.%d" % (0, 0), chars=Rstest.sig_gen_set_output_ramp_log())

    def set_pulse_gen_ramp(
            self):  # Calls set_bias_pull_in() & set_ramp_width() to Configure signal_Generator ramp bias voltage and pulse width (used in TAB4)
        self.set_bias_pullin()
        self.set_ramp_width()
        self.text4.delete("1.0", "end")
        self.text4.insert(index="%d.%d" % (0, 0), chars=Rstest.sig_gen_set_output_ramp_log())

    def set_pulse_gen_pulsemode(
            self):  # Calls inst_command module's configuration_sig_gen() to reset the signal_Generator and sends an error log (used in TAB7)
        Rstest.configuration_sig_gen()
        self.text14.delete("1.0", "end")
        self.text14.insert(index="%d.%d" % (0, 0), chars=Rstest.sig_gen_set_output_log())

    def set_Bias_Voltage(
            self):  # Calls inst_command modules's bias_voltage_s3p() function using the voltage provided by entry pull_in_v as an input (used in TAB5)
        bias = self.pullin_v.get()
        Rstest.bias_voltage(bias)
        self.error_log(Rstest.sig_gen)

    def set_bias_pullin(
            self):  # Calls inst_command modules's bias_voltage_s3p() function using the voltage provided by entry pull_in_v as an input (used in TAB4) !!!!FUNCTION IS LIKELY REDUNDANT!!!!
        bias = self.pullin_v_bias.get()
        Rstest.bias_pullin(bias)
        self.error_log(Rstest.sig_gen)

    def set_ramp_width(self):  # Calls inst_command modules's ramp_width(width) to set ramp width
        width = self.ramp_width.get()
        Rstest.ramp_width(width)
        self.error_log(Rstest.sig_gen)

    def set_PRF(self):  # Calls inst_command modules's set_prf(prf) to set set pulse repetition frequency
        PRF = self.pulse_freq.get()
        Rstest.set_PRF(PRF)
        self.error_log(Rstest.sig_gen)

    def set_pulse_width(self):  # Calls inst_command modules's set_pulse_width(width) to set pulse width
        width = self.pulse_width.get()
        Rstest.set_pulse_width(width)
        self.error_log(Rstest.sig_gen)

    def close_ressources(self):  # Calls close_all_resources to close all ressources

        Rstest.close_all_ressources()

    # Plots functions -------------------------------------------------------------
    def trace_pulldown(
            self):  # Measurement function that calls inst_command Module to trigger signal_Generator to figure pull in trace and display the measurement values in the text_file_name_s3p_test boxes(used in TAB6)
        try:
            Rstest.sig_gen.write('TRIG')
            curve_det = Rstest.get_curve(channel=4)
            curve_bias = Rstest.get_curve(channel=2)
            t = curve_det[:, 1]
            rf_detector = -max(3 * curve_det[:, 0] / 0.040) + 3 * curve_det[:, 0] / 0.040
            v_bias = curve_bias[:, 0]
            measurement_values = self.calculate_pullin_out_voltage_measurement(v_bias, curve_det[:, 0])
            plt.figure(num=4)
            number_of_graphs = len(self.ax4.get_lines()[0:])
            self.ax4.plot(v_bias, rf_detector, label='figure n°{}'.format(number_of_graphs))
            self.ax4.set(xlabel='V_bias (V)')
            self.ax4.set(ylabel='Isolation (dB)')
            self.ax4.grid(visible=True)
            self.ax4.legend(fancybox=True, shadow=True)
            self.canvas4.draw()
            self.text5.delete("1.0", "end")
            self.text6.delete("1.0", "end")
            self.text7.delete("1.0", "end")
            self.text8.delete("1.0", "end")
            self.text9.delete("1.0", "end")
            self.text10.delete("1.0", "end")
            self.text11.delete("1.0", "end")
            self.text12.delete("1.0", "end")
            self.text5.insert(index="%d.%d" % (0, 0), chars=measurement_values['Vpullin_plus'])
            self.text6.insert(index="%d.%d" % (0, 0), chars=measurement_values['Vpullin_minus'])
            self.text7.insert(index="%d.%d" % (0, 0), chars=measurement_values['Vpullout_plus'])
            self.text8.insert(index="%d.%d" % (0, 0), chars=measurement_values['Vpullout_minus'])
            self.text9.insert(index="%d.%d" % (0, 0), chars=measurement_values['Isolation_at_pullin_plus'])
            self.text10.insert(index="%d.%d" % (0, 0), chars=measurement_values['Isolation_at_pullout_plus'])
            self.text11.insert(index="%d.%d" % (0, 0), chars=measurement_values['Isolation_at_pullin_minus'])
            self.text12.insert(index="%d.%d" % (0, 0), chars=measurement_values['Isolation_at_pullout_minus'])
        except:
            print("Error in trace pull down function [Line 905]")

    def plot_s3p(self):  # Display function that calls skrf Module to figure s3p files (used in display TAB)
        entered_filename = self.s3p_file_name_combobox.get()
        print(entered_filename + '\n')
        cwd = os.chdir('{}'.format(self.entered_var_s3p.get()))
        self.s_par_network = rf.Network('{}'.format(entered_filename))
        self.s_par_network.frequency.unit = 'GHz'
        self.freq = self.s_par_network.frequency
        spar_dict_s3p = {'S11': [0, 0], 'S12': [0, 1], 'S13': [0, 2],
                         'S21': [1, 0], 'S22': [1, 1], 'S23': [1, 2],
                         'S31': [2, 0], 'S32': [0, 0], 'S33': [2, 2]}
        [m, n] = spar_dict_s3p[self.sparmeter_chosen_s3p.get()]
        plt.figure(num=1)
        self.s_par_network.plot_s_db(m, n)
        self.ax.set_ylim(ymin=self.scale_amplitude_value.get(), ymax=0)
        self.ax.set_xlim(xmin=self.scale_frequency_lower_value.get(), xmax=self.scale_frequency_upper_value.get())
        self.ax.set(ylabel='S{}{} (dB)'.format(m + 1, n + 1))
        self.ax.grid(visible=True)
        self.ax.legend(fancybox=True, shadow=True)
        if not (self.ax.get_lines()[0:] == []):
            cursor = AnnotatedCursor(
                line=self.ax.get_lines()[-1],
                numberformat="{0:.2e} Hz\n{1:.2f} dB",
                dataaxis='x', offset=[10, -40],
                textprops={'color': 'black', 'fontweight': 'book'},
                ax=self.ax,
                useblit=True,
                color='gray',
                linewidth=1, )
            cursor.visible(True)

    def plot_s2p(self):  # Display function that calls skrf Module to figure s2p files (used in display TAB)
        entered_filename = self.s2p_file_name_combobox.get()
        print(entered_filename + '\n')
        cwd = os.chdir('{}'.format(self.entered_var_s2p.get()))
        s_par_network = rf.Network('{}'.format(entered_filename))
        s_par_network.frequency.unit = 'Ghz'
        spar_dict_s2p = {'S11': [0, 0], 'S12': [0, 1],
                         'S21': [1, 0], 'S22': [1, 1], }
        [m, n] = spar_dict_s2p[self.sparmeter_chosen_s2p.get()]
        plt.figure(num=2, tight_layout=True)
        s_par_network.plot_s_db(m, n)
        self.ax2.set_ylim(ymin=self.scale_amplitude_value.get(), ymax=0)
        self.ax2.set_xlim(xmin=self.scale_frequency_lower_value.get(), xmax=self.scale_frequency_upper_value.get())
        self.ax2.set(ylabel='S{}{} (dB)'.format(m + 1, n + 1))
        self.ax2.grid(visible=True)
        self.ax2.legend(fancybox=True, shadow=True)
        if not (self.ax2.get_lines()[0:] == []):
            cursor2 = AnnotatedCursor(
                line=self.ax2.get_lines()[-1],
                numberformat="{0:.2e} Hz\n{1:.2f} dB",
                dataaxis='x', offset=[10, -40],
                textprops={'color': 'black', 'fontweight': 'book'},
                ax=self.ax2,
                useblit=True,
                color='gray',
                linewidth=1, )
            cursor2.visible(True)

    def plot_vpullin(self):  # Display function to figure Isolation vs pull in voltage files (used in display TAB)
        f = self.txt_file_name_combobox.get()
        cwd = os.chdir('{}'.format(self.pullin_dir_name.get()))
        with open(f, newline='') as input_file:
            data_np = np.loadtxt(f, delimiter=',', unpack=True, skiprows=1)
            v_bias = data_np[:, 0].copy()
            print(v_bias, end='\n')
            v_logamp = data_np[:, 1].copy()
            max_iso = np.max(3 * v_logamp / 0.040)
            min_iso = np.min(3 * v_logamp / 0.040) - 3
            max_vbias = np.max(v_bias)
            iso = 3 * v_logamp / 0.040 - max_iso
            plt.figure(num=3)
            self.ax3.plot(v_bias, iso, label="{}".format(f)[:-4])  # removesuffixe non fonctionnel dans python 3.6
            self.ax3.set_ylim(ymin=self.scale_isolation_value.get(), ymax=0)
            self.ax3.set_xlim(xmin=-self.scale_voltage_value.get(), xmax=self.scale_voltage_value.get())
            self.ax3.set(ylabel='Isolation (dB)')
            self.ax3.grid(visible=True)
            self.ax3.legend(fancybox=True, shadow=True)
            self.canvas3.draw()
            if not (self.ax3.get_lines()[0:] == []):
                cursor3 = AnnotatedCursor(
                    line=self.ax3.get_lines()[-1],
                    numberformat="{0:.2f} V\n{1:.2f} dB",
                    dataaxis='x', offset=[10, -40],
                    textprops={'color': 'black', 'fontweight': 'book'},
                    ax=self.ax3,
                    useblit=True,
                    color='gray',
                    linewidth=1, )
                cursor3.visible(True)

    def calculate_pullin_out_voltage(
            self):  # Display function to calculate pull in/out voltages and associated Isolation values (used in display TAB)
        self.textscroll.delete('1.0', tk.END)
        f = self.txt_file_name_combobox.get()
        with open(f, newline='') as input_file:
            data_np = np.loadtxt(f, delimiter=',', unpack=True, skiprows=1)
            v_bias = data_np[:, 0].copy()
            v_logamp = data_np[:, 1].copy()
            # Acquiring the indexes that correspond to both positive and negative bias triangles
            # the indexes are extracted by slicing voltages (for positive bias) > 2V and <-2 V (for negative bias)
            positive_bias = np.extract((v_bias > 2), v_bias)
            negative_bias = np.extract((v_bias < -2), v_bias)

            # Position of the first positive bias index along v_bias array
            first_index_pos = np.where(v_bias == positive_bias[0])[0]

            # Position of the first negative bias index along v_bias array
            first_index_neg = np.where(v_bias == negative_bias[0])[0]
            # Position of the last negative bias index along v_bias array
            last_index_neg = np.where(v_bias == negative_bias[-1])[0]
            # Calculating the max and min indexes in both casses
            max_positive_bias_index = np.argmax(positive_bias)
            min_positive_bias_index = 0
            max_negative_bias_index = 0
            min_negative_bias_index = np.argmin(negative_bias)

            # Creating the ascent and descent portion of the graph for v_bias and v_log converted to normalized isolation
            positive_ascent = positive_bias[0:max_positive_bias_index]
            positive_descent = positive_bias[max_positive_bias_index:len(positive_bias)]

            # Calculating normalized isolation factor
            normalize_iso = np.max(3 * v_logamp[first_index_pos[0]:max_positive_bias_index] / 0.040)

            iso_ascent = 3 * v_logamp[
                             first_index_pos[0]:first_index_pos[0] + max_positive_bias_index] / 0.040 - normalize_iso
            iso_max_ascent = np.min(iso_ascent)

            iso_descent = 3 * v_logamp[first_index_pos[0] + max_positive_bias_index:first_index_pos[0] + len(
                positive_bias)] / 0.040 - normalize_iso
            iso_min_descent = np.min(iso_descent)
            # ==============================================================================
            # Calculation Vpull in as isolation passing below 90% max isolation in dB mark
            # Calculation Vpull out as isolation passing above 90% max isolation in dB mark
            pullin_index_pos = int(np.where(iso_ascent <= 0.9 * iso_max_ascent)[0][0])
            Vpullin = positive_bias[pullin_index_pos]

            tenpercent_iso = 0.1 * iso_min_descent
            ninetypercent_iso = 0.9 * iso_max_ascent

            pullout_index_pos = int(np.where(iso_descent >= 0.1 * iso_min_descent)[0][0])
            Vpullout = positive_bias[max_positive_bias_index + pullout_index_pos]

            # ==============================================================================
            # Creating the ascent and descent portion of the graph for v_bias and v_log converted to normalized isolation
            negative_descent = negative_bias[0:min_negative_bias_index]
            negative_ascent = negative_bias[min_negative_bias_index:len(negative_bias)]

            # Calculating normalized isolation factor
            normalized_iso_minus = np.max(3 * v_logamp[first_index_neg[0]:first_index_neg[
                                                                              0] + min_negative_bias_index] / 0.040)  # This is extracted from the detector V/dB characteristics

            iso_descent_minus = 3 * v_logamp[first_index_neg[0]:first_index_neg[
                                                                    0] + min_negative_bias_index] / 0.040 - normalized_iso_minus
            iso_min_descent_minus = np.min(iso_descent_minus)

            iso_ascent_minus = 3 * v_logamp[first_index_neg[0] + min_negative_bias_index:last_index_neg[
                0]] / 0.040 - normalized_iso_minus
            iso_min_ascent = np.min(iso_ascent_minus)

            # Calculation Vpull in negative as isolation passing below 90% max isolation in dB mark (downwards)
            # Calculation Vpull out negative as isolation passing above 10% off isolation in dB mark (upwards)
            pullin_index_minus = int(np.where(iso_descent_minus <= 0.9 * iso_min_descent)[0][0])
            Vpullin_minus = negative_bias[pullin_index_minus]

            tenpercent_iso_ascent = 0.1 * iso_min_ascent
            ninetypercent_iso_descent = 0.9 * iso_min_descent

            pullout_index_minus = int(np.where(iso_ascent_minus >= 0.1 * iso_min_ascent)[0][0])
            Vpullout_minus = negative_bias[min_negative_bias_index + pullout_index_minus]
            # print('Vpullin = {} | Isolation measured = {}\nVpullout = {} | Isolation measured = {} \nVpullin_minus = {} | Isolation measured = {}\nVpullout_minus = {} | Isolation measured = {} \n'.format(Vpullin, ninetypercent_iso, Vpullout, tenpercent_iso, Vpullin_minus, ninetypercent_iso_descent, Vpullout_minus, tenpercent_iso_ascent))

            self.textscroll.insert(index="%d.%d" % (1, 0),
                                   chars='Isolation_at_pullout_minus = {} dB \n'.format(tenpercent_iso_ascent))
            self.textscroll.insert(index="%d.%d" % (1, 0), chars='Vpullout_minus = {} V | \t'.format(Vpullout_minus))

            self.textscroll.insert(index="%d.%d" % (1, 0),
                                   chars='Isolation_at_pullin_minus = {} dB \n'.format(ninetypercent_iso_descent))
            self.textscroll.insert(index="%d.%d" % (1, 0), chars='Vpullin_minus = {} V | \t'.format(Vpullin_minus))

            self.textscroll.insert(index="%d.%d" % (1, 0),
                                   chars='Isolation_at_pullout_plus = {} dB  \n'.format(tenpercent_iso))
            self.textscroll.insert(index="%d.%d" % (1, 0), chars='Vpullout_plus = {} V | \t'.format(Vpullout))

            self.textscroll.insert(index="%d.%d" % (1, 0),
                                   chars='Isolation_at_pullin_plus = {} dB \n'.format(ninetypercent_iso))
            self.textscroll.insert(index="%d.%d" % (1, 0), chars='Vpullin_plus = {} V | \t'.format(Vpullin))

            pull_dict = {'Vpullin_plus': Vpullin, 'Vpullout_plus': Vpullout,
                         'Isolation_at_pullin_plus': ninetypercent_iso, 'Isolation_at_pullout_plus': tenpercent_iso,
                         'Vpullin_minus': Vpullin_minus, 'Vpullout_minus': Vpullout_minus,
                         'Isolation_at_pullin_minus': ninetypercent_iso_descent,
                         'Isolation_at_pullout_minus': tenpercent_iso_ascent}
            return (pull_dict)

    def delete_axs_s3p(self):  # Delete last drawn line in s3p display tab (in ax_s3p)
        list_graph_ax = self.ax.lines[-1]
        list_graph_ax.remove()
        self.ax.legend(fancybox=True)
        self.canvas.draw()

    def delete_axs_s2p(self):  # Delete last drawn line in s2p display tab (in ax_s2p)
        list_graph_ax2 = self.ax2.lines[-1]
        list_graph_ax2.remove()
        self.ax2.legend(fancybox=True)
        self.canvas2.draw()

    def delete_axs_vpullin(self):  # Delete last drawn line in pull in graph display tab (in ax_pull_in)
        try:
            list_graph_ax3 = self.ax3.lines[-1]
            list_graph_ax3.remove()
            self.ax3.legend(fancybox=True)
            self.canvas3.draw()
        except:
            print("No more graphs to delete")

    def update_ylim(self):
        value = self.scale_amplitude_value.get()
        self.ax.set_ylim(ymin=0, ymax=value)
        self.plot_s3p()
        self.ax.grid(visible=True)

    def update_xlim(self):
        value = self.scale_frequency_upper_value.get()
        value2 = self.scale_frequency_lower_value.get()
        self.plot_s3p()
        self.ax.set_xlim(xmin=value2, xmax=value)
        self.ax.grid(visible=True)

    def add_slider(self, frame, _from, to, name, variable, step):
        slider = tk.Scale(master=frame, from_=_from, to=to, orient=tk.HORIZONTAL, label=name, length=400, digits=2,
                          relief=tk.GROOVE, border=3, sliderrelief=tk.RIDGE, tickinterval=step, variable=variable,
                          font=('Bahnschrift Light', 10))
        # slider.pack()
        return (slider)

    def set_txt(self):  # (used in TAB5)
        # self.text_snp_debug.delete(index1="%d.%d" % (1, 0), index2="%d.%s" % (1, 'end'))
        self.text2.delete("1.0", "end")
        self.text4.delete("1.0", "end")
        error_logs = Rstest.print_error_log()
        self.text2.insert(index="%d.%d" % (0, 0), chars=error_logs)
        self.text4.insert(index="%d.%d" % (0, 0), chars=error_logs)

    def error_log(self, ressource):
        error_log_ressource = ressource.query('SYSTem:ERRor?')
        error_string_ressource = error_log_ressource.split(",")[1]
        ressource_name = ressource.query('*IDN?').split(",")[:2]
        error_output = '{} ERROR LOG: {}\n'.format(ressource_name, error_string_ressource)
        self.text2.delete("1.0", "end")
        self.text2.insert(index="%d.%d" % (0, 0), chars=error_output)
        self.text4.delete("1.0", "end")
        self.text4.insert(index="%d.%d" % (0, 0), chars=error_output)
        return (error_output)

    def calculate_pullin_out_voltage_measurement(self, v_bias,
                                                 v_logamp):  # same function as in display implemented in measurement
        self.text4.delete('1.0', tk.END)
        list_graph_ax4 = self.ax4.lines[:]
        if not (list_graph_ax4 == []):
            list_graph_ax4[-1].remove()
        self.ax4.legend(fancybox=True)
        self.canvas2.draw()

        # Acquiring the indexes that correspond to both positive and negative bias triangles
        # the indexes are extracted by slicing voltages (for positive bias) > 2V and <-2 V (for negative bias)
        positive_bias = np.extract((v_bias > 2), v_bias)
        negative_bias = np.extract((v_bias < -2), v_bias)

        # Position of the first positive bias index along v_bias array
        first_index_pos = np.where(v_bias == positive_bias[0])[0]

        # Position of the first negative bias index along v_bias array
        first_index_neg = np.where(v_bias == negative_bias[0])[0]
        # Position of the last negative bias index along v_bias array
        last_index_neg = np.where(v_bias == negative_bias[-1])[0]
        # Calculating the max and min indexes in both casses
        max_positive_bias_index = np.argmax(positive_bias)
        min_positive_bias_index = 0
        max_negative_bias_index = 0
        min_negative_bias_index = np.argmin(negative_bias)

        # Creating the ascent and descent portion of the graph for v_bias and v_log converted to normalized isolation
        positive_ascent = positive_bias[0:max_positive_bias_index]
        positive_descent = positive_bias[max_positive_bias_index:len(positive_bias)]

        # Calculating normalized isolation factor
        normalize_iso = np.max(3 * v_logamp[first_index_pos[0]:max_positive_bias_index] / 0.040)

        iso_ascent = 3 * v_logamp[
                         first_index_pos[0]:first_index_pos[0] + max_positive_bias_index] / 0.040 - normalize_iso
        iso_max_ascent = np.min(iso_ascent)

        iso_descent = 3 * v_logamp[first_index_pos[0] + max_positive_bias_index:first_index_pos[0] + len(
            positive_bias)] / 0.040 - normalize_iso
        iso_min_descent = np.min(iso_descent)
        # ==============================================================================
        # Calculation Vpull in as isolation passing below 90% max isolation in dB mark
        # Calculation Vpull out as isolation passing above 90% max isolation in dB mark
        pullin_index_pos = int(np.where(iso_ascent <= 0.9 * iso_max_ascent)[0][0])
        Vpullin = round(positive_bias[pullin_index_pos], ndigits=2)

        tenpercent_iso = round(0.1 * iso_min_descent, ndigits=2)
        ninetypercent_iso = round(0.9 * iso_max_ascent, ndigits=2)

        pullout_index_pos = int(np.where(iso_descent >= 0.1 * iso_min_descent)[0][0])
        Vpullout = round(positive_bias[max_positive_bias_index + pullout_index_pos], ndigits=2)

        # ==============================================================================
        # Creating the ascent and descent portion of the graph for v_bias and v_log converted to normalized isolation
        negative_descent = negative_bias[0:min_negative_bias_index]
        negative_ascent = negative_bias[min_negative_bias_index:len(negative_bias)]

        # Calculating normalized isolation factor
        normalized_iso_minus = np.max(3 * v_logamp[first_index_neg[0]:first_index_neg[
                                                                          0] + min_negative_bias_index] / 0.040)  # This is extracted from the detector V/dB characteristics

        iso_descent_minus = 3 * v_logamp[first_index_neg[0]:first_index_neg[
                                                                0] + min_negative_bias_index] / 0.040 - normalized_iso_minus
        iso_min_descent_minus = np.min(iso_descent_minus)

        iso_ascent_minus = 3 * v_logamp[first_index_neg[0] + min_negative_bias_index:last_index_neg[
            0]] / 0.040 - normalized_iso_minus
        iso_min_ascent = np.min(iso_ascent_minus)

        # Calculation Vpull in negative as isolation passing below 90% max isolation in dB mark (downwards)
        # Calculation Vpull out negative as isolation passing above 10% off isolation in dB mark (upwards)
        pullin_index_minus = int(np.where(iso_descent_minus <= 0.9 * iso_min_descent)[0][0])
        Vpullin_minus = round(negative_bias[pullin_index_minus], ndigits=2)

        tenpercent_iso_ascent = round(0.1 * iso_min_ascent, ndigits=2)
        ninetypercent_iso_descent = round(0.9 * iso_min_descent, ndigits=2)

        pullout_index_minus = int(np.where(iso_ascent_minus >= 0.1 * iso_min_ascent)[0][0])
        Vpullout_minus = round(negative_bias[min_negative_bias_index + pullout_index_minus], ndigits=2)
        # print('Vpullin = {} | Isolation measured = {}\nVpullout = {} | Isolation measured = {} \nVpullin_minus = {} | Isolation measured = {}\nVpullout_minus = {} | Isolation measured = {} \n'.format(Vpullin, ninetypercent_iso, Vpullout, tenpercent_iso, Vpullin_minus, ninetypercent_iso_descent, Vpullout_minus, tenpercent_iso_ascent))

        self.text4.insert(index="%d.%d" % (1, 0),
                          chars='Isolation_at_pullout_minus = {} dB \n'.format(tenpercent_iso_ascent))
        self.text4.insert(index="%d.%d" % (1, 0), chars='Vpullout_minus = {} V  \n'.format(Vpullout_minus))

        self.text4.insert(index="%d.%d" % (1, 0),
                          chars='Isolation_at_pullin_minus = {} dB \n'.format(ninetypercent_iso_descent))
        self.text4.insert(index="%d.%d" % (1, 0), chars='Vpullin_minus = {} V  \n'.format(Vpullin_minus))

        self.text4.insert(index="%d.%d" % (1, 0), chars='Isolation_at_pullout_plus = {} dB  \n'.format(tenpercent_iso))
        self.text4.insert(index="%d.%d" % (1, 0), chars='Vpullout_plus = {} V  \n'.format(Vpullout))

        self.text4.insert(index="%d.%d" % (1, 0), chars='Isolation_at_pullin_plus = {} dB \n'.format(ninetypercent_iso))
        self.text4.insert(index="%d.%d" % (1, 0), chars='Vpullin_plus = {} V  \n'.format(Vpullin))

        pull_dict = {'Vpullin_plus': Vpullin, 'Vpullout_plus': Vpullout, 'Isolation_at_pullin_plus': ninetypercent_iso,
                     'Isolation_at_pullout_plus': tenpercent_iso,
                     'Vpullin_minus': Vpullin_minus, 'Vpullout_minus': Vpullout_minus,
                     'Isolation_at_pullin_minus': ninetypercent_iso_descent,
                     'Isolation_at_pullout_minus': tenpercent_iso_ascent}
        return (pull_dict)

    def cycling_sequence(self, number_of_cycles, number_of_pulses_in_wf=1000):

        number_of_triggered_acquisitions = int(number_of_cycles / number_of_pulses_in_wf)
        pullin = np.empty(1, dtype=float)
        pullout = np.empty(1, dtype=float)
        isolation = np.empty(1, dtype=float)
        sw_time = np.empty(1, dtype=float)

        for n in range(start=0, stop=number_of_triggered_acquisitions, step=1):
            Ch_4_detector = Rstest.get_curve_cycling(channel=4)
            Ch_2_bias = Rstest.get_curve_cycling(channel=2)
            data = Rstest.extract_data(rf_detector_channel=Ch_4_detector, v_bias_channel=Ch_2_bias)
            switch_time = Rstest.switching_time()

            pullin.append(data['Vpullin'])
            pullout.append(data['Vpullout'])
            isolation.append(data['_100percent_iso'])
            sw_time.append(switch_time)
            cycling_data = np.stack((pullin, pullout, isolation, switch_time), axis=1)

        np.savetxt(fname='test.txt', X=cycling_data, delimiter='\n', newline='\n',
                   header='RF MEMS Reference = test\nCycling_data', footer='END')
        print('Cycle is Finished')

    def send_trig(self):
        Rstest.trigger_measurement_zva()
        self.error_log(Rstest.sig_gen)


# Main ------------------------------------------------------------------------
app = Window()
fonts = list(font.families())
app.mainloop()
# Main ------------------------------------------------------------------------
