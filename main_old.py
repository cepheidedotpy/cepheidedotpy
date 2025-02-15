# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 14:31:59 2022
This Tkinter app can get S3P & S2P files in a directory and display them
after selection
@author: T0188303
_version :10
"""
import os
import time
import tkinter as tk
import tkinter.ttk
from tkinter import Menu
from tkinter import Toplevel
# from tkinter import font
from tkinter import scrolledtext
from tkinter import ttk
from tkinter.ttk import Notebook
from typing import Optional

# Implement the default Matplotlib key bindings.
import matplotlib.pyplot as plt
import numpy as np
import skrf as rf
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)  # , NavigationToolbar2Tk)
from matplotlib.figure import Figure

import dir_and_var_declaration
# ==============================================================================
# Imports#%matplotlib inline
# ==============================================================================
import scripts_and_functions as scripts_and_functions

# %matplotlib inline

""" This GUI is used to display S Parameters inside a Folder chosen by the user."""
_version = '10'

# This code is dated to 15/02/24

# ==============================================================================
# Globals
# ==============================================================================
tab_pad_x = 5
tab_pad_y = 5
plt.style.use('default')
plt.rcParams["legend.fontsize"] = 10
plt.rcParams["axes.labelsize"] = 10
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 12


def add_tab(tab_name: str, notebook: ttk.Notebook, col: int, row: int) -> ttk.LabelFrame:
    """
    Adds a tab to a notebook at the defined column and row and returns the tab instance.

    Parameters:
    tab_name (str): Name of the tab.
    notebook (ttk.Notebook): Notebook in which the tab is to be created.
    col (int): Column position within the notebook.
    row (int): Row position within the notebook.

    Returns:
    ttk.Frame: The created tab (frame) instance.
    """
    # Create a new frame (tab) with 'ridge' relief and a border width of 10.
    tab_inst = ttk.LabelFrame(notebook, relief='ridge', borderwidth=10)

    # Add the newly created tab to the notebook with the given tab name.
    notebook.add(tab_inst, text='{}'.format(tab_name))

    # Position the notebook at the specified column and row in the parent widget.
    notebook.grid(column=col, row=row)

    # Return the created tab (frame) instance.
    return tab_inst


def add_button(tab: ttk.LabelFrame, button_name: str, command, col: int, row: int) -> ttk.Button:
    """
    Adds a button to a specified tab (LabelFrame) with given name, command, column, and row.
    The button changes color for 500 milliseconds when pressed.

    Parameters:
    tab (ttk.LabelFrame): The parent LabelFrame where the button is to be added.
    button_name (str): The text to be displayed on the button.
    command (callable): The function to be executed when the button is pressed.
    col (int): The column position within the LabelFrame.
    row (int): The row position within the LabelFrame.

    Returns:
    ttk.Button: The created Button widget.
    """

    def on_press():
        # Change the button color to a highlight color when pressed.
        action.configure(style='Pressed.TButton')

        # Call the original command.
        command()

        # Schedule the color to revert back to the original after 500 milliseconds.
        action.after(500, lambda: action.configure(style='TButton'))

    # Create a Button widget with the specified text and additional configurations.
    action = ttk.Button(
        tab,  # The parent LabelFrame where the button is added.
        text=button_name,  # The text displayed on the button.
        command=on_press,  # The function to be executed on button press.
        width=len(button_name),  # Set the button width to the length of the button name.
        padding=1  # Set padding around the button.
    )

    # Enable the button.
    action.configure(state='enabled')

    # Place the Button widget at the specified column and row in the LabelFrame.
    action.grid(column=col, row=row)

    # Define a new style for the pressed button.
    style = ttk.Style()
    style.configure('Pressed.TButton', background='blue')  # Change 'blue' to any color you prefer.

    # Return the created Button widget.
    return action


def update_button(button: ttk.Button) -> ttk.Button:
    """
    Changes the text on a button to 'Updated' for 500 milliseconds when the button is pressed,
    then changes it back to 'Update files'.

    Parameters:
    button (ttk.Button): The button whose text is to be changed.

    Returns:
    ttk.Button: The same button with updated behavior.
    """

    def update_text_back():
        # Change the button text back to 'Update files' after 500 milliseconds.
        button.configure(text='Update files')

    # Change the button text to 'Updated' immediately.
    button.configure(text='Updated')
    # Schedule the text to change back to 'Update files' after 500 milliseconds.
    button.after(500, update_text_back)

    return button


def add_label(tab: ttk.LabelFrame, label_name: str, col: int, row: int) -> ttk.Label:
    """
    Adds a Label widget to a specified tab (LabelFrame) at the given column and row.

    Parameters:
    tab (ttk.LabelFrame): The parent LabelFrame where the Label is to be added.
    label_name (str): The text to be displayed on the Label.
    col (int): The column position within the LabelFrame.
    row (int): The row position within the LabelFrame.

    Returns:
    ttk.Label: The created Label widget.
    """
    # Create a Label widget with the specified text.
    label = ttk.Label(tab, text=label_name)

    # Place the Label widget at the specified column and row in the LabelFrame.
    label.grid(column=col, row=row)

    # Return the created Label widget.
    return label


def add_scrolled_text(tab: ttk.LabelFrame, scrolled_width: int, scrolled_height: int) -> scrolledtext.ScrolledText:
    """
    Adds a ScrolledText widget to a specified tab (LabelFrame) with given width and height.

    Parameters:
    tab (ttk.LabelFrame): The parent LabelFrame where the ScrolledText is to be added.
    scrolled_width (int): The width of the ScrolledText widget.
    scrolled_height (int): The height of the ScrolledText widget.

    Returns:
    scrolledtext.ScrolledText: The created ScrolledText widget.
    """
    # Create a ScrolledText widget with the specified width, height, and other configurations.
    scroll = scrolledtext.ScrolledText(
        tab,  # The parent LabelFrame where the ScrolledText is added.
        width=scrolled_width,  # Width of the ScrolledText widget.
        height=scrolled_height,  # Height of the ScrolledText widget.
        wrap=tk.WORD,  # Wrap text by words.
        border=2,  # Set border width of the widget.
        relief=tk.SUNKEN,  # Sunken relief appearance.
        pady=0  # Padding on the y-axis.
    )

    # Pack the ScrolledText widget to the top of the parent LabelFrame.
    scroll.pack(side='top')

    # Return the created ScrolledText widget.
    return scroll


def add_label_frame(tab: ttk.LabelFrame, frame_name: str, col: int, row: int, row_span: int = 1) -> ttk.LabelFrame:
    """
    Adds a LabelFrame to a specified tab (LabelFrame) with given name, column, row, and row span.
    The LabelFrame is created with a 'ridge' relief and the label anchor set to North West.

    Parameters:
    tab (ttk.LabelFrame): The parent LabelFrame where the new LabelFrame is to be added.
    frame_name (str): The text to be displayed on the LabelFrame.
    col (int): The column position within the parent LabelFrame.
    row (int): The row position within the parent LabelFrame.
    row_span (int, optional): The number of rows the LabelFrame should span. Default is 1.

    Returns:
    ttk.LabelFrame: The created LabelFrame widget.
    """
    # Create a LabelFrame widget with the specified text, border width, relief, and label anchor.
    frame = ttk.LabelFrame(
        tab,  # The parent LabelFrame where the new LabelFrame is added.
        text=frame_name,  # The text displayed on the LabelFrame.
        borderwidth=5,  # Set the border width of the LabelFrame.
        relief=tk.RIDGE,  # Set the relief style to 'ridge'.
        labelanchor='nw'  # Set the label anchor to North West.
    )

    # Place the LabelFrame widget at the specified column and row in the parent LabelFrame,
    # making it span the specified number of rows and stick to all sides of the cell.
    frame.grid(
        column=col,  # The column position within the parent LabelFrame.
        row=row,  # The row position within the parent LabelFrame.
        sticky=tk.N + tk.S + tk.W + tk.E,  # Make the LabelFrame stick to all sides of the cell.
        rowspan=row_span  # Set the number of rows the LabelFrame should span.
    )

    # Return the created LabelFrame widget.
    return frame


def extension_detector(file: str) -> tuple:
    """
    Separates the file name and extension from a given file path.

    Parameters:
    file (str): The file path or file name to be processed.

    Returns:
    tuple: A tuple containing the file extension and the file name without the extension.
    """
    # Separate the file name and extension using os.path.splitext.
    file, extension = os.path.splitext(file)

    # Return the extension and the file name.
    return extension, file


def filetypes_dir(path: str) -> tuple:
    """
    Separates different file types in the specified directory and returns tuples of s3p, s2p, and txt files.

    Parameters:
    path (str): The directory path to search for files.

    Returns:
    tuple: Three tuples containing s3p, s2p, and txt files, respectively.
    """
    if not path:
        return 'empty', 'empty'

    # List all files in the directory
    file_list = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    # Initialize lists to store different types of files
    txt_files = []
    s3p_files = []
    s2p_files = []

    # Loop through each file and classify by extension
    for file in file_list:
        extension, _ = extension_detector(file)
        if extension == '.txt':
            txt_files.append(file)
        elif extension == '.s3p':
            s3p_files.append(file)
        elif extension == '.s2p':
            s2p_files.append(file)

    # Convert lists to tuples and return
    return tuple(s3p_files), tuple(s2p_files), tuple(txt_files)


def add_entry(tab: ttk.LabelFrame, text_var: tk.StringVar | tk.DoubleVar, width: int, col: int, row: int) -> ttk.Entry:
    """
    Adds an Entry widget to a specified tab (LabelFrame) with given text variable, width, column, and row.

    Parameters:
    tab (ttk.LabelFrame): The parent LabelFrame where the Entry is to be added.
    text_var (tk.StringVar or tk.DoubleVar): The text variable associated with the Entry widget.
    width (int): The width of the Entry widget.
    col (int): The column position within the parent LabelFrame.
    row (int): The row position within the parent LabelFrame.

    Returns:
    ttk.Entry: The created Entry widget.
    """
    # Create an Entry widget with the specified width, text variable, validation, and font.
    entered = ttk.Entry(
        tab,  # The parent LabelFrame where the Entry is added.
        width=width,  # The width of the Entry widget.
        textvariable=text_var,  # The text variable associated with the Entry widget.
        validate='focus',  # Validation on focus.
        font=('Bahnschrift Light', 10)  # Font style and size.
    )

    # Place the Entry widget at the specified column and row in the parent LabelFrame,
    # and make it stretch horizontally.
    entered.grid(
        column=col,  # The column position within the parent LabelFrame.
        row=row,  # The row position within the parent LabelFrame.
        sticky="WE"  # Make the Entry widget stretch horizontally.
    )

    # Return the created Entry widget.
    return entered


def add_combobox(tab: ttk.LabelFrame, text: tk.StringVar, col: int, row: int, width: int) -> ttk.Combobox:
    """
    Adds a Combobox widget to a specified tab (LabelFrame) with given text variable, column, row, and width.

    Parameters:
    tab (ttk.LabelFrame): The parent LabelFrame where the Combobox is to be added.
    text (tk.StringVar): The text variable associated with the Combobox widget.
    col (int): The column position within the parent LabelFrame.
    row (int): The row position within the parent LabelFrame.
    width (int): The width of the Combobox widget.

    Returns:
    ttk.Combobox: The created Combobox widget.
    """
    # Create a Combobox widget with the specified text variable, state, values, validation, width, height, and font.
    combobox = ttk.Combobox(
        tab,  # The parent LabelFrame where the Combobox is added.
        textvariable=text,  # The text variable associated with the Combobox widget.
        state='readonly',  # Make the Combobox read-only.
        values=[''],  # Initialize the Combobox with an empty list of values.
        validate='focus',  # Validation on focus.
        width=width,  # The width of the Combobox widget.
        font=('Bahnschrift Light', 10)  # Font style and size.
    )

    # Place the Combobox widget at the specified column and row in the parent LabelFrame.
    combobox.grid(
        column=col,  # The column position within the parent LabelFrame.
        row=row  # The row position within the parent LabelFrame.
    )

    # Return the created Combobox widget.
    return combobox


def close_resources():  # Calls close_all_resources to close all resources
    scripts_and_functions.close_all_resources()


def call_s3p_config():
    """
    Calls the load_config function to load the s3p configuration file to the instrument.
    Uses predefined file paths from the dir_and_var_declaration module.
    """
    # Call the load_config function with predefined file paths for the s3p configuration.
    scripts_and_functions.load_config(
        pc_file=dir_and_var_declaration.pc_file_s3p,  # Path to the s3p configuration file on the PC.
        inst_file=dir_and_var_declaration.instrument_file_ZVA67  # Path to the instrument file location.
    )


def call_s2p_config():
    """
    Calls the load_config function to load the s2p configuration file to the instrument.
    Uses predefined file paths from the dir_and_var_declaration module.
    """
    # Call the load_config function with predefined file paths for the s2p configuration.
    scripts_and_functions.load_config(
        pc_file=dir_and_var_declaration.pc_file_s2p,  # Path to the s2p configuration file on the PC.
        inst_file=dir_and_var_declaration.instrument_file_ZVA67  # Path to the instrument file location.
    )


def call_s1p_config():
    """
    Calls the load_config function to load the s1p configuration file to the instrument.
    Uses predefined file paths from the dir_and_var_declaration module.
    """
    # Call the load_config function with predefined file paths for the s1p configuration.
    scripts_and_functions.load_config(
        pc_file=dir_and_var_declaration.pc_file_s1p,  # Path to the s1p configuration file on the PC.
        inst_file=dir_and_var_declaration.instrument_file_ZVA67  # Path to the instrument file location.
    )


def update_entries(directory: str, combobox: ttk.Combobox, filetype: str) -> ttk.Combobox:
    """
    Updates the values of a Combobox based on the specified file type from the given directory.

    Parameters:
    directory (str): The directory path to search for files.
    combobox (ttk.Combobox): The Combobox widget to update with file names.
    filetype (str): The file type to filter for updating the Combobox values.

    Returns:
    ttk.Combobox: The updated Combobox widget.
    """
    # Get the files in the directory classified by their extensions.
    files = filetypes_dir(directory)

    # Update the Combobox values based on the specified file type.
    if filetype == '.s2p':
        combobox['values'] = files[1]  # Update with s2p files.
    elif filetype == '.s3p':
        combobox['values'] = files[0]  # Update with s3p files.
    elif filetype == '.txt':
        combobox['values'] = files[2]  # Update with txt files.

    # Return the updated Combobox widget.
    return combobox


def create_canvas(figure: plt.Figure, frame: ttk.LabelFrame, toolbar: Optional[bool] = True) -> FigureCanvasTkAgg:
    """
    Creates display Canvas in the specified frame, and optionally adds a toolbar.

    Parameters:
    figure (plt.Figure): The matplotlib figure to be displayed on the canvas.
    frame (ttk.Frame): The parent frame where the canvas is to be added.
    toolbar (bool, optional): Whether to add a navigation toolbar. Default is True.

    Returns:
    FigureCanvasTkAgg: The created canvas with the matplotlib figure.
    """
    # Create a FigureCanvasTkAgg widget with the specified figure and parent frame.
    canvas = FigureCanvasTkAgg(figure, master=frame)

    # Pack the canvas widget with specified padding.
    canvas.get_tk_widget().pack(ipady=2, ipadx=2)

    # Optionally add a navigation toolbar.
    if toolbar:
        NavigationToolbar2Tk(canvas=canvas, window=frame)

    # Return the created canvas widget.
    return canvas


def file_name_creation(data_list: list, text: tkinter.Text, end_characters: str = '') -> str:
    """
    Creates a filename by joining elements of a data list with hyphens and appending end characters.
    Updates a given text widget with the created filename and prints it.

    Parameters:
    data_list (list): List of strings to be joined into a filename.
    text (tkinter.Text): Text widget to be updated with the created filename.
    end_characters (str, optional): Characters to be appended at the end of the filename. Default is an empty string.

    Returns:
    str: The created filename.
    """
    # Clear the current content of the text widget.
    text.delete(index1="1.0", index2="1.end")

    # Create the filename by joining elements of the data list with hyphens and appending end characters.
    filename = '-'.join(data_list) + end_characters

    # Insert the created filename into the text widget at the beginning.
    text.insert(index="1.0", chars=filename)

    # Print the created filename.
    print(filename)

    # Return the created filename.
    return filename


def add_slider(frame, _from, to, name, variable, step):
    slider = tk.Scale(master=frame, from_=_from, to=to, orient=tk.HORIZONTAL, label=name, length=400, digits=2,
                      relief=tk.GROOVE, border=3, sliderrelief=tk.RIDGE, tickinterval=step, variable=variable,
                      font=('Bahnschrift Light', 10))
    # slider.pack()
    return slider


class Window(tk.Tk, Toplevel):
    """
    Main application class for handling SNP file display and acquisition The app controls VNAs ZVA50 & ZVA67
    the powermeter A-33521B, the RF generator RS SMB100a and oscilloscope DPO DPO5054

    This class inherits from tk.Tk to provide a main application window.
    It initializes the GUI components and binds the necessary event handlers.
    """
    tabControl: Notebook
    fig_cycling: Figure
    fig_pull_in_meas: Figure
    fig_snp_meas: Figure
    fig_s2p: Figure
    fig_s3p: Figure
    fig_pull_in: Figure

    def __init__(self, master=None):
        tk.Tk.__init__(self, master)
        s = ttk.Style()
        # s.theme_use('default')
        s.configure(style='.', font=('Bahnschrift Light', 10))
        self.title(f"SUMMIT 11K Machine Interface v{_version}")
        self.menubar()
        self.resizable(width=True, height=True)
        self.tabControl = ttk.Notebook(self)  # Create Tab Control

        # figure that contains S3P parameters for data display
        self.fig_s3p = plt.figure(num=1, dpi=100, tight_layout=True, figsize=(13, 4.1), frameon=True)
        self.ax_s3p = self.fig_s3p.add_subplot(1, 1, 1)
        self.ax_s3p.grid()

        # figure that contains S2P parameters for data display
        self.fig_s2p = plt.figure(num=2, dpi=100, tight_layout=True, figsize=(13, 4.1), frameon=True)
        self.ax_s2p = self.fig_s2p.add_subplot(1, 1, 1)
        self.ax_s2p.grid()

        # figure that contains pull-in plots for data display
        self.fig_pull_in = plt.figure(num=3, dpi=100, tight_layout=True, figsize=(13, 3.5), frameon=True)
        self.ax_pull_in = self.fig_pull_in.add_subplot(1, 1, 1)
        self.ax_pull_in.grid()
        self.ax_pull_in.set(xlabel="V_bias (V)", ylabel="Isolation (dB)", title="Isolation vs Bias voltage")

        # figure that contains pull-in plots for measurement display
        self.fig_pull_in_meas = plt.figure(num=4, dpi=100, tight_layout=True, figsize=(6.5, 6), frameon=True)
        self.ax_pull_in_meas = self.fig_pull_in_meas.add_subplot(1, 1, 1)
        self.ax_pull_in_meas.grid()

        # figure that contains S parameters for measurement display
        self.fig_snp_meas = plt.figure(num=5, dpi=100, tight_layout=True, figsize=(6.5, 6), frameon=True)
        self.ax_snp_meas = self.fig_snp_meas.add_subplot(1, 1, 1)
        self.ax_snp_meas.grid()

        # figure that contains Cycling parameters during cycling test
        self.fig_cycling = plt.figure(num=6, dpi=100, tight_layout=True, figsize=(10, 6), frameon=True)
        # self.ax_cycling_pull_in = self.fig_cycling.add_subplot(3, 2, 1).set_title(label="Pull-in Voltage")
        self.ax_cycling_pull_in = self.fig_cycling.add_subplot(3, 2, 1).set(xlabel="Cycles", ylabel="Pull-in (V)",
                                                                            title="Pull-in Voltage")
        self.ax_cycling_pull_out = self.fig_cycling.add_subplot(3, 2, 2).set(xlabel="Cycles", ylabel="Pull-out (V)",
                                                                             title="Pull-out Voltage")
        self.ax_cycling_isolation = self.fig_cycling.add_subplot(3, 2, 3).set(xlabel="Cycles", ylabel="Isolation (dB)",
                                                                              title="Isolation")
        self.ax_cycling_insertion_loss = self.fig_cycling.add_subplot(3, 2,
                                                                      4).set(xlabel="Cycles",
                                                                             ylabel="Insertion loss variation (dB)",
                                                                             title="Insertion loss variation")
        self.ax_cycling_t_down = self.fig_cycling.add_subplot(3, 2, 5).set(xlabel="Cycles", ylabel="ts_down (s)",
                                                                           title="Down state switching time")
        self.ax_cycling_t_up = self.fig_cycling.add_subplot(3, 2, 6).set(xlabel="Cycles", ylabel="ts_up (s)",
                                                                         title="Up state switching time")
        for ax in self.fig_cycling.axes:
            ax.grid()

        self.fig_power_meas = plt.figure(num=7, dpi=100, tight_layout=True, figsize=(6.5, 6), frameon=True)
        self.ax_power_meas = self.fig_power_meas.add_subplot(1, 1, 1)
        self.ax_power_meas.grid()

        self.s_parameter_s3p = tk.StringVar(value='S11')
        self.s_parameter_s2p = tk.StringVar(value='S11')

        self.scale_amplitude_value = tk.DoubleVar(value=-20)
        self.scale_voltage_value = tk.DoubleVar(value=40)
        self.scale_isolation_value = tk.DoubleVar(value=-20)
        self.scale_frequency_upper_value = tk.DoubleVar(value=2 * 10e9)
        self.scale_frequency_lower_value = tk.DoubleVar(value=0.1 * 10e9)

        self.ax_s3p.set_ylim(ymin=self.scale_amplitude_value.get(), ymax=0)
        self.ax_s3p.set_xlim(xmin=0, xmax=self.scale_frequency_upper_value.get())

        tab_s3p = add_tab(tab_name=' S3P Files ', notebook=self.tabControl, col=0, row=1)  # s3p Tab display
        tab_s2p = add_tab(tab_name=' S2P Files ', notebook=self.tabControl, col=0, row=1)  # s2p Tab display
        tab_pull_in = add_tab(tab_name=' Pull-in Files ', notebook=self.tabControl, col=0, row=1)  # Pull-in Tab display
        tab_pull_in_meas = add_tab(tab_name=' Pull-in Test ', notebook=self.tabControl, col=0, row=1)  # Pull-in Tab
        tab_snp_meas = add_tab(tab_name=' SNP Test ', notebook=self.tabControl, col=0, row=1)  # s3p test Tab
        tab_power_meas = add_tab(tab_name=' Power Test ', notebook=self.tabControl, col=0, row=1)  # Power test Tab
        tab_cycling = add_tab(tab_name=' Cycling tab ', notebook=self.tabControl, col=0, row=1)  # Cycling test Tab
        tab_resources = add_tab(tab_name=' Resource Page ', notebook=self.tabControl, col=0, row=1)  # s3p test Tab

        # ==============================================================================
        # TAB1 S3P parameter display
        # ==============================================================================
        # This TAB is for S3P parameter display
        frame_s3p_directory = add_label_frame(tab_s3p, 's3p Directory', 0, 0)  # s3p Frame
        frame_s3p_display = add_label_frame(tab_s3p, frame_name='s3p Display', col=0, row=1)

        # s3p_dir_name is the directory variable used in the entry entereded_var_s3p
        self.s3p_dir_name = tk.StringVar(
            value=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\S3P')  # Entry variable for s3p dir
        # Adding labels and frame_s3p_display
        add_label(frame_s3p_directory, label_name='Directory', col=1, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                                  ipady=tab_pad_x)
        # Directory frame label
        add_label(frame_s3p_directory, label_name='File', col=1, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                             ipady=tab_pad_x)  # File frame label
        add_label(frame_s3p_directory, label_name='S parameter', col=1, row=3).grid(sticky='e', ipadx=tab_pad_x,
                                                                                    ipady=tab_pad_x)  # File frame label
        #  Adding entry for file directory
        self.entered_var_s3p = add_entry(frame_s3p_directory, text_var=self.s3p_dir_name, width=70, col=2, row=1)

        file_s3p = filetypes_dir(self.entered_var_s3p.get())[0]

        self.s3p_file_name_combobox = add_combobox(frame_s3p_directory, text=file_s3p, col=2, row=2, width=100)
        self.s_parameter_chosen_s3p = add_combobox(frame_s3p_directory, text=self.s_parameter_s3p, col=2, row=3,
                                                   width=100)
        self.s_parameter_chosen_s3p['values'] = ('S11', 'S12', 'S13', 'S21', 'S22', 'S23', 'S31', 'S32', 'S33')

        self.button_file_update = add_button(tab=frame_s3p_directory, button_name=' Update Files ',
                                             command=lambda: [update_entries(directory=self.entered_var_s3p.get(),
                                                                             combobox=self.s3p_file_name_combobox,
                                                                             filetype='.s3p'),
                                                              update_button(self.button_file_update)], col=3,
                                             row=1)  # (self.update_entries_s3p_v2), (self.update_button)

        add_button(tab=frame_s3p_directory, button_name='Exit', command=self._quit, col=5, row=1)
        add_button(tab=frame_s3p_directory, button_name='Plot', command=self.plot_s3p, col=3, row=3)
        add_button(tab=frame_s3p_directory, button_name='Delete graphs', command=self.delete_axs_s3p, col=3, row=2)

        self.s3p_canvas = create_canvas(figure=self.fig_s3p, frame=frame_s3p_display)

        self.slider_amplitude = add_slider(frame=frame_s3p_display, _from=0, to=-40, name="Amplitude (dB)",
                                                variable=self.scale_amplitude_value, step=5)
        self.slider_frequency = add_slider(frame=frame_s3p_display, _from=1e9, to=40e9,
                                                name="Upper Frequency Limit (Hz)",
                                                variable=self.scale_frequency_upper_value, step=10e9)
        self.slider_lower_frequency = add_slider(frame=frame_s3p_display, _from=1e9, to=40e9,
                                                      name=" Lower Frequency Limit (Hz)",
                                                      variable=self.scale_frequency_lower_value, step=10e9)

        self.slider_amplitude.pack(side='left')
        self.slider_frequency.pack(side='right')
        self.slider_lower_frequency.pack(side='right')
        # ==============================================================================
        # TAB2 S2P parameter display
        # ==============================================================================
        # This TAB is for S2P parameter display
        frame_s2p_dir = add_label_frame(tab_s2p, 's2p Directory', 0, 0)  # s2p Frame
        frame_s2p_display = add_label_frame(tab_s2p, frame_name='s2p Display', col=0, row=1)

        self.s2p_dir_name = tk.StringVar(value=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\S2P')
        add_label(frame_s2p_dir, label_name='Directory', col=1, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                            ipady=tab_pad_x)
        add_label(frame_s2p_dir, label_name='File', col=1, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                       ipady=tab_pad_x)
        add_label(frame_s2p_dir, label_name='S parameter', col=1, row=3).grid(sticky='e', ipadx=tab_pad_x,
                                                                              ipady=tab_pad_x)

        self.entered_var_s2p = add_entry(frame_s2p_dir, text_var=self.s2p_dir_name, width=70, col=2, row=1)

        file_s2p = filetypes_dir(self.entered_var_s2p.get())[1]
        self.s2p_file_name_combobox = add_combobox(frame_s2p_dir, text=file_s2p, col=2, row=2, width=100)
        self.s_parameter_chosen_s2p = add_combobox(frame_s2p_dir, text=self.s_parameter_s2p, col=2, row=3, width=100)
        self.s_parameter_chosen_s2p['values'] = ('S11', 'S12', 'S21', 'S22')

        self.update_s2p_button = add_button(tab=frame_s2p_dir, button_name=' Update Files ',
                                            command=lambda: [update_entries(directory=self.entered_var_s2p.get(),
                                                                            combobox=self.s2p_file_name_combobox,
                                                                            filetype='.s2p'),
                                                             update_button(self.update_s2p_button)], col=3, row=1)
        add_button(frame_s2p_dir, button_name='Exit', command=self._quit, col=5, row=1).grid_anchor('e')
        add_button(frame_s2p_dir, button_name='Plot', command=self.plot_s2p, col=3, row=3)
        add_button(frame_s2p_dir, button_name='Delete Graphs', command=self.delete_axs_s2p, col=3, row=2)

        self.s2p_canvas = create_canvas(figure=self.fig_s2p, frame=frame_s2p_display)

        self.slider_amplitude_s2p = add_slider(frame=frame_s2p_display, _from=0, to=-40,
                                                    name="Amplitude (dB)",
                                                    variable=self.scale_amplitude_value, step=5)
        self.slider_frequency_s2p = add_slider(frame=frame_s2p_display, _from=1e9, to=40e9,
                                                    name="Upper Frequency limit (Hz)",
                                                    variable=self.scale_frequency_upper_value, step=10e9)
        self.slider_lower_frequency_s2p = add_slider(frame=frame_s2p_display, _from=1e9, to=40e9,
                                                          name=" Lower Frequency Limit (Hz)",
                                                          variable=self.scale_frequency_lower_value, step=10e9)

        self.slider_amplitude_s2p.pack(side='left')
        self.slider_frequency_s2p.pack(side='right')
        self.slider_lower_frequency_s2p.pack(side='right')
        # ==============================================================================
        # TAB3 Pull voltage vs isolation display
        # ==============================================================================
        # This TAB is for Pull voltage vs isolation display
        frame_v_pull_in_dir = add_label_frame(tab_pull_in, frame_name='Vpull-in Directory', col=0, row=0)  # s2p Frame
        frame_v_pull_in_graph = add_label_frame(tab_pull_in, frame_name='Graph', col=0, row=3)  # s2p Frame

        self.pull_in_dir_name = tk.StringVar(
            value=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\Pullin voltage')

        add_label(frame_v_pull_in_dir, 'Directory', col=1, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                       ipady=tab_pad_x)
        add_label(frame_v_pull_in_dir, 'File', col=1, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                  ipady=tab_pad_x)

        self.frame_v_pull_in_display = add_label_frame(tab_pull_in, frame_name='Pull-in Display', col=0, row=1)

        self.entered_var_txt = add_entry(frame_v_pull_in_dir, text_var=self.pull_in_dir_name, width=70, col=2, row=1)

        file_txt = filetypes_dir(self.entered_var_txt.get())[2]
        self.txt_file_name_combobox = add_combobox(frame_v_pull_in_dir, text=file_txt, col=2, row=2, width=100)

        self.update_pull_in_button = add_button(tab=frame_v_pull_in_dir, button_name=' Update Files ',
                                                command=lambda: [update_entries(directory=self.entered_var_txt.get(),
                                                                                combobox=self.txt_file_name_combobox,
                                                                                filetype='.txt'),
                                                                 update_button(self.update_pull_in_button)],
                                                col=3, row=1)
        add_button(frame_v_pull_in_dir, 'Exit', command=self._quit, col=5, row=1).grid_anchor('e')
        add_button(frame_v_pull_in_dir, 'Plot', command=lambda: [self.plot_vpull_in(),
                                                                 self.calculate_pull_in_out_voltage()], col=3, row=3)
        add_button(frame_v_pull_in_dir, 'Delete Graphs', command=self.delete_axs_vpullin, col=3, row=2)
        add_button(frame_v_pull_in_dir, 'Calculate Pull-in and Pull-out voltages',
                   command=self.calculate_pull_in_out_voltage, col=2, row=3).configure(width=40)
        self.text_scroll = add_scrolled_text(tab=self.frame_v_pull_in_display, scrolled_width=100, scrolled_height=3)

        self.canvas_v_pull_in_display = create_canvas(figure=self.fig_pull_in, frame=frame_v_pull_in_graph)

        self.slider_isolation = add_slider(frame=frame_v_pull_in_graph, _from=0, to=-40,
                                                name="Isolation (dB)", variable=self.scale_isolation_value, step=5)
        self.slider_voltage = add_slider(frame=frame_v_pull_in_graph, _from=0, to=50,
                                              name="Voltage upper limit (V)", variable=self.scale_voltage_value, step=5)

        self.slider_isolation.pack(side='left')
        self.slider_voltage.pack(side='right')
        # ==============================================================================
        # TAB4 Pull down voltage vs isolation measurement
        # ==============================================================================
        # This TAB is for Pull down voltage vs isolation measurement
        frame_test_pull_in_comp_info = add_label_frame(tab_pull_in_meas, frame_name='Component information', col=0,
                                                       row=0)
        frame_test_pull_in_sig_gen = add_label_frame(tab=tab_pull_in_meas, frame_name='Signal Generator', col=0, row=1)
        frame_test_pull_in_gen_controls = add_label_frame(tab=tab_pull_in_meas, frame_name='General controls', col=2,
                                                          row=0)

        add_label(frame_test_pull_in_comp_info, label_name='DIR', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x,
                                                                                     ipady=tab_pad_x)
        add_label(frame_test_pull_in_comp_info, label_name='Project', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                                         ipady=tab_pad_x)
        add_label(frame_test_pull_in_comp_info, label_name='Cell', col=0, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                                      ipady=tab_pad_x)
        add_label(frame_test_pull_in_comp_info, label_name='Reticule', col=0, row=3).grid(sticky='e', ipadx=tab_pad_x,
                                                                                          ipady=tab_pad_x)
        add_label(frame_test_pull_in_comp_info, label_name='Device', col=0, row=4).grid(sticky='e', ipadx=tab_pad_x,
                                                                                        ipady=tab_pad_x)
        add_label(frame_test_pull_in_comp_info, label_name='Bias Voltage', col=0, row=5).grid(sticky='e',
                                                                                              ipadx=tab_pad_x,
                                                                                              ipady=tab_pad_x)

        self.test_pull_in_dir = tk.StringVar(value=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\Pullin '
                                                   r'voltage')
        self.test_pull_in_project = tk.StringVar(value=r'Project_Name')
        self.test_pull_in_cell = tk.StringVar(value=r'Cell_Name')
        self.test_pull_in_reticule = tk.StringVar(value=r'Reticule')
        self.test_pull_in_device = tk.StringVar(value=r'Device_name')
        self.test_pull_in_file_created = tk.StringVar(value=r'EMPTY')
        self.test_pull_in_bias_voltage = tk.StringVar(value=r'Bias_Voltage')

        add_entry(tab=frame_test_pull_in_comp_info, text_var=self.test_pull_in_dir, width=20, col=1, row=0)
        add_entry(tab=frame_test_pull_in_comp_info, text_var=self.test_pull_in_project, width=20, col=1, row=1)
        add_entry(tab=frame_test_pull_in_comp_info, text_var=self.test_pull_in_cell, width=20, col=1, row=2)
        add_entry(tab=frame_test_pull_in_comp_info, text_var=self.test_pull_in_reticule, width=20, col=1, row=3)
        add_entry(tab=frame_test_pull_in_comp_info, text_var=self.test_pull_in_device, width=20, col=1, row=4)
        add_entry(tab=frame_test_pull_in_comp_info, text_var=self.test_pull_in_bias_voltage, width=20, col=1, row=5)

        # Signal Generator-------------------------------------------------------------
        self.pull_in_v_bias = tk.DoubleVar(value=10)  # Peak bias voltage for ramp function
        self.ramp_width = tk.DoubleVar(value=100)  # Ramp length for ramp function
        self.chosen_bias_voltage_pull_in = add_entry(tab=frame_test_pull_in_comp_info, text_var=self.pull_in_v_bias,
                                                     width=20, col=1, row=5)
        add_label(frame_test_pull_in_sig_gen, label_name='Bias Voltage', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x,
                                                                                            ipady=tab_pad_x)
        add_label(frame_test_pull_in_sig_gen, label_name='Ramp length', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                                           ipady=tab_pad_x)
        self.entered_ramp_volt = add_entry(frame_test_pull_in_sig_gen, text_var=self.pull_in_v_bias, width=10, col=1,
                                           row=0)
        self.txt_file_name_meas_combobox = [self.test_pull_in_project.get(),
                                            self.test_pull_in_cell.get(),
                                            self.test_pull_in_reticule.get(),
                                            self.test_pull_in_device.get(),
                                            self.entered_ramp_volt.get()]
        add_button(tab=frame_test_pull_in_comp_info, button_name='Create-file',
                   command=lambda: [self.txt_file_name_meas_combobox,
                                    file_name_creation(data_list=self.txt_file_name_meas_combobox,
                                                       text=self.text_file_name_pull_in_test, end_characters='V')],
                   col=2, row=0)

        self.entered_ramp_width = add_entry(frame_test_pull_in_sig_gen, text_var=self.ramp_width, width=10, col=1,
                                            row=1)
        add_label(frame_test_pull_in_sig_gen, label_name='(V)', col=2, row=0).grid(sticky='w', ipadx=tab_pad_x,
                                                                                   ipady=tab_pad_x)
        add_label(frame_test_pull_in_sig_gen, label_name='(µs)', col=2, row=1).grid(sticky='w', ipadx=tab_pad_x,
                                                                                    ipady=tab_pad_x)
        add_button(tab=frame_test_pull_in_sig_gen, button_name='Set Bias Voltage', command=self.set_bias_pull_in,
                   col=3, row=0).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_test_pull_in_sig_gen, button_name='Set Ramp Width', command=self.set_ramp_width, col=3,
                   row=1).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_test_pull_in_sig_gen, button_name='Set Pulse Gen', command=self.set_pulse_gen_ramp,
                   col=3, row=3).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)

        # General controls---------------------------------------------------------------

        self.text_file_name_pull_in_test = tk.Text(frame_test_pull_in_gen_controls, width=40, height=1, wrap=tk.WORD,
                                                   border=4, borderwidth=2,
                                                   relief=tk.SUNKEN, font=('Bahnschrift Light', 10))  # Filename
        self.text_file_name_pull_in_test.grid(column=0, row=0, sticky='n', columnspan=5)
        self.text4 = tk.Text(frame_test_pull_in_gen_controls, width=40, height=10, wrap=tk.WORD, border=4,
                             borderwidth=2, relief=tk.SUNKEN, font=('Bahnschrift Light', 10))
        # Debug text_file_name_s3p_test display
        self.text4.grid(column=0, row=3, sticky='n', columnspan=4)

        add_button(tab=frame_test_pull_in_gen_controls, button_name='Reset Signal Generator',
                   command=self.reset_sig_gen, col=0, row=1).grid(ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_test_pull_in_gen_controls, button_name='Exit', command=lambda: [self._quit(),
                                                                                             close_resources()], col=1,
                   row=1).grid(ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_test_pull_in_gen_controls, button_name='Plot IsovsV',
                   command=lambda: [self.trace_pull_down(), self.acquire_pull_down_data()], col=1, row=5).grid(
            ipadx=tab_pad_x, ipady=tab_pad_x)
        # -------------------------------------------------------------------------------------------------------------
        frame13 = add_label_frame(tab=tab_pull_in_meas, frame_name='Oscilloscope Tecktronix', col=1, row=0, row_span=2)
        self.canvas_v_pull_in_meas = create_canvas(figure=self.fig_pull_in_meas, frame=frame13)

        frame_test_pull_in_sig_gen = add_label_frame(tab=tab_pull_in_meas, frame_name='Measurement', col=2, row=1,
                                                     row_span=2)
        add_label(frame_test_pull_in_sig_gen,
                  label_name='Positive-Pull-in', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        self.text5 = tk.Text(frame_test_pull_in_sig_gen, width=15, height=1, wrap=tk.WORD, border=4, borderwidth=2,
                             relief=tk.SUNKEN, font=('Bahnschrift Light', 10))  # Positive Pull-in
        self.text5.grid(column=1, row=0, sticky='n', columnspan=5)

        add_label(frame_test_pull_in_sig_gen,
                  label_name='Negative-Pull-in', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        self.text6 = tk.Text(frame_test_pull_in_sig_gen, width=15,
                             height=1, wrap=tk.WORD, border=4, borderwidth=2, relief=tk.SUNKEN,
                             font=('Bahnschrift Light', 10))  # Negative Pull-in
        self.text6.grid(column=1, row=1, sticky='n', columnspan=5)

        add_label(frame_test_pull_in_sig_gen,
                  label_name='Positive-Pull-out', col=0, row=2).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        self.text7 = tk.Text(frame_test_pull_in_sig_gen,
                             width=15, height=1, wrap=tk.WORD, border=4,
                             borderwidth=2, relief=tk.SUNKEN, font=('Bahnschrift Light', 10))  # Positive Pull-out
        self.text7.grid(column=1, row=2, sticky='n', columnspan=5)

        add_label(frame_test_pull_in_sig_gen, label_name='Negative-Pull-out', col=0, row=3).grid(sticky='e',
                                                                                                 ipadx=tab_pad_x,
                                                                                                 ipady=tab_pad_x)
        self.text8 = tk.Text(frame_test_pull_in_sig_gen, width=15, height=1, wrap=tk.WORD, border=4, borderwidth=2,
                             relief=tk.SUNKEN,
                             font=('Bahnschrift Light', 10))  # Negative Pull-out
        self.text8.grid(column=1, row=3, sticky='n', columnspan=5)

        add_label(frame_test_pull_in_sig_gen, label_name='Isolation at PI(+)', col=0, row=4).grid(sticky='e',
                                                                                                  ipadx=tab_pad_x,
                                                                                                  ipady=tab_pad_x)
        self.text9 = tk.Text(frame_test_pull_in_sig_gen, width=15, height=1, wrap=tk.WORD, border=4, borderwidth=2,
                             relief=tk.SUNKEN,
                             font=('Bahnschrift Light', 10))  # Isolation at PI (+)
        self.text9.grid(column=1, row=4, sticky='n', columnspan=5)

        add_label(frame_test_pull_in_sig_gen, label_name='Isolation at PO (+)', col=0, row=5).grid(sticky='e',
                                                                                                   ipadx=tab_pad_x,
                                                                                                   ipady=tab_pad_x)
        self.text_iso_pull_out_plus = tk.Text(frame_test_pull_in_sig_gen, width=15, height=1, wrap=tk.WORD, border=4,
                                              borderwidth=2, relief=tk.SUNKEN,
                                              font=('Bahnschrift Light', 10))  # Isolation at PO (+)
        self.text_iso_pull_out_plus.grid(column=1, row=5, sticky='n', columnspan=5)

        add_label(frame_test_pull_in_sig_gen, label_name='Isolation at PI (-)', col=0, row=6).grid(sticky='e',
                                                                                                   ipadx=tab_pad_x,
                                                                                                   ipady=tab_pad_x)
        self.text_iso_pull_in_minus = tk.Text(frame_test_pull_in_sig_gen, width=15, height=1, wrap=tk.WORD, border=4,
                                              borderwidth=2, relief=tk.SUNKEN,
                                              font=('Bahnschrift Light', 10))  # Isolation at PI (-)
        self.text_iso_pull_in_minus.grid(column=1, row=6, sticky='n', columnspan=5)

        add_label(frame_test_pull_in_sig_gen, label_name='Isolation at PO (-)', col=0, row=7).grid(sticky='e',
                                                                                                   ipadx=tab_pad_x,
                                                                                                   ipady=tab_pad_x)
        self.text_iso_pull_out_minus = tk.Text(frame_test_pull_in_sig_gen, width=15, height=1, wrap=tk.WORD, border=4,
                                               borderwidth=2, relief=tk.SUNKEN,
                                               font=('Bahnschrift Light', 10))  # Isolation at PO (-)
        self.text_iso_pull_out_minus.grid(column=1, row=7, sticky='n', columnspan=5)
        # ==============================================================================
        # TAB5 S-parameters test
        # ==============================================================================
        frame_snp_compo_info = add_label_frame(tab_snp_meas, frame_name='Component information', col=0,
                                               row=0)  # s3p frame
        frame_snp_sig_gen = add_label_frame(tab=tab_snp_meas, frame_name='Signal Generator', col=0, row=1)
        frame_snp_zva = add_label_frame(tab=tab_snp_meas, frame_name='ZVA', col=3, row=1)
        frame_snp_gene_controls = add_label_frame(tab=tab_snp_meas, frame_name='General controls', col=3, row=0)

        add_label(frame_snp_compo_info, label_name='DIR', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x,
                                                                             ipady=tab_pad_x)
        add_label(frame_snp_compo_info, label_name='Project', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                                 ipady=tab_pad_x)
        add_label(frame_snp_compo_info, label_name='Cell', col=0, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                              ipady=tab_pad_x)
        add_label(frame_snp_compo_info, label_name='Reticule', col=0, row=3).grid(sticky='e', ipadx=tab_pad_x,
                                                                                  ipady=tab_pad_x)
        add_label(frame_snp_compo_info, label_name='Device', col=0, row=4).grid(sticky='e', ipadx=tab_pad_x,
                                                                                ipady=tab_pad_x)
        add_label(frame_snp_compo_info, label_name='Status', col=0, row=5).grid(sticky='e', ipadx=tab_pad_x,
                                                                                ipady=tab_pad_x)
        add_label(frame_snp_compo_info, label_name='Bias Voltage', col=0, row=6).grid(sticky='e', ipadx=tab_pad_x,
                                                                                      ipady=tab_pad_x)

        self.test_s3p_dir = tk.StringVar(value=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\S3P')
        self.test_s3p_project = tk.StringVar(value=r'Project_Name')
        self.test_s3p_cell = tk.StringVar(value=r'Cell_Name')
        self.test_s3p_reticule = tk.StringVar(value=r'Reticule')
        self.test_s3p_device = tk.StringVar(value=r'Device_name')
        self.test_s3p_file_created = tk.StringVar(value=r'EMPTY')
        self.test_s3p_state = tk.StringVar(value=r'Active')

        # self.component_state = add_combobox(frame_snp_compo_info, text=self.test_s3p_state, col=1, row=5, width=20)
        self.bias_voltage_s3p = tk.StringVar(value=r'Bias_Voltage')

        self.chosen_component_state = add_combobox(frame_snp_compo_info, text=self.test_s3p_state, col=1, row=5,
                                                   width=20)
        self.chosen_component_state['values'] = ('Active', 'Frozen')
        self.chosen_component_state.current(0)

        add_entry(tab=frame_snp_compo_info, text_var=self.test_s3p_dir, width=20, col=1, row=0)
        add_entry(tab=frame_snp_compo_info, text_var=self.test_s3p_project, width=20, col=1, row=1)
        add_entry(tab=frame_snp_compo_info, text_var=self.test_s3p_cell, width=20, col=1, row=2)
        add_entry(tab=frame_snp_compo_info, text_var=self.test_s3p_reticule, width=20, col=1, row=3)
        add_entry(tab=frame_snp_compo_info, text_var=self.test_s3p_device, width=20, col=1, row=4)

        #  ------------------------------------------------------------------------------
        self.text_file_name_s3p_test = tk.Text(frame_snp_gene_controls, width=40, height=1, wrap=tk.WORD, border=4,
                                               borderwidth=2,
                                               relief=tk.SUNKEN, font=('Bahnschrift Light', 10))

        self.pull_in_v = tk.DoubleVar(value=10)
        self.pulse_width = tk.DoubleVar(value=5)
        self.pulse_freq = tk.DoubleVar(value=0.1)
        self.chosen_bias_voltage = add_entry(tab=frame_snp_compo_info, text_var=self.pull_in_v, width=20, col=1, row=6)

        self.file_s3p = [self.test_s3p_project.get(), self.test_s3p_cell.get(), self.test_s3p_reticule.get(),
                         self.test_s3p_device.get(), self.chosen_component_state.get(), self.chosen_bias_voltage.get()]

        add_button(tab=frame_snp_compo_info, button_name='Create-file',
                   command=lambda: [self.file_s3p, file_name_creation(
                       data_list=self.file_s3p, text=self.text_file_name_s3p_test, end_characters='V')], col=2, row=0)

        add_label(frame_snp_sig_gen, label_name='Bias Voltage', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x,
                                                                                   ipady=tab_pad_x)
        add_label(frame_snp_sig_gen, label_name='Pulse Width', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                                  ipady=tab_pad_x)
        self.entered_pull_in_volt = add_entry(frame_snp_sig_gen, text_var=self.pull_in_v, width=10, col=1, row=0)
        self.entered_pulse_width = add_entry(frame_snp_sig_gen, text_var=self.pulse_width, width=10, col=1, row=1)
        add_label(frame_snp_sig_gen, label_name='(V)', col=2, row=0).grid(sticky='w', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_snp_sig_gen, label_name='(s)', col=2, row=1).grid(sticky='w', ipadx=tab_pad_x, ipady=tab_pad_x)

        add_label(frame_snp_sig_gen, label_name='Pulse Frequency', col=0, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                                      ipady=tab_pad_x)
        self.entered_pulse_freq = add_entry(frame_snp_sig_gen, text_var=self.pulse_freq, width=10, col=1, row=2)
        add_label(frame_snp_sig_gen, label_name='(Hz)', col=2, row=2).grid(sticky='w', ipadx=tab_pad_x, ipady=tab_pad_x)

        add_button(tab=frame_snp_sig_gen, button_name='Set Bias Voltage', command=self.set_bias_voltage, col=3,
                   row=0).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_sig_gen, button_name='Set Pulse Width', command=self.set_ramp_width, col=3,
                   row=1).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_sig_gen,
                   button_name='Set prf', command=self.set_prf, col=3, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                                   ipady=tab_pad_x)
        add_button(tab=frame_snp_sig_gen, button_name='Set Pulse Gen', command=self.set_pulse_gen, col=3, row=3).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        # ------------------------------------------------------------------------------
        frame19 = add_label_frame(tab=tab_snp_meas, frame_name='SNP measurement', col=1, row=0, row_span=2)
        self.canvas_snp_meas = create_canvas(figure=self.fig_snp_meas, frame=frame19)

        # ------------------------------------------------------------------------------

        self.text_file_name_s3p_test.grid(column=0, row=0, sticky='n', columnspan=5)

        self.f_start = tk.DoubleVar(value=1)
        self.f_stop = tk.DoubleVar(value=10)
        self.nb_points = tk.DoubleVar(value=100)

        add_label(frame_snp_zva, label_name='Fstart', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_snp_zva, label_name='Fstop', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_snp_zva, label_name='Nb Points', col=0, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                            ipady=tab_pad_x)
        self.entered_f_start = add_entry(frame_snp_zva, text_var=self.f_start, width=10, col=1, row=0)
        self.entered_fstop = add_entry(frame_snp_zva, text_var=self.f_stop, width=10, col=1, row=1)
        self.entered_nb_points = add_entry(frame_snp_zva, text_var=self.nb_points, width=10, col=1, row=2)
        add_label(frame_snp_zva, label_name='(GHz)', col=2, row=0).grid(sticky='w', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_snp_zva, label_name='(GHz)', col=2, row=1).grid(sticky='w', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_snp_zva, label_name='(Pts)', col=2, row=2).grid(sticky='w', ipadx=tab_pad_x, ipady=tab_pad_x)

        add_button(tab=frame_snp_zva, button_name='Set Fstart',
                   command=self.set_f_start, col=3, row=0).grid(sticky='e',
                                                                ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_zva, button_name='Set Fstop',
                   command=self.set_fstop, col=3, row=1).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_zva, button_name='Set Nb points', command=self.set_nb_points, col=3, row=2).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_zva, button_name='Set ZVA', command=self.set_zva, col=3, row=3).grid(sticky='e',
                                                                                                      ipadx=tab_pad_x,
                                                                                                      ipady=tab_pad_x)
        add_button(tab=frame_snp_zva, button_name='Capture S3P', command=self.data_acquire, col=1, row=4).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_zva, button_name='Capture S2P', command=self.data_acquire_s2p, col=2, row=4).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_zva, button_name='Capture S1P', command=self.data_acquire_s1p, col=3, row=4).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)

        # ------------------------------------------------------------------------------

        self.text_snp_debug = tk.Text(frame_snp_gene_controls, width=40, height=10, wrap=tk.WORD, border=4,
                                      borderwidth=2,
                                      relief=tk.SUNKEN,
                                      font=('Bahnschrift Light', 10))
        self.text_snp_debug.grid(column=0, row=3, sticky='n', columnspan=4)

        add_button(tab=frame_snp_gene_controls, button_name='Comms prep', command=scripts_and_functions.comprep_zva,
                   col=0, row=1).grid(
            ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_gene_controls, button_name='Reset ZVA', command=self.reset_zva, col=0, row=2).grid(
            ipadx=tab_pad_x,
            ipady=tab_pad_x)
        add_button(tab=frame_snp_gene_controls, button_name='Exit', command=lambda: [self._quit(), close_resources()],
                   col=1,
                   row=1).grid(ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_gene_controls, button_name='Reset Signal Gen', command=self.set_pulse_gen_pulse_mode,
                   col=1,
                   row=2).grid(ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_gene_controls, button_name='S1P config', command=call_s1p_config, col=0, row=4).grid(
            ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_gene_controls, button_name='S2P config', command=call_s2p_config, col=1, row=4).grid(
            ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_gene_controls, button_name='S3P config', command=call_s3p_config, col=2, row=4).grid(
            ipadx=tab_pad_x, ipady=tab_pad_x)

        # ==============================================================================
        # TAB6 Power measurement TAB
        # ==============================================================================
        frame_power_compo_info = add_label_frame(tab_power_meas, frame_name='Component information', col=0,
                                                 row=0)  # power sweep frame

        add_label(frame_power_compo_info, label_name='DIR', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x,
                                                                               ipady=tab_pad_x)
        add_label(frame_power_compo_info, label_name='Project', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                                   ipady=tab_pad_x)
        add_label(frame_power_compo_info, label_name='Cell', col=0, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                                ipady=tab_pad_x)
        add_label(frame_power_compo_info, label_name='Reticule', col=0, row=3).grid(sticky='e', ipadx=tab_pad_x,
                                                                                    ipady=tab_pad_x)
        add_label(frame_power_compo_info, label_name='Device', col=0, row=4).grid(sticky='e', ipadx=tab_pad_x,
                                                                                  ipady=tab_pad_x)
        add_label(frame_power_compo_info, label_name='Status', col=0, row=5).grid(sticky='e', ipadx=tab_pad_x,
                                                                                  ipady=tab_pad_x)
        add_label(frame_power_compo_info, label_name='Bias Voltage', col=0, row=6).grid(sticky='e', ipadx=tab_pad_x,
                                                                                        ipady=tab_pad_x)

        self.test_pow_dir = tk.StringVar(value=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\Power handling')
        self.test_pow_project = tk.StringVar(value=r'Project_Name')
        self.test_pow_cell = tk.StringVar(value=r'Cell_Name')
        self.test_pow_reticule = tk.StringVar(value=r'Reticule')
        self.test_pow_device = tk.StringVar(value=r'Device_name')
        self.test_pow_file_created = tk.StringVar(value=r'EMPTY')
        self.test_pow_state = tk.StringVar(value=r'EMPTY')

        self.bias_voltage_pow = tk.StringVar(value=r'Bias_Voltage')

        self.chosen_component_state_pow = add_combobox(frame_power_compo_info, text=self.test_pow_state, col=1, row=5,
                                                       width=20)
        self.chosen_component_state_pow['values'] = ('Active', 'Frozen')
        self.chosen_component_state_pow.current(0)

        add_entry(tab=frame_power_compo_info, text_var=self.test_pow_dir, width=20, col=1, row=0)
        add_entry(tab=frame_power_compo_info, text_var=self.test_pow_project, width=20, col=1, row=1)
        add_entry(tab=frame_power_compo_info, text_var=self.test_pow_cell, width=20, col=1, row=2)
        add_entry(tab=frame_power_compo_info, text_var=self.test_pow_reticule, width=20, col=1, row=3)
        add_entry(tab=frame_power_compo_info, text_var=self.test_pow_device, width=20, col=1, row=4)
        add_entry(tab=frame_power_compo_info, text_var=self.bias_voltage_pow, width=20, col=1, row=6)

        self.power_test_file_name = [self.test_pow_project.get(), self.test_pow_cell.get(),
                                     self.test_pow_reticule.get(),
                                     self.test_pow_device.get(), self.chosen_component_state_pow.get(),
                                     self.bias_voltage_pow.get()]

        add_button(tab=frame_power_compo_info, button_name='Create-file',
                   command=lambda: [self.power_test_file_name,
                                    file_name_creation(data_list=self.power_test_file_name,
                                                       text=self.text_power_file_name, end_characters='V')],
                   col=2, row=0)
        add_button(tab=frame_power_compo_info, button_name='Send trigger', command=scripts_and_functions.send_trig,
                   col=2, row=1)
        # General controls---------------------------------------------------------------
        frame_power_meas = add_label_frame(tab=tab_power_meas, frame_name='General controls', col=2, row=0)
        frame_power_meas_graph = add_label_frame(tab=tab_power_meas, frame_name='Power test Graph', col=1, row=0,
                                                 row_span=2)
        frame_power_meas_sig_gen = add_label_frame(tab=tab_power_meas, frame_name='Signal Generator', col=0, row=1,
                                                   row_span=1)
        frame_power_meas_rf_gen = add_label_frame(tab=tab_power_meas, frame_name='RF Generator', col=2, row=1,
                                                  row_span=1)

        rf_gen_min_power = tk.DoubleVar(value=-40)
        rf_gen_max_power = tk.DoubleVar(value=-20)
        rf_gen_step = tk.DoubleVar(value=1)

        add_entry(tab=frame_power_meas_rf_gen, text_var=rf_gen_min_power, width=20, col=1, row=0)
        add_entry(tab=frame_power_meas_rf_gen, text_var=rf_gen_max_power, width=20, col=1, row=1)
        add_entry(tab=frame_power_meas_rf_gen, text_var=rf_gen_step, width=20, col=1, row=2)

        add_label(tab=frame_power_meas_rf_gen, label_name="Min Power", col=0, row=0)
        add_label(tab=frame_power_meas_rf_gen, label_name="Max Power", col=0, row=1)
        add_label(tab=frame_power_meas_rf_gen, label_name="Step Power", col=0, row=2)

        self.text_power_file_name = tk.Text(frame_power_meas, width=40, height=1, wrap=tk.WORD, border=4,
                                            borderwidth=2, relief=tk.SUNKEN, font=('Bahnschrift Light', 10))  # Filename
        self.text_power_file_name.grid(column=0, row=0, sticky='n', columnspan=5)
        self.text_power_debug = tk.Text(frame_power_meas,
                                        width=40, height=10, wrap=tk.WORD, border=4, borderwidth=2, relief=tk.SUNKEN,
                                        font=('Bahnschrift Light', 10))  # Debug text_file_name_s3p_test display
        self.text_power_debug.grid(column=0, row=3, sticky='n', columnspan=4)

        add_button(tab=frame_power_meas_sig_gen, button_name='Reset Signal Generator',
                   command=self.set_pulse_gen_pulse_mode, col=0,
                   row=0).grid(ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_power_meas, button_name='Exit', command=lambda: [self._quit(), close_resources()], col=1,
                   row=1).grid(ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_power_meas, button_name='Launch Test',
                   command=lambda: scripts_and_functions.power_test_sequence(), col=1, row=5).grid(ipadx=tab_pad_x,
                                                                                                   ipady=tab_pad_x)
        add_button(tab=frame_power_meas_sig_gen, button_name='Setup power test',
                   command=NotImplemented, col=1, row=0).grid(ipadx=tab_pad_x, ipady=tab_pad_x)

        create_canvas(figure=self.fig_power_meas, frame=frame_power_meas_graph, toolbar=True)
        # ==============================================================================
        # TAB8 Resource SCPI configuration
        # ==============================================================================
        frame_resources = add_label_frame(tab_resources, frame_name='Ressouce Configuration', col=0, row=0)
        # Resource frame

        self.zva_inst = tk.StringVar(value=r'TCPIP0::ZNA67-101810::inst0::INSTR')
        self.sig_gen_inst = tk.StringVar(value=r'TCPIP0::A-33521B-00526::inst0::INSTR')
        self.osc_inst = tk.StringVar(value=r'TCPIP0::DPO5054-C011738::inst0::INSTR')
        self.powermeter_inst = tk.StringVar(value=u'TCPIP0::A-N1912A-00589::inst0::INSTR')
        self.rf_gen_inst = tk.StringVar(value=u'TCPIP0::rssmb100a179766::inst0::INSTR')

        add_label(frame_resources, label_name='ZVA', col=1, row=1).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_resources, label_name='Signal Generator', col=1, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                                     ipady=tab_pad_x)
        add_label(frame_resources,
                  label_name='Oscilloscope', col=1, row=3).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_resources,
                  label_name='Powermeter', col=1, row=4).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_resources,
                  label_name='RF Generator', col=1, row=5).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)

        self.entered_var_zva_address = add_entry(frame_resources, text_var=self.zva_inst, width=70, col=2, row=1)
        self.entered_var_sig_gen_address = add_entry(frame_resources, text_var=self.sig_gen_inst, width=70, col=2,
                                                     row=2)
        self.entered_var_osc_address = add_entry(frame_resources, text_var=self.osc_inst, width=70, col=2, row=3)
        self.entered_var_powermeter_address = add_entry(frame_resources, text_var=self.powermeter_inst, width=70, col=2,
                                                        row=4)
        self.entered_var_rf_gen_address = add_entry(frame_resources, text_var=self.rf_gen_inst, width=70, col=2, row=5)

        # ==============================================================================
        # TAB9
        # ==============================================================================
        frame_cycling_comp_info = add_label_frame(tab=tab_cycling, frame_name='Component information', col=0,
                                                  row=0)  # Resource frame

        add_label(frame_cycling_comp_info,
                  label_name='DIR', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_cycling_comp_info,
                  label_name='Project', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_cycling_comp_info,
                  label_name='Cell', col=0, row=2).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_cycling_comp_info,
                  label_name='Reticule', col=0, row=3).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_cycling_comp_info,
                  label_name='Device', col=0, row=4).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_cycling_comp_info,
                  label_name='Cycles', col=0, row=5).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_cycling_comp_info,
                  label_name='Events', col=0, row=6).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_cycling_comp_info,
                  label_name='File name', col=0, row=7).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_cycling_comp_info,
                  label_name='x10^5', col=2, row=5).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)

        add_button(tab=frame_cycling_comp_info, button_name="Exit", command=self._quit,
                   col=0, row=8).grid(ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_cycling_comp_info, button_name="Start Cycling", command=self.cycling_test,
                   col=1, row=8).grid(ipadx=tab_pad_x, ipady=tab_pad_x)

        self.test_cycling_dir = tk.StringVar(value=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement '
                                                   r'Data\Mechanical cycling')
        self.test_cycling_project = tk.StringVar(value=r'Project_Name')
        self.test_cycling_cell = tk.StringVar(value='Cell_name')
        self.test_cycling_ret = tk.StringVar(value='Reticule')
        self.test_cycling_device = tk.StringVar(value='Device_Name')
        self.test_cycling_var_bias = tk.StringVar(value='Bias_voltage')
        self.test_cycling_var_nb_cycles = tk.DoubleVar(value=1)
        self.test_cycling_file_name = tk.StringVar(value='new_file')
        self.test_cycling_events = tk.DoubleVar(value=100)

        self.entered_cycling_dir = add_entry(
            frame_cycling_comp_info, text_var=self.test_cycling_dir, width=20, col=1, row=0)
        self.entered_var_cycling_project = add_entry(
            frame_cycling_comp_info, text_var=self.test_cycling_project, width=20, col=1, row=1)
        self.entered_var_cycling_cell = add_entry(
            frame_cycling_comp_info, text_var=self.test_cycling_cell, width=20, col=1, row=2)
        self.entered_cycling_ret = add_entry(
            frame_cycling_comp_info, text_var=self.test_cycling_ret, width=15, col=1, row=3)
        self.entered_cycling_device = add_entry(
            frame_cycling_comp_info, text_var=self.test_cycling_device, width=20, col=1, row=4)
        self.entered_cycling_var_bias = add_entry(
            frame_cycling_comp_info, text_var=self.test_cycling_var_nb_cycles, width=20, col=1, row=5)
        self.entered_file_name = add_entry(
            frame_cycling_comp_info, text_var=self.test_cycling_file_name, width=20, col=1, row=7)
        self.entered_test_cycling_events = add_entry(
            frame_cycling_comp_info, text_var=self.test_cycling_events, width=20, col=1, row=6)

        frame20 = add_label_frame(tab=tab_cycling, frame_name='Signal Generator', col=0, row=1)

        add_label(frame20, label_name='Bias voltage', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x,
                                                                         ipady=tab_pad_x)
        add_label(frame20, label_name='V', col=2, row=0).grid(sticky='w', ipadx=tab_pad_x,
                                                              ipady=tab_pad_x)
        add_label(frame20, label_name='Number of Cycles', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                             ipady=tab_pad_x)
        add_label(frame20, label_name='Cycles (x10^5)', col=2, row=1).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        self.test_cycling_var_bias = tk.StringVar(value='40')

        self.entered_var_cycling_bias = add_entry(frame20, text_var=self.test_cycling_var_bias, width=15, col=1, row=0)
        self.entered_var_cycling_nb_cycles = add_entry(frame20, text_var=self.test_cycling_var_nb_cycles,
                                                       width=15, col=1, row=1)

        add_button(tab=frame20, button_name='Cycling config', command=self.sig_gen_cycling_config, col=0, row=2).grid(
            ipadx=tab_pad_x, ipady=tab_pad_x)

        add_button(tab=frame20, button_name='Set Bias voltage',
                   command=lambda: self.set_symmetrical_voltage_bias(voltage=self.test_cycling_var_bias.get()), col=3,
                   row=0).grid(ipadx=tab_pad_x, ipady=tab_pad_x)

        frame21 = add_label_frame(tab=tab_cycling, frame_name='Oscilloscope', col=0, row=2)

        add_button(tab=frame21, button_name='Cycling config',
                   command=scripts_and_functions.osc_cycling_config, col=0,
                   row=0).grid(ipadx=tab_pad_x, ipady=tab_pad_x)

        frame22 = add_label_frame(tab=tab_cycling, frame_name='Cycling monitor', col=1, row=0, row_span=3)

        create_canvas(figure=self.fig_cycling, frame=frame22)

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
        return file_menu

    def _quit(self):  # Exit GUI cleanly (used in all TABS)
        self.quit()
        scripts_and_functions.close_all_resources()
        plt.close()
        self.destroy()

    # ZVA Functions ---------------------------------------------------------------
    def reset_zva(self):  # Reset zva using the IP address at Resource Page (used in TAB5)
        ip = self.zva_inst.get()
        scripts_and_functions.setup_zva_with_rst(ip)

    def set_f_start(self):  # Configure ZVA f_start (used in TAB5)
        fstart = self.f_start.get()
        scripts_and_functions.set_f_start(fstart)
        self.error_log(scripts_and_functions.zva)

    def set_fstop(self):  # Configure ZVA f_stop (used in TAB5)
        fstop = self.f_stop.get()
        scripts_and_functions.set_fstop(fstop)
        self.error_log(scripts_and_functions.zva)

    def set_nb_points(self):  # Configure ZVA number of points (used in TAB5)
        nb_points = self.nb_points.get()
        scripts_and_functions.number_of_points(nb_points)
        self.error_log(scripts_and_functions.zva)

    def set_zva(self):  # Configure ZVA f_start/f_stop/nbpoints (used in TAB5)
        self.set_f_start()
        self.set_fstop()
        self.set_nb_points()
        self.text_snp_debug.delete("1.0", "end")
        self.text_snp_debug.insert(index="%d.%d" % (0, 0), chars=scripts_and_functions.zva_set_output_log())

    def data_acquire(
            self):  # Calls scripts_and_functions module function triggered_data_acquisition() to acquire data and
        # create a S3P file
        scripts_and_functions.signal_Generator.write("TRIG")
        scripts_and_functions.time.sleep(2 + float(scripts_and_functions.zva.query_str_with_opc('SENSe1:SWEep:TIME?')))
        scripts_and_functions.triggered_data_acquisition(
            filename=self.text_file_name_s3p_test.get(index1="1.0", index2="end-1c"),
            zva_file_dir=r"C:\Users\Public\Documents\Rohde-Schwarz\ZNA"
                         r"\Traces",
            pc_file_dir=self.test_s3p_dir.get(),
            file_format='s3p')
        self.plot_snp_test(filetype='.s3p')
        scripts_and_functions.print_error_log()
        self.set_txt()

    def data_acquire_s2p(self):
        scripts_and_functions.signal_Generator.write("TRIG")
        scripts_and_functions.time.sleep(2 + float(scripts_and_functions.zva.query_str_with_opc('SENSe1:SWEep:TIME?')))
        scripts_and_functions.triggered_data_acquisition(
            filename=self.text_file_name_s3p_test.get(index1="1.0", index2="end-1c"),
            zva_file_dir=r"C:\Users\Public\Documents\Rohde-Schwarz\ZNA"
                         r"\Traces",
            pc_file_dir=self.test_s3p_dir.get(),
            file_format='s2p')
        self.plot_snp_test(filetype='.s2p')
        scripts_and_functions.print_error_log()
        self.set_txt()

    def data_acquire_s1p(self):
        scripts_and_functions.signal_Generator.write("TRIG")
        scripts_and_functions.time.sleep(2 + float(scripts_and_functions.zva.query_str_with_opc('SENSe1:SWEep:TIME?')))
        scripts_and_functions.triggered_data_acquisition(
            filename=self.text_file_name_s3p_test.get(index1="1.0", index2="end-1c"),
            zva_file_dir=r"C:\Users\Public\Documents\Rohde-Schwarz\ZNA"
                         r"\Traces",
            pc_file_dir=self.test_s3p_dir.get(),
            file_format='s1p')
        self.plot_snp_test(filetype='.s1p')
        scripts_and_functions.print_error_log()
        self.set_txt()

    # signal_Generator Functions -----------------------------------------------------------
    def reset_sig_gen(self):  # Reset signal_Generator using the IP address at Ressource Page (used in TAB4)
        ip = self.sig_gen_inst.get()
        scripts_and_functions.setup_signal_Generator_ramp_with_rst(ip)

    def acquire_pull_down_data(
            self):  # Calls scripts_and_functions module measure_pull_down_voltage() to acquire pull down voltage (
        # used in TAB5)
        # try:
        os.chdir(self.test_pull_in_dir.get())
        scripts_and_functions.measure_pull_down_voltage(
            filename=self.text_file_name_pull_in_test.get(index1="1.0", index2="end-1c"))
        # scripts_and_functions.print_error_log()
        self.set_txt()
        # except:
        #     print("Error")

    def set_pulse_gen(self):  # Configure signal_Generator bias voltage, pulse width and prf (used in TAB5)
        self.set_bias_voltage()
        self.set_prf()
        self.set_pulse_width()
        self.text_snp_debug.delete("1.0", "end")
        self.text_snp_debug.insert(index="%d.%d" % (0, 0), chars=scripts_and_functions.sig_gen_set_output_ramp_log())

    def set_pulse_gen_ramp(
            self):  # Calls set_bias_pull_in() & set_ramp_width() to Configure signal_Generator ramp bias voltage and pulse
        # width (used in TAB4)
        self.set_bias_pull_in()
        self.set_ramp_width()
        self.text4.delete("1.0", "end")
        self.text4.insert(index="%d.%d" % (0, 0), chars=scripts_and_functions.sig_gen_set_output_ramp_log())

    def set_pulse_gen_pulse_mode(
            self):  # Calls scripts_and_functions module's configuration_sig_gen() to reset the signal_Generator and sends an
        # error log (used
        # in TAB7)
        scripts_and_functions.configuration_sig_gen()
        self.text_power_debug.delete("1.0", "end")
        self.text_power_debug.insert(index="%d.%d" % (0, 0), chars=scripts_and_functions.sig_gen_set_output_log())

    def set_bias_voltage(self):
        # Calls scripts_and_functions modules's bias_voltage_s3p() function using the voltage provided by
        # entry pull_in_v as
        # an input (used in TAB5)
        bias = self.pull_in_v.get()
        scripts_and_functions.bias_voltage(bias)
        self.error_log(scripts_and_functions.signal_Generator)

    def set_symmetrical_voltage_bias(self, voltage: str = '10'):
        scripts_and_functions.bias_pull_in_voltage(voltage)
        self.error_log(scripts_and_functions.signal_Generator)

    def set_bias_pull_in(
            self):  # Calls scripts_and_functions modules's bias_voltage_s3p() function using the voltage provided by
        # entry pull_in_v as
        # an input (used in TAB4) !!!!FUNCTION IS LIKELY REDUNDANT!!!!
        bias = self.pull_in_v_bias.get()
        scripts_and_functions.bias_pull_in_voltage(bias)
        self.error_log(scripts_and_functions.signal_Generator)

    def set_ramp_width(self):  # Calls scripts_and_functions module's ramp_width(width) to set ramp width
        width = self.ramp_width.get()
        scripts_and_functions.ramp_width(width)
        self.error_log(scripts_and_functions.signal_Generator)

    def set_prf(self):  # Calls scripts_and_functions modules's set_prf(prf) to set set pulse repetition frequency
        prf = self.pulse_freq.get()
        scripts_and_functions.set_prf(prf)
        self.error_log(scripts_and_functions.signal_Generator)

    def set_pulse_width(self):  # Calls scripts_and_functions modules's set_pulse_width(width) to set pulse width
        width = self.pulse_width.get()
        scripts_and_functions.set_pulse_width(width)
        self.error_log(scripts_and_functions.signal_Generator)

    # Plots functions -------------------------------------------------------------
    def trace_pull_down(self):
        # Measurement function that calls scripts_and_functions Module to trigger signal_Generator to figure pull in trace and
        # display the measurement values in the text_file_name_s3p_test boxes(used in TAB6)
        # try:
        scripts_and_functions.signal_Generator.write('TRIG')
        curve_det = scripts_and_functions.get_curve(channel=4)
        curve_bias = scripts_and_functions.get_curve(channel=2)
        t = curve_det[:, 1]
        rf_detector = -max(3 * curve_det[:, 0] / 0.040) + 3 * curve_det[:, 0] / 0.040
        v_bias = curve_bias[:, 0]
        measurement_values = self.calculate_pull_in_out_voltage_measurement(v_bias, curve_det[:, 0])
        plt.figure(num=4)
        number_of_graphs = len(self.ax_pull_in_meas.get_lines()[0:])
        self.ax_pull_in_meas.plot(v_bias, rf_detector, label='figure n°{}'.format(number_of_graphs))
        self.ax_pull_in_meas.set(xlabel='V_bias (V)')
        self.ax_pull_in_meas.set(ylabel='Isolation (dB)')
        self.ax_pull_in_meas.grid(visible=True)
        self.ax_pull_in_meas.legend(fancybox=True, shadow=True)
        self.canvas_v_pull_in_meas.draw()
        self.text5.delete("1.0", "end")
        self.text6.delete("1.0", "end")
        self.text7.delete("1.0", "end")
        self.text8.delete("1.0", "end")
        self.text9.delete("1.0", "end")
        self.text_iso_pull_out_plus.delete("1.0", "end")
        self.text_iso_pull_in_minus.delete("1.0", "end")
        self.text_iso_pull_out_minus.delete("1.0", "end")
        self.text5.insert(index="%d.%d" % (0, 0), chars=measurement_values['Vpullin_plus'])
        self.text6.insert(index="%d.%d" % (0, 0), chars=measurement_values['Vpullin_minus'])
        self.text7.insert(index="%d.%d" % (0, 0), chars=measurement_values['Vpullout_plus'])
        self.text8.insert(index="%d.%d" % (0, 0), chars=measurement_values['Vpullout_minus'])
        self.text9.insert(index="%d.%d" % (0, 0), chars=measurement_values['Isolation_at_pullin_plus'])
        self.text_iso_pull_out_plus.insert(index="%d.%d" % (0, 0),
                                           chars=measurement_values['Isolation_at_pullout_plus'])
        self.text_iso_pull_in_minus.insert(index="%d.%d" % (0, 0),
                                           chars=measurement_values['Isolation_at_pullin_minus'])
        self.text_iso_pull_out_minus.insert(index="%d.%d" % (0, 0),
                                            chars=measurement_values['Isolation_at_pullout_minus'])
        # except:
        #     print("Error in trace pull down function [Line 905]")

    def plot_s3p(self):  # Display function that calls skrf Module to figure s3p files (used in display TAB)
        entered_filename = self.s3p_file_name_combobox.get()
        print(entered_filename + '\n')
        os.chdir('{}'.format(self.entered_var_s3p.get()))
        s_par_network = rf.Network('{}'.format(entered_filename))
        s_par_network.frequency.unit = 'GHz'
        # freq = s_par_network.frequency
        spar_dict_s3p = {'S11': [0, 0], 'S12': [0, 1], 'S13': [0, 2],
                         'S21': [1, 0], 'S22': [1, 1], 'S23': [1, 2],
                         'S31': [2, 0], 'S32': [0, 0], 'S33': [2, 2]}
        [m, n] = spar_dict_s3p[self.s_parameter_chosen_s3p.get()]
        plt.figure(num=1)
        s_par_network.plot_s_db(m, n)
        self.ax_s3p.set_ylim(ymin=self.scale_amplitude_value.get(), ymax=0)
        self.ax_s3p.set_xlim(xmin=self.scale_frequency_lower_value.get(), xmax=self.scale_frequency_upper_value.get())
        self.ax_s3p.set(ylabel='S{}{} (dB)'.format(m + 1, n + 1))
        self.ax_s3p.grid(visible=True)
        self.ax_s3p.legend(fancybox=True, shadow=True)
        self.s3p_canvas.draw()

    def plot_s2p(self):  # Display function that calls skrf Module to figure s2p files (used in display TAB)
        entered_filename = self.s2p_file_name_combobox.get()
        print(entered_filename + '\n')
        os.chdir('{}'.format(self.entered_var_s2p.get()))
        s_par_network = rf.Network('{}'.format(entered_filename))
        s_par_network.frequency.unit = 'Ghz'
        spar_dict_s2p = {'S11': [0, 0], 'S12': [0, 1],
                         'S21': [1, 0], 'S22': [1, 1], }
        [m, n] = spar_dict_s2p[self.s_parameter_chosen_s2p.get()]
        plt.figure(num=2, tight_layout=True)
        s_par_network.plot_s_db(m, n)
        self.ax_s2p.set_ylim(ymin=self.scale_amplitude_value.get(), ymax=0)
        self.ax_s2p.set_xlim(xmin=self.scale_frequency_lower_value.get(), xmax=self.scale_frequency_upper_value.get())
        self.ax_s2p.set(ylabel='S{}{} (dB)'.format(m + 1, n + 1))
        self.ax_s2p.grid(visible=True)
        self.ax_s2p.legend(fancybox=True, shadow=True)
        self.s2p_canvas.draw()

    def plot_snp_test(self, filetype='.s3p'):
        self.fig_snp_meas.clear()
        self.ax_snp_meas = self.fig_snp_meas.add_subplot(1, 1, 1)
        # Display function that calls skrf Module to figure s1p files (used in SNP test TAB)
        entered_filename = self.text_file_name_s3p_test.get(index1="1.0", index2="end-1c") + filetype
        print(entered_filename + '\n')
        os.chdir('{}'.format(self.test_s3p_dir.get()))
        s_par_network = rf.Network('{}'.format(entered_filename))
        s_par_network.frequency.unit = 'GHz'
        plt.figure(num=5, tight_layout=True)
        s_par_network.plot_s_db()
        self.ax_snp_meas.grid(visible=True)
        self.ax_snp_meas.legend(fancybox=True, shadow=True)
        self.canvas_snp_meas.draw()

    def plot_vpull_in(self):  # Display function to figure Isolation vs pull in voltage files (used in display TAB)
        f = self.txt_file_name_combobox.get()
        os.chdir('{}'.format(self.pull_in_dir_name.get()))
        with open(f, newline=''):
            data_np = np.loadtxt(f, delimiter=',', unpack=True, skiprows=1)
            v_bias = data_np[:, 0].copy()
            print(v_bias, end='\n')
            v_log_amp = data_np[:, 1].copy()
            max_iso = np.max(3 * v_log_amp / 0.040)
            min_iso = np.min(3 * v_log_amp / 0.040) - 3
            max_v_bias = np.max(v_bias)
            iso = 3 * v_log_amp / 0.040 - max_iso
            plt.figure(num=3)
            self.ax_pull_in.plot(v_bias, iso,
                                 label="{}".format(f)[:-4])  # removesuffixe non fonctionnel dans python 3.6
            self.ax_pull_in.set_ylim(ymin=self.scale_isolation_value.get(), ymax=0)
            self.ax_pull_in.set_xlim(xmin=-self.scale_voltage_value.get(), xmax=self.scale_voltage_value.get())
            self.ax_pull_in.set(ylabel='Isolation (dB)')
            self.ax_pull_in.grid(visible=True)
            self.ax_pull_in.legend(fancybox=True, shadow=True)
            self.canvas_v_pull_in_display.draw()

    def calculate_pull_in_out_voltage(
            self):  # Display function to calculate pull in/out voltages and associated Isolation values (used in
        # display TAB)
        self.text_scroll.delete('1.0', tk.END)
        f = self.txt_file_name_combobox.get()
        with open(f, newline=''):
            data_np = np.loadtxt(f, delimiter=',', unpack=True, skiprows=1)
            v_bias = data_np[:, 0].copy()
            v_log_amp = data_np[:, 1].copy()
            # Acquiring the indexes that correspond to both positive and negative bias triangles
            # The indexes are extracted by slicing voltages (for positive bias) > 2V and <-2 V (for negative bias)
            positive_bias = np.extract((v_bias > 2), v_bias)
            negative_bias = np.extract((v_bias < -2), v_bias)

            print(f'positive bias array:\n {positive_bias}\nnegative bias array:\n{negative_bias}')

            # Position of the first positive bias index along v_bias array
            first_index_pos = np.where(v_bias == positive_bias[0])[0]
            print(f'first index pos array={first_index_pos}')
            # Position of the first negative bias index along v_bias array
            first_index_neg = np.where(v_bias == negative_bias[0])[0]
            print(f'first index neg array={first_index_neg}')
            # Position of the last negative bias index along v_bias array
            last_index_neg = np.where(v_bias == negative_bias[-1])[0]
            # Calculating the max and min indexes in both casses
            max_positive_bias_index = np.argmax(positive_bias)
            min_positive_bias_index = 0
            max_negative_bias_index = 0
            min_negative_bias_index = np.argmin(negative_bias)

            # Creating the ascent and descent portion of the graph for v_bias and v_log converted to normalized
            # isolation
            positive_ascent = positive_bias[0:max_positive_bias_index]
            positive_descent = positive_bias[max_positive_bias_index:len(positive_bias)]

            # Calculating normalized isolation factor
            normalize_iso = np.max(3 * v_log_amp[first_index_pos[0]:max_positive_bias_index] / 0.040)

            iso_ascent = 3 * v_log_amp[
                             first_index_pos[0]:first_index_pos[0] + max_positive_bias_index] / 0.040 - normalize_iso
            iso_max_ascent = np.min(iso_ascent)

            iso_descent = 3 * v_log_amp[first_index_pos[0] + max_positive_bias_index:first_index_pos[0] + len(
                positive_bias)] / 0.040 - normalize_iso
            iso_min_descent = np.min(iso_descent)
            # ==============================================================================
            # Calculation Vpull in as isolation passing below 90% max isolation in dB mark
            # Calculation Vpull out as isolation passing above 90% max isolation in dB mark
            pullin_index_pos = int(np.where(iso_ascent <= 0.9 * iso_max_ascent)[0][0])
            vpullin = positive_bias[pullin_index_pos]

            tenpercent_iso = 0.1 * iso_min_descent
            ninetypercent_iso = 0.9 * iso_max_ascent
            try:
                pullout_index_pos = int(np.where(iso_descent >= 0.1 * iso_min_descent)[0][0])
                vpullout = positive_bias[max_positive_bias_index + pullout_index_pos]
            except IndexError as e:
                print({e.args}, end='\n')
                pullout_index_pos = int(len(iso_descent) - 1)
                vpullout = positive_bias[max_positive_bias_index + pullout_index_pos]
            # ============================================================================== Creating the ascent and
            # descent portion of the graph for v_bias and v_log converted to normalized isolation
            negative_descent = negative_bias[0:min_negative_bias_index]
            negative_ascent = negative_bias[min_negative_bias_index:len(negative_bias)]

            # Calculating normalized isolation factor
            normalized_iso_minus = np.max(3 * v_log_amp[first_index_neg[0]:first_index_neg[
                                                                               0] + min_negative_bias_index] / 0.040)
            # This is extracted from the detector V/dB characteristics

            iso_descent_minus = 3 * v_log_amp[
                                    first_index_neg[0]:first_index_neg[0] + min_negative_bias_index] / (
                                        0.040 - normalized_iso_minus)
            iso_min_descent_minus = np.min(iso_descent_minus)
            print(
                f'first_index_neg={first_index_neg[0]}\nmin_negative_bias_index={min_negative_bias_index}'
                f'\nlast_index_neg={last_index_neg[0]}')
            iso_ascent_minus = 3 * v_log_amp[first_index_neg[0] + min_negative_bias_index:last_index_neg[
                -1]] / 0.040 - normalized_iso_minus
            try:
                iso_min_ascent = np.min(iso_ascent_minus)
            except ValueError as e:
                print('Value ERROR')

            # Calculation Vpull in negative as isolation passing below 90% max isolation in dB mark (downwards)
            # Calculation Vpull out negative as isolation passing above 10% off isolation in dB mark (upwards)
            try:
                pullin_index_minus = int(np.where(iso_descent_minus <= 0.9 * iso_min_descent)[0][0])
                vpullin_minus = negative_bias[pullin_index_minus]
            except IndexError as e:
                print({e.args}, end='\n')
            pullin_index_minus = int(len(iso_descent_minus) - 1)
            vpullin_minus = negative_bias[pullin_index_minus]

            tenpercent_iso_ascent = 0.1 * iso_min_ascent
            ninetypercent_iso_descent = 0.9 * iso_min_descent

            pullout_index_minus = int(np.where(iso_ascent_minus >= 0.1 * iso_min_ascent)[0][0])
            vpullout_minus = negative_bias[min_negative_bias_index + pullout_index_minus]
            # print('vpullin = {} | Isolation measured = {}\nvpullout = {} | Isolation measured = {} \nvpullin_minus
            # = {} | Isolation measured = {}\nVpullout_minus = {} | Isolation measured = {} \n'.format(vpullin,
            # ninetypercent_iso, vpullout, tenpercent_iso, vpullin_minus, ninetypercent_iso_descent, vpullout_minus,
            # tenpercent_iso_ascent))

            self.text_scroll.insert(index="%d.%d" % (1, 0),
                                    chars='Isolation_at_pullout_minus = {} dB \n'.format(
                                        round(tenpercent_iso_ascent, ndigits=2)))
            self.text_scroll.insert(index="%d.%d" % (1, 0),
                                    chars='vpullout_minus = {} V | \t'.format(round(vpullout_minus, ndigits=2)))

            self.text_scroll.insert(index="%d.%d" % (1, 0),
                                    chars='Isolation_at_pullin_minus = {} dB \n'.format(
                                        round(ninetypercent_iso_descent, ndigits=2)))
            self.text_scroll.insert(index="%d.%d" % (1, 0),
                                    chars='vpullin_minus = {} V | \t'.format(round(vpullin_minus, ndigits=2)))

            self.text_scroll.insert(index="%d.%d" % (1, 0),
                                    chars='Isolation_at_pullout_plus = {} dB  \n'.format(
                                        round(tenpercent_iso, ndigits=2)))
            self.text_scroll.insert(index="%d.%d" % (1, 0),
                                    chars='Vpullout_plus = {} V | \t'.format(round(vpullout, ndigits=2)))

            self.text_scroll.insert(index="%d.%d" % (1, 0),
                                    chars='Isolation_at_pullin_plus = {} dB \n'.format(
                                        round(ninetypercent_iso, ndigits=2)))
            self.text_scroll.insert(index="%d.%d" % (1, 0),
                                    chars='Vpullin_plus = {} V | \t'.format(round(vpullin, ndigits=2)))

            pull_dict = {'Vpullin_plus': vpullin, 'Vpullout_plus': vpullout,
                         'Isolation_at_pullin_plus': ninetypercent_iso, 'Isolation_at_pullout_plus': tenpercent_iso,
                         'vpullin_minus': vpullin_minus, 'vpullout_minus': vpullout_minus,
                         'Isolation_at_pullin_minus': ninetypercent_iso_descent,
                         'Isolation_at_pullout_minus': tenpercent_iso_ascent}
            return pull_dict

    def delete_axs_s3p(self):  # Delete last drawn line in s3p display tab (in ax_s3p)
        try:
            list_graph_ax = self.ax_s3p.lines[-1]
            list_graph_ax.remove()
            self.ax_s3p.legend(fancybox=True).remove()
            self.s3p_canvas.draw()
        except IndexError:
            print("No more graphs to delete")

    def delete_axs_s2p(self):  # Delete last drawn line in s2p display tab (in ax_s2p)
        try:
            list_graph_ax2 = self.ax_s2p.lines[-1]
            list_graph_ax2.remove()
            self.ax_s2p.legend(fancybox=True).remove()
            self.s2p_canvas.draw()
        except IndexError as ind:
            print(f"No more graphs to delete\n{ind}")

    def delete_axs_vpullin(self):  # Delete last drawn line in pull in graph display tab (in ax_pull_in)
        try:
            list_graph_ax3 = self.ax_pull_in.lines[-1]
            list_graph_ax3.remove()
            self.ax_pull_in.legend(fancybox=True).remove()
            self.canvas_v_pull_in_display.draw()
        except IndexError:
            print("No more graphs to delete")

    def update_ylim(self):
        value = self.scale_amplitude_value.get()
        self.ax_s3p.set_ylim(ymin=0, ymax=value)
        self.plot_s3p()
        self.ax_s3p.grid(visible=True)

    def update_xlim(self):
        value = self.scale_frequency_upper_value.get()
        value2 = self.scale_frequency_lower_value.get()
        self.plot_s3p()
        self.ax_s3p.set_xlim(xmin=value2, xmax=value)
        self.ax_s3p.grid(visible=True)

    def set_txt(self):  # (used in TAB5)
        # self.text_snp_debug.delete(index1="%d.%d" % (1, 0), index2="%d.%s" % (1, 'end'))
        self.text_snp_debug.delete("1.0", "end")
        self.text4.delete("1.0", "end")
        error_logs = scripts_and_functions.print_error_log()
        self.text_snp_debug.insert(index="%d.%d" % (0, 0), chars=error_logs)
        self.text4.insert(index="%d.%d" % (0, 0), chars=error_logs)

    def error_log(self, resource):
        error_log_resource = resource.query('SYSTem:ERRor?')
        time.sleep(1)
        error_string_resource = error_log_resource.split(",")[1]
        resource_name = resource.query('*IDN?').split(",")[:2]
        error_output = '{} ERROR LOG: {}\n'.format(resource_name, error_string_resource)
        self.text_snp_debug.delete("1.0", "end")
        self.text_snp_debug.insert(index="%d.%d" % (0, 0), chars=error_output)
        self.text4.delete("1.0", "end")
        self.text4.insert(index="%d.%d" % (0, 0), chars=error_output)
        return error_output

    def calculate_pull_in_out_voltage_measurement(self, v_bias,
                                                  v_log_amp):  # same function as in display implemented in measurement
        self.text4.delete('1.0', tk.END)
        list_graph_ax4 = self.ax_pull_in_meas.lines[:]
        if not (list_graph_ax4 == []):
            list_graph_ax4[-1].remove()
        self.ax_pull_in_meas.legend(fancybox=True)
        self.s2p_canvas.draw()

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
        # Calculating the max and min indexes in both cases
        max_positive_bias_index = np.argmax(positive_bias)
        min_positive_bias_index = 0
        max_negative_bias_index = 0
        min_negative_bias_index = np.argmin(negative_bias)

        # Creating the ascent and descent portion of the graph for v_bias and v_log converted to normalized isolation
        positive_ascent = positive_bias[0:max_positive_bias_index]
        positive_descent = positive_bias[max_positive_bias_index:len(positive_bias)]

        # Calculating normalized isolation factor
        normalize_iso = np.max(3 * v_log_amp[first_index_pos[0]:max_positive_bias_index] / 0.040)

        iso_ascent = 3 * v_log_amp[
                         first_index_pos[0]:first_index_pos[0] + max_positive_bias_index] / 0.040 - normalize_iso
        iso_max_ascent = np.min(iso_ascent)

        iso_descent = 3 * v_log_amp[first_index_pos[0] + max_positive_bias_index:first_index_pos[0] + len(
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
        normalized_iso_minus = np.max(3 * v_log_amp[first_index_neg[0]:first_index_neg[
                                                                           0] + min_negative_bias_index] / 0.040)
        # This is extracted from the detector V/dB characteristics

        iso_descent_minus = 3 * v_log_amp[first_index_neg[0]:first_index_neg[0] + min_negative_bias_index] / (
                0.040 - normalized_iso_minus)
        iso_min_descent_minus = np.min(iso_descent_minus)

        iso_ascent_minus = 3 * v_log_amp[first_index_neg[0] + min_negative_bias_index:last_index_neg[
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
        # print('Vpullin = {} | Isolation measured = {}\nVpullout = {} | Isolation measured = {} \nVpullin_minus = {}
        # | Isolation measured = {}\nVpullout_minus = {} | Isolation measured = {} \n'.format(Vpullin,
        # ninetypercent_iso, Vpullout, tenpercent_iso, Vpullin_minus, ninetypercent_iso_descent, Vpullout_minus,
        # tenpercent_iso_ascent))

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
        return pull_dict

    def send_trig(self):
        scripts_and_functions.trigger_measurement_zva()
        self.error_log(scripts_and_functions.signal_Generator)

    def sig_gen_cycling_config(self):
        scripts_and_functions.signal_Generator_cycling_config()
        time.sleep(3)
        self.error_log(scripts_and_functions.signal_Generator)

    def cycling_test(self):
        print("Started cycling")
        scripts_and_functions.cycling_sequence(number_of_cycles=(self.test_cycling_var_nb_cycles.get()) * 1e5,
                                               number_of_pulses_in_wf=1000, filename=r'{}-{}-{}-{}-{}'.format(
                self.test_cycling_project.get(), self.test_cycling_ret.get(), self.test_cycling_cell.get(),
                self.test_cycling_device.get(), self.test_cycling_var_nb_cycles.get(), self.test_cycling_var_bias.get()
            ), events=self.test_cycling_events.get(), df_path=self.test_cycling_dir.get(), figure=self.fig_cycling)


# Main ------------------------------------------------------------------------
app = Window()
# fonts = list(font.families())
app.mainloop()
# Main ------------------------------------------------------------------------
