# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 14:31:59 2022
This Tkinter app can get S3P & S2P files in a directory and display them
after selection
@author: T0188303
_version :10
"""
import os
import tkinter as tk
import tkinter.ttk
from tkinter import Menu
import time
# from tkinter import font
from tkinter import scrolledtext
from tkinter import ttk
from tkinter.ttk import Notebook
from typing import Optional, Literal, Type
import pandas as pd
# Implement the default Matplotlib key bindings.
# import matplotlib.pyplot as plt
import numpy as np
import skrf as rf
import matplotlib.pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import scripts_and_functions
import dir_and_var_declaration
import threading  # Import threading module
from matplotlib.ticker import FuncFormatter

# ==============================================================================
# Imports
# ==============================================================================
import scripts_and_functions

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
    notebook.grid(column=col, row=row, sticky="NSEW")

    # Return the created tab (frame) instance.
    return tab_inst


def add_button(tab: ttk.LabelFrame | ttk.Frame, button_name: str, command, col: int, row: int) -> ttk.Button:
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
        action.after(ms=500, func=lambda: action.configure(style='Centered.TButton'))

    # Create a style for the centered button text.
    style = ttk.Style()
    style.configure('Centered.TButton', anchor='center', padding=1, justify='center')
    style.configure('Pressed.TButton', background='blue', anchor='center', padding=1, justify='center')

    # Create a Button widget with the specified text and additional configurations.
    action = ttk.Button(
        tab,  # The parent LabelFrame where the button is added.
        text=button_name,  # The text displayed on the button.
        command=on_press,  # The function to be executed on button press.
        width=len(button_name),  # Set the button width to the length of the button name.
        style='Centered.TButton'  # Set the initial style.
    )

    # Place the Button widget at the specified column and row in the LabelFrame.
    action.grid(column=col, row=row, sticky="nsew")

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
    button.after(ms=500, func=update_text_back)

    return button


def add_label(tab: ttk.LabelFrame | ttk.Frame, label_name: str, col: int, row: int) -> ttk.Label:
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


def add_entry(tab: ttk.LabelFrame | ttk.Frame, text_var: tk.StringVar | tk.DoubleVar, width: int, col: int,
              row: int) -> ttk.Entry:
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
        pc_file=dir_and_var_declaration.zva_parameters["setup_s3p"],  # Path to the s3p configuration file on the PC.
        inst_file=dir_and_var_declaration.zva_parameters["instrument_file"]  # Path to the instrument file location.
    )


def call_s2p_config():
    """
    Calls the load_config function to load the s2p configuration file to the instrument.
    Uses predefined file paths from the dir_and_var_declaration module.
    """
    # Call the load_config function with predefined file paths for the s2p configuration.
    scripts_and_functions.load_config(
        pc_file=dir_and_var_declaration.zva_parameters["setup_s2p"],  # Path to the s2p configuration file on the PC.
        inst_file=dir_and_var_declaration.zva_parameters["instrument_file"]  # Path to the instrument file location.
    )


def call_s1p_config():
    """
    Calls the load_config function to load the s1p configuration file to the instrument.
    Uses predefined file paths from the dir_and_var_declaration module.
    """
    # Call the load_config function with predefined file paths for the s1p configuration.
    scripts_and_functions.load_config(
        pc_file=dir_and_var_declaration.zva_parameters["setup_s1p"],  # Path to the s1p configuration file on the PC.
        inst_file=dir_and_var_declaration.zva_parameters["instrument_file"]  # Path to the instrument file location.
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


def create_canvas(figure: plt.Figure, frame: ttk.LabelFrame | ttk.Frame,
                  toolbar_frame: Optional[ttk.LabelFrame | ttk.Frame] = None,
                  toolbar: Optional[bool] = True) -> FigureCanvasTkAgg:
    """
    Creates display Canvas in the specified frame, and optionally adds a toolbar.

    Parameters:
    figure (plt.Figure): The matplotlib figure to be displayed on the canvas.
    frame (ttk.Frame): The parent frame where the canvas is to be added.
    toolbar_frame (ttk.Frame, optional): The frame where the toolbar is to be added.
    If None, toolbar is added to the same frame as the canvas.
    toolbar (bool, optional): Whether to add a navigation toolbar. Default is True.

    Returns:
    FigureCanvasTkAgg: The created canvas with the matplotlib figure.
    """
    # Create a FigureCanvasTkAgg widget with the specified figure and parent frame.
    canvas = FigureCanvasTkAgg(figure, master=frame)

    # Pack the canvas widget with specified padding.
    canvas.get_tk_widget().pack(ipady=2, ipadx=2, expand=True, fill=tk.BOTH, side="right", anchor=tk.CENTER)

    # Optionally add a navigation toolbar.
    if toolbar:
        if toolbar_frame is None:
            toolbar_frame = frame  # Use the same frame if no separate toolbar frame is provided
        toolbar_widget = NavigationToolbar2Tk(canvas=canvas, window=toolbar_frame)
        toolbar_widget.update()

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


def create_figure(num: int, figsize: tuple[float, float]):
    """Helper method to create a matplotlib figure."""
    return plt.figure(num=num, dpi=100, tight_layout=True, figsize=figsize, frameon=True)


def create_figure_with_axes(num: int, figsize: tuple[float, float]):
    """Helper method to create a matplotlib figure and its axes."""
    fig = create_figure(num, figsize)
    ax = fig.add_subplot(1, 1, 1)
    ax.grid()
    return fig, ax


def add_slider(frame, _from, to, name, variable, step, orientation: Literal["horizontal", "vertical"] = tk.HORIZONTAL):
    slider_frame = ttk.Frame(frame)
    slider_frame.pack(pady=10)

    if orientation == tk.VERTICAL:
        # Create a canvas for the vertical text
        canvas = tk.Canvas(slider_frame, width=20, height=250)
        canvas.create_text(10, 125, text=name, angle=90, font=('Bahnschrift Light', 10))
        canvas.pack(side=tk.LEFT, padx=5, pady=5)

        # Create the vertical slider
        slider = tk.Scale(master=slider_frame, from_=_from, to=to, orient=orientation, length=250, digits=2,
                          relief=tk.GROOVE, border=2, sliderrelief=tk.RIDGE, tickinterval=step, variable=variable,
                          font=('Bahnschrift Light', 10))
        slider.pack(side=tk.RIGHT, padx=5, pady=5)
    else:
        # Create the horizontal slider with a label
        slider = tk.Scale(master=slider_frame, from_=_from, to=to, orient=orientation, label=name, length=250, digits=2,
                          relief=tk.GROOVE, border=2, sliderrelief=tk.RIDGE, tickinterval=step, variable=variable,
                          font=('Bahnschrift Light', 10))
        slider.pack()

    # Center the frame within the parent frame
    slider_frame.pack(side="left", anchor=tk.CENTER)

    return slider


def add_small_scale(frame, name, col, row):
    label = ttk.Label(frame, text=name)
    # label.grid(column=col, row=row, padx=5, pady=5)

    # Create a scale with a smaller length
    scale = ttk.Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL, length=100)
    # scale.grid(column=col + 1, row=row, padx=5, pady=5)

    # Use padding to adjust the appearance
    scale.configure(style="TScale")
    s = ttk.Style()
    s.configure(style="TScale", thickness=10)  # Adjust thickness as needed
    return scale


class Window(tk.Tk):
    """
    Main application class for handling SNP file display and acquisition.
    The app controls VNAs ZVA50 & ZVA67, the powermeter A-33521B, the RF generator RS SMB100a, and oscilloscope DPO DPO5054.

    This class inherits from tk.Tk to provide a main application window.
    It initializes the GUI components and binds the necessary event handlers.
    """

    def __init__(self, master: Optional[tk.Tk] = None):
        super().__init__()
        self.master = master
        # Declare figures and axes
        self.sig_gen_inst: tk.StringVar
        self.text_snp_debug: tk.Text
        self.text_file_name_s3p_test: tk.Text
        self.canvas_v_pull_in_meas: tk.Canvas
        self.text_file_name_s3p_test: tk.Text
        self.text_iso_pull_out_minus_test: tk.Text
        self.text_iso_pull_in_minus_test: tk.Text
        self.text_iso_pull_out_plus_test: tk.Text
        self.text_pull_out_plus_test: tk.Text
        self.text_pull_out_minus_test: tk.Text
        self.text_pull_in_minus_test: tk.Text
        self.text_iso_pull_in_plus_test: tk.Text
        self.text_pull_in_plus_test: tk.Text
        self.text_iso_pull_out_minus: tk.Text
        self.text_iso_pull_in_minus: tk.Text
        self.text_iso_pull_out_plus: tk.Text
        self.canvas_v_pull_in_meas: tk.Canvas
        self.pull_in_v: tk.DoubleVar
        self.text_gen_controls_pull_in_debug: tk.Text
        self.test_cycling_var_bias: tk.StringVar
        self.test_cycling_var_nb_cycles: tk.DoubleVar
        self.test_cycling_ret: tk.StringVar
        self.test_cycling_project: tk.StringVar
        self.test_cycling_events: tk.DoubleVar
        self.test_pull_in_dir: tk.StringVar
        self.text_file_name_pull_in_test: tk.Text
        self.text_file_name_s3p_test: tk.Text
        self.test_s3p_dir: tk.StringVar
        self.nb_points: tk.DoubleVar
        self.text_gen_controls_pull_in_debug: tk.Text
        self.text_snp_debug: tk.Text
        self.zva_inst: tk.StringVar
        self.scale_frequency_lower_value: tk.DoubleVar
        self.scale_frequency_upper_value: tk.DoubleVar
        self.scale_isolation_value: tk.DoubleVar
        self.scale_voltage_value: tk.DoubleVar
        self.scale_amplitude_value: tk.DoubleVar
        self.s_parameter_s2p: tk.StringVar
        self.s_parameter_s3p: tk.StringVar
        self.tabControl: ttk.Notebook
        self.fig_s3p: plt.figure
        self.ax_s3p: plt.axes
        self.fig_s2p: plt.axes
        self.ax_s2p: plt.axes
        self.fig_pull_in: plt.figure
        self.ax_pull_in: plt.axes
        self.fig_pull_in_meas: plt.figure
        self.ax_pull_in_meas: plt.axes
        self.fig_snp_meas: plt.figure
        self.ax_snp_meas: plt.axes
        self.fig_cycling: plt.figure
        self.ax_cycling_pull_in: plt.axes
        self.ax_cycling_pull_out: plt.axes
        self.ax_cycling_isolation: plt.axes
        self.ax_cycling_insertion_loss: plt.axes
        self.ax_cycling_t_down: plt.axes
        self.ax_cycling_t_up: plt.axes
        self.fig_power_meas: plt.figure
        self.ax_power_meas: plt.axes
        self.nb_points: tk.DoubleVar
        self.text_file_name_s3p_test: tk.Text
        self.canvas_cycling: FigureCanvasTkAgg

        self.file_df = pd.DataFrame(columns=["vpullin_plus", "vpullin_minus", "vpullout_plus", "vpullout_minus",
                                             "iso_ascent", "iso_descent_minus", "switching_time",
                                             "amplitude_variation", "release_time", "cycles", "sticking events"])

        self.file_power_sweep = pd.DataFrame(columns=['Power Input DUT Avg (dBm)', 'Power Output DUT Avg (dBm)'])

        self.update_interval = 5000  # Update interval in milliseconds

        self.is_cycling = False
        self.is_power_sweeping = False
        # Configure styles
        self.zva_inst = None
        self.configure_window()

        # Initialize figures and axes
        self.init_figures()

        # Initialize variables
        self.init_variables()

        # Set up tabs
        self.setup_tabs()

        # Create the menu bar
        self.menubar()

        # Create an event to signal new data availability
        self.new_data_event = threading.Event()
        self.new_data_event_power_sweep = threading.Event()
        self.data_thread = threading.Thread(target=self.run_new_data_event)
        self.data_thread.daemon = True  # Ensures the thread will close when the main program exits
        self.data_thread.start()

    def configure_window(self):
        s = ttk.Style()
        s.configure(style='.', font=('Bahnschrift Light', 10))

        # Set window properties
        self.title(f"SUMMIT 11K Machine Interface v{_version}")
        self.resizable(width=True, height=True)

        # Initialize the tab control
        self.tabControl = ttk.Notebook(self)

    def init_figures(self):
        """Initialize all the matplotlib figures and their respective axes."""
        self.fig_s3p, self.ax_s3p = create_figure_with_axes(num=1, figsize=(13, 4.1))
        self.ax_s3p.set_title("|Sij| vs frequency")
        self.fig_s2p, self.ax_s2p = create_figure_with_axes(num=2, figsize=(13, 4.1))
        self.ax_s2p.set_title("|Sij| vs frequency")
        self.fig_pull_in, self.ax_pull_in = create_figure_with_axes(num=3, figsize=(13, 3.5))
        self.ax_pull_in.set(xlabel="V_bias (V)", ylabel="Isolation (dB)", title="Isolation vs Bias voltage")
        self.ax_s2p.set(xlabel="Frequency (Hz)", ylabel="S Parameter (dB)", title="S Parameter vs Frequency")
        self.ax_s3p.set(xlabel="Frequency (Hz)", ylabel="S Parameter (dB)", title="S Parameter vs Frequency")

        self.fig_pull_in_meas, self.ax_pull_in_meas = create_figure_with_axes(num=4, figsize=(6.5, 6))
        self.fig_snp_meas, self.ax_snp_meas = create_figure_with_axes(num=5, figsize=(6.5, 6))
        self.fig_cycling = create_figure(num=6, figsize=(10, 6))
        self.fig_power_meas = create_figure(num=7, figsize=(6.5, 6))

        self.create_cycling_axes()
        self.create_power_sweeping_axes()

    def create_power_sweeping_axes(self):
        self.ax_power_meas = self.fig_power_meas.add_subplot(1, 1, 1)
        self.ax_power_meas.set(xlabel="Pin (dBm)", ylabel="Pout (dBm)", title="Pout vs Pin")
        self.ax_power_meas.set_xscale('linear')
        self.ax_power_meas.grid("both")
        self.ax_power_meas_secondary = self.ax_power_meas.twinx()
        self.ax_power_meas_secondary.set_ylabel('Loss (dB)')

    def create_cycling_axes(self):
        """Create and configure axes for the cycling figure."""
        self.ax_cycling_pull_in = self.fig_cycling.add_subplot(3, 2, 1)
        self.ax_cycling_pull_in.set(xlabel="Cycles", ylabel="Pull-in (V)", title="Pull-in Voltage")
        self.ax_cycling_pull_in.set_xscale('log')
        self.ax_cycling_pull_in.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        self.ax_cycling_pull_out = self.fig_cycling.add_subplot(3, 2, 2)
        self.ax_cycling_pull_out.set(xlabel="Cycles", ylabel="Pull-out (V)", title="Pull-out Voltage")
        self.ax_cycling_pull_out.set_xscale('log')
        self.ax_cycling_pull_out.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        self.ax_cycling_isolation = self.fig_cycling.add_subplot(3, 2, 3)
        self.ax_cycling_isolation.set(xlabel="Cycles", ylabel="Isolation (dB)", title="Isolation")
        self.ax_cycling_isolation.set_xscale('log')
        self.ax_cycling_isolation.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        self.ax_cycling_insertion_loss = self.fig_cycling.add_subplot(3, 2, 4)
        self.ax_cycling_insertion_loss.set(xlabel="Cycles", ylabel="Insertion loss variation (dB)",
                                           title="Insertion loss variation")
        self.ax_cycling_insertion_loss.set_xscale('log')
        self.ax_cycling_insertion_loss.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        self.ax_cycling_t_down = self.fig_cycling.add_subplot(3, 2, 5)
        self.ax_cycling_t_down.set(xlabel="Cycles", ylabel="ts_down (s)", title="Down state switching time")
        self.ax_cycling_t_down.set_xscale('log')
        self.ax_cycling_t_down.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        self.ax_cycling_t_up = self.fig_cycling.add_subplot(3, 2, 6)
        self.ax_cycling_t_up.set(xlabel="Cycles", ylabel="ts_up (s)", title="Up state switching time")
        self.ax_cycling_t_up.set_xscale('log')
        self.ax_cycling_t_up.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        for ax in self.fig_cycling.axes:
            ax.grid()

    def init_variables(self):
        """Initialize Tkinter variables."""
        self.s_parameter_s3p = tk.StringVar(value='S11')
        self.s_parameter_s2p = tk.StringVar(value='S11')

        self.scale_amplitude_value = tk.DoubleVar(value=-20)
        self.scale_voltage_value = tk.DoubleVar(value=40)
        self.scale_isolation_value = tk.DoubleVar(value=-20)
        self.scale_frequency_upper_value = tk.DoubleVar(value=2 * 10e9)
        self.scale_frequency_lower_value = tk.DoubleVar(value=0.1 * 10e9)

        self.ax_s3p.set_ylim(ymin=self.scale_amplitude_value.get(), ymax=0)
        self.ax_s3p.set_xlim(xmin=0, xmax=self.scale_frequency_upper_value.get())

    def setup_tabs(self):
        """Set up the tabs in the notebook."""
        tab_s3p = add_tab(tab_name=' S3P Files ', notebook=self.tabControl, col=0, row=1)  # s3p Tab display
        tab_s2p = add_tab(tab_name=' S2P Files ', notebook=self.tabControl, col=0, row=1)  # s2p Tab display
        tab_pull_in = add_tab(tab_name=' Pull-in Files ', notebook=self.tabControl, col=0, row=1)  # Pull-in Tab display
        tab_pull_in_meas = add_tab(tab_name=' Pull-in Test ', notebook=self.tabControl, col=0, row=1)  # Pull-in Tab
        tab_snp_meas = add_tab(tab_name=' SNP Test ', notebook=self.tabControl, col=0, row=1)  # s3p test Tab
        tab_power_meas = add_tab(tab_name=' Power Test ', notebook=self.tabControl, col=0, row=1)  # Power test Tab
        tab_cycling = add_tab(tab_name=' Cycling tab ', notebook=self.tabControl, col=0, row=1)  # Cycling test Tab
        tab_resources = add_tab(tab_name=' Resource Page ', notebook=self.tabControl, col=0, row=1)  # s3p test Tab

        def setup_s3p_display_tab():
            """
            Set up the S3P tab with all related widgets and frames.
            """

            # TAB1 S3P parameter display
            frame_s3p_directory = add_label_frame(tab_s3p, frame_name='s3p Directory', col=0, row=0)  # s3p Frame
            frame_s3p_display = add_label_frame(tab_s3p, frame_name='s3p Display', col=0, row=1)
            frame_s3p_sliders = add_label_frame(tab_s3p, frame_name='Frequency Range', col=0, row=2)

            # Adding String variables
            self.s3p_dir_name = tk.StringVar(
                value=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\S3P')  # Entry variable for s3p dir
            self.s_parameter_s3p = tk.StringVar(value='S11')  # Entry variable for s parameter dir

            # Adding labels and frame_s3p_display
            add_label(frame_s3p_directory, label_name='Directory', col=1, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                                      ipady=tab_pad_x)
            add_label(frame_s3p_directory, label_name='File', col=1, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                                 ipady=tab_pad_x)
            add_label(frame_s3p_directory, label_name='S parameter', col=1, row=3).grid(sticky='e',
                                                                                        ipadx=tab_pad_x,
                                                                                        ipady=tab_pad_x)
            # Adding entry for file directory
            self.entered_var_s3p = add_entry(frame_s3p_directory, text_var=self.s3p_dir_name, width=70, col=2,
                                             row=1)
            file_s3p = filetypes_dir(self.entered_var_s3p.get())[0]
            self.s3p_file_name_combobox = add_combobox(frame_s3p_directory, text=file_s3p, col=2, row=2, width=100)
            self.s_parameter_chosen_s3p = add_combobox(frame_s3p_directory, text=self.s_parameter_s3p, col=2, row=3,
                                                       width=100)
            self.s_parameter_chosen_s3p['values'] = ('S11', 'S12', 'S13', 'S21', 'S22', 'S23', 'S31', 'S32', 'S33')

            self.button_file_update = add_button(tab=frame_s3p_directory, button_name='Update Files',
                                                 command=lambda: [
                                                     update_entries(directory=self.entered_var_s3p.get(),
                                                                    combobox=self.s3p_file_name_combobox,
                                                                    filetype='.s3p'),
                                                     update_button(self.button_file_update)], col=3,
                                                 row=1)
            # Adding buttons
            add_button(tab=frame_s3p_directory, button_name='Exit',
                       command=self._quit, col=5, row=1)
            add_button(tab=frame_s3p_directory, button_name='Plot', command=self.plot_s3p,
                       col=3, row=3)
            add_button(tab=frame_s3p_directory, button_name='Delete graphs', command=self.delete_axs_s3p, col=3,
                       row=2)
            # Canvas creation
            self.s3p_canvas = create_canvas(figure=self.fig_s3p, frame=frame_s3p_display,
                                            toolbar_frame=frame_s3p_sliders)

            # Sliders creation
            self.slider_amplitude = add_slider(frame=frame_s3p_display, _from=0, to=-50,
                                               name="Amplitude (dB)",
                                               variable=self.scale_amplitude_value, step=5, orientation=tk.VERTICAL)
            self.slider_frequency = add_slider(frame=frame_s3p_sliders, _from=1e9, to=50e9,
                                               name="Upper Frequency Limit (Hz)",
                                               variable=self.scale_frequency_upper_value, step=10e9)
            self.slider_lower_frequency = add_slider(frame=frame_s3p_sliders, _from=1e9, to=50e9,
                                                     name="Lower Frequency Limit (Hz)",
                                                     variable=self.scale_frequency_lower_value, step=10e9)
            self.slider_amplitude.pack(side='left', anchor="center")
            self.slider_frequency.pack(side='right')
            self.slider_lower_frequency.pack(side='left')

        def setup_s2p_display_tab():
            # TAB2 S2P parameter display
            frame_s2p_dir = add_label_frame(tab_s2p, 's2p Directory', 0, 0)  # s2p Frame
            frame_s2p_display = add_label_frame(tab_s2p, frame_name='s2p Display', col=0, row=1)
            frame_s2p_sliders = add_label_frame(tab_s2p, frame_name='Frequency Range', col=0, row=2)

            # Adding String variables
            self.s2p_dir_name = tk.StringVar(value=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\S2P')
            add_label(frame_s2p_dir, label_name='Directory', col=1, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                                ipady=tab_pad_x)
            # Adding labels
            add_label(frame_s2p_dir, label_name='File', col=1, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                           ipady=tab_pad_x)
            add_label(frame_s2p_dir, label_name='S parameter', col=1, row=3).grid(sticky='e', ipadx=tab_pad_x,
                                                                                  ipady=tab_pad_x)

            # Adding entry for file directory
            self.entered_var_s2p = add_entry(frame_s2p_dir, text_var=self.s2p_dir_name, width=70, col=2, row=1)

            file_s2p = filetypes_dir(self.entered_var_s2p.get())[1]
            self.s2p_file_name_combobox = add_combobox(frame_s2p_dir, text=file_s2p, col=2, row=2, width=100)
            self.s_parameter_chosen_s2p = add_combobox(frame_s2p_dir, text=self.s_parameter_s2p, col=2, row=3,
                                                       width=100)
            self.s_parameter_chosen_s2p['values'] = ('S11', 'S12', 'S21', 'S22')

            # Adding buttons
            self.update_s2p_button = add_button(tab=frame_s2p_dir, button_name=' Update Files ',
                                                command=lambda: [update_entries(directory=self.entered_var_s2p.get(),
                                                                                combobox=self.s2p_file_name_combobox,
                                                                                filetype='.s2p'),
                                                                 update_button(self.update_s2p_button)], col=3, row=1)
            self.update_s2p_button
            add_button(frame_s2p_dir, button_name='Exit',
                       command=self._quit, col=5, row=1)
            add_button(frame_s2p_dir, button_name='Plot',
                       command=self.plot_s2p, col=3, row=3)
            add_button(frame_s2p_dir, button_name='Delete Graphs',
                       command=self.delete_axs_s2p, col=3, row=2)

            # Canvas creation
            self.s2p_canvas = create_canvas(figure=self.fig_s2p, frame=frame_s2p_display,
                                            toolbar_frame=frame_s2p_sliders)

            # Sliders creation
            self.slider_amplitude_s2p = add_slider(frame=frame_s2p_display, _from=0, to=-40,
                                                   name="Amplitude (dB)",
                                                   variable=self.scale_amplitude_value, step=5,
                                                   orientation=tk.VERTICAL)
            self.slider_frequency_s2p = add_slider(frame=frame_s2p_sliders, _from=1e9, to=40e9,
                                                   name="Upper Frequency limit (Hz)",
                                                   variable=self.scale_frequency_upper_value, step=10e9)
            self.slider_lower_frequency_s2p = add_slider(frame=frame_s2p_sliders, _from=1e9, to=40e9,
                                                         name=" Lower Frequency Limit (Hz)",
                                                         variable=self.scale_frequency_lower_value, step=10e9)

            self.slider_amplitude_s2p.pack(side='left', anchor='center')
            self.slider_frequency_s2p.pack(side='right')
            self.slider_lower_frequency_s2p.pack(side='left')

        def setup_pull_in_display_tab():
            # TAB is for Pull voltage vs isolation display
            frame_v_pull_in_dir = add_label_frame(tab_pull_in, frame_name='Vpull-in Directory', col=0,
                                                  row=0)  # s2p Frame
            frame_v_pull_in_graph = add_label_frame(tab_pull_in, frame_name='Graph', col=0, row=3)  # s2p Frame
            frame_v_pull_in_sliders = add_label_frame(tab_pull_in, frame_name='Voltage limit', col=0, row=4)

            self.pull_in_dir_name = tk.StringVar(
                value=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\Pullin voltage')

            add_label(frame_v_pull_in_dir, label_name='Directory', col=1, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                                      ipady=tab_pad_x)
            add_label(frame_v_pull_in_dir, label_name='File', col=1, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                                 ipady=tab_pad_x)
            frame_v_pull_in_display = add_label_frame(tab_pull_in, frame_name='Pull-in Display', col=0, row=1)

            # Adding entry for file directory
            self.entered_var_txt = add_entry(frame_v_pull_in_dir, text_var=self.pull_in_dir_name, width=70, col=2,
                                             row=1)

            file_txt = filetypes_dir(self.entered_var_txt.get())[2]
            self.txt_file_name_combobox = add_combobox(frame_v_pull_in_dir, text=file_txt, col=2, row=2, width=100)

            # Adding buttons
            self.update_pull_in_button = add_button(tab=frame_v_pull_in_dir, button_name=' Update Files ',
                                                    command=lambda: [
                                                        update_entries(directory=self.entered_var_txt.get(),
                                                                       combobox=self.txt_file_name_combobox,
                                                                       filetype='.txt'),
                                                        update_button(self.update_pull_in_button)],
                                                    col=3, row=1)
            add_button(frame_v_pull_in_dir, button_name='Exit', command=self.quit, col=5, row=1).grid_anchor('e')
            add_button(frame_v_pull_in_dir, button_name='Plot', command=lambda: [self.plot_vpull_in(),
                                                                                 self.calculate_pull_in_out_voltage()],
                       col=3, row=3)
            add_button(frame_v_pull_in_dir, button_name='Delete Graphs', command=self.delete_axs_vpullin, col=3,
                       row=2)
            add_button(frame_v_pull_in_dir, button_name='Calculate Pull-in and Pull-out voltages',
                       command=None, col=2, row=3).configure(width=40)
            # Scrolled text creation
            self.text_scroll = add_scrolled_text(tab=frame_v_pull_in_display, scrolled_width=100,
                                                 scrolled_height=3)
            # Canvas creation
            self.canvas_v_pull_in_display = create_canvas(figure=self.fig_pull_in, frame=frame_v_pull_in_graph,
                                                          toolbar_frame=frame_v_pull_in_sliders)

            # Sliders creation
            self.slider_isolation = add_slider(frame=frame_v_pull_in_graph, _from=0, to=-40,
                                               name="Isolation (dB)", variable=self.scale_isolation_value, step=5,
                                               orientation=tk.VERTICAL)
            self.slider_voltage = add_slider(frame=frame_v_pull_in_sliders, _from=0, to=50,
                                             name="Voltage upper limit (V)", variable=self.scale_voltage_value, step=5)

            self.slider_isolation.pack(side='left')
            self.slider_voltage.pack(side='left')

        def setup_pull_in_measurement():
            # This TAB is for Pull down voltage vs isolation measurement
            frame_test_pull_in_comp_info = add_label_frame(tab_pull_in_meas, frame_name='Component information', col=0,
                                                           row=0)
            frame_test_pull_in_sig_gen = add_label_frame(tab=tab_pull_in_meas, frame_name='Signal Generator', col=0,
                                                         row=1)
            frame_test_pull_in_gen_controls = add_label_frame(tab=tab_pull_in_meas, frame_name='General controls',
                                                              col=2,
                                                              row=0)
            frame_osc_tecktro_pull_in_test = add_label_frame(tab=tab_pull_in_meas, frame_name='Oscilloscope Tecktronix',
                                                             col=1, row=0, row_span=3)
            frame_test_pull_in_measurement = add_label_frame(tab=tab_pull_in_meas, frame_name='Measurement', col=2,
                                                             row=1,
                                                             row_span=2)
            frame_test_measurement = ttk.Frame(frame_test_pull_in_measurement)
            frame_oscilloscope = add_label_frame(tab_pull_in_meas, frame_name='Ocilloscope & RF Gen', col=0, row=2,
                                                 row_span=1)

            # Adding labels to component info labelframe
            add_label(frame_test_pull_in_comp_info, label_name='DIR', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x,
                                                                                         ipady=tab_pad_x)
            add_label(frame_test_pull_in_comp_info, label_name='Project', col=0, row=1).grid(sticky='e',
                                                                                             ipadx=tab_pad_x,
                                                                                             ipady=tab_pad_x)
            add_label(frame_test_pull_in_comp_info, label_name='Cell', col=0, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                                          ipady=tab_pad_x)
            add_label(frame_test_pull_in_comp_info, label_name='Reticule', col=0, row=3).grid(sticky='e',
                                                                                              ipadx=tab_pad_x,
                                                                                              ipady=tab_pad_x)
            add_label(frame_test_pull_in_comp_info, label_name='Device', col=0, row=4).grid(sticky='e', ipadx=tab_pad_x,
                                                                                            ipady=tab_pad_x)
            add_label(frame_test_pull_in_comp_info, label_name='Bias Voltage', col=0, row=5).grid(sticky='e',
                                                                                                  ipadx=tab_pad_x,
                                                                                                  ipady=tab_pad_x)
            # Variables for the TAB
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

            # Signal Generator labelframe
            frame_signal_gen_measurement = ttk.Frame(frame_test_pull_in_sig_gen)
            frame_signal_gen_measurement.pack()
            self.pull_in_v_bias = tk.DoubleVar(value=10)  # Peak bias voltage for ramp function
            self.ramp_width = tk.DoubleVar(value=100)  # Ramp length for ramp function
            self.chosen_bias_voltage_pull_in = add_entry(tab=frame_test_pull_in_comp_info, text_var=self.pull_in_v_bias,
                                                         width=20, col=1, row=5)
            add_label(frame_signal_gen_measurement, label_name='Bias Voltage', col=0, row=0).grid(sticky='e',
                                                                                                  ipadx=tab_pad_x,
                                                                                                  ipady=tab_pad_x)
            add_label(frame_signal_gen_measurement, label_name='Ramp length', col=0, row=1).grid(sticky='e',
                                                                                                 ipadx=tab_pad_x,
                                                                                                 ipady=tab_pad_x)
            self.entered_ramp_volt = add_entry(frame_signal_gen_measurement, text_var=self.pull_in_v_bias, width=10,
                                               col=1,
                                               row=0)
            self.txt_file_name_meas_combobox = tk.StringVar(value=r'test')

            add_button(tab=frame_test_pull_in_comp_info, button_name='Create-file',
                       command=lambda: [file_name_creation(data_list=[self.test_pull_in_project.get(),
                                                                      self.test_pull_in_cell.get(),
                                                                      self.test_pull_in_reticule.get(),
                                                                      self.test_pull_in_device.get(),
                                                                      self.entered_ramp_volt.get()],
                                                           text=self.text_file_name_pull_in_test, end_characters='V')],
                       col=2, row=0)

            self.entered_ramp_width = add_entry(frame_signal_gen_measurement, text_var=self.ramp_width, width=10, col=1,
                                                row=1)
            add_label(frame_signal_gen_measurement, label_name='(V)', col=2, row=0).grid(sticky='w', ipadx=tab_pad_x,
                                                                                         ipady=tab_pad_x)
            add_label(frame_signal_gen_measurement, label_name='(µs)', col=2, row=1).grid(sticky='w', ipadx=tab_pad_x,
                                                                                          ipady=tab_pad_x)
            add_button(tab=frame_signal_gen_measurement, button_name='Set Bias Voltage', command=self.set_bias_pull_in,
                       col=3, row=0).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
            add_button(tab=frame_signal_gen_measurement, button_name='Set Ramp Width', command=self.set_ramp_width,
                       col=3,
                       row=1).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
            add_button(tab=frame_signal_gen_measurement, button_name='Set Pulse Gen', command=self.set_pulse_gen_ramp,
                       col=3, row=3).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
            # Oscilloscope
            add_button(tab=frame_oscilloscope, button_name='Setup Oscilloscope',
                       command=lambda: scripts_and_functions.osc_pullin_config(),
                       col=0, row=0).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
            add_button(tab=frame_oscilloscope, button_name='Setup RF Gen',
                       command=lambda: scripts_and_functions.rf_gen_pull_in_setup(),
                       col=0, row=1).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
            # General controls labelframe
            self.text_file_name_pull_in_test = tk.Text(frame_test_pull_in_gen_controls, width=40, height=1,
                                                       wrap=tk.WORD,
                                                       border=4, borderwidth=2,
                                                       relief=tk.SUNKEN, font=('Bahnschrift Light', 10))  # Filename
            self.text_file_name_pull_in_test.grid(column=0, row=0, sticky='n', columnspan=5)
            self.text_gen_controls_pull_in_debug = tk.Text(frame_test_pull_in_gen_controls, width=40, height=10,
                                                           wrap=tk.WORD, border=4,
                                                           borderwidth=2, relief=tk.SUNKEN,
                                                           font=('Bahnschrift Light', 10))
            # Debug text_file_name_s3p_test display
            self.text_gen_controls_pull_in_debug.grid(column=0, row=3, sticky='n', columnspan=4)

            add_button(tab=frame_test_pull_in_gen_controls, button_name='Reset Signal Generator',
                       command=self.reset_sig_gen, col=0, row=1).grid(ipadx=tab_pad_x, ipady=tab_pad_x)
            add_button(tab=frame_test_pull_in_gen_controls, button_name='Exit', command=lambda: [self._quit(),
                                                                                                 close_resources()],
                       col=1,
                       row=1).grid(ipadx=tab_pad_x, ipady=tab_pad_x)
            add_button(tab=frame_test_pull_in_gen_controls, button_name='Plot IsovsV',
                       command=lambda: [self.trace_pull_down(self.test_cycling_detector_conversion.get()),
                                        self.acquire_pull_down_data()], col=1, row=5).grid(
                ipadx=tab_pad_x, ipady=tab_pad_x)
            # -------------------------------------------------------------------------------------------------------------

            self.canvas_v_pull_in_meas = create_canvas(figure=self.fig_pull_in_meas,
                                                       frame=frame_osc_tecktro_pull_in_test,
                                                       toolbar_frame=frame_test_pull_in_measurement, toolbar=True)

            add_label(frame_test_measurement,
                      label_name='Positive-Pull-in', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
            self.text_pull_in_plus_test = tk.Text(frame_test_measurement, width=15, height=1, wrap=tk.WORD,
                                                  border=4, borderwidth=2,
                                                  relief=tk.SUNKEN, font=('Bahnschrift Light', 10))  # Positive Pull-in
            self.text_pull_in_plus_test.grid(column=1, row=0, sticky='n', columnspan=5)

            add_label(frame_test_measurement,
                      label_name='Negative-Pull-in', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
            self.text_pull_in_minus_test = tk.Text(frame_test_measurement, width=15,
                                                   height=1, wrap=tk.WORD, border=4, borderwidth=2, relief=tk.SUNKEN,
                                                   font=('Bahnschrift Light', 10))  # Negative Pull-in
            self.text_pull_in_minus_test.grid(column=1, row=1, sticky='n', columnspan=5)

            add_label(frame_test_measurement,
                      label_name='Positive-Pull-out', col=0, row=2).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
            self.text_pull_out_plus_test = tk.Text(frame_test_measurement,
                                                   width=15, height=1, wrap=tk.WORD, border=4,
                                                   borderwidth=2, relief=tk.SUNKEN,
                                                   font=('Bahnschrift Light', 10))  # Positive Pull-out
            self.text_pull_out_plus_test.grid(column=1, row=2, sticky='n', columnspan=5)

            add_label(frame_test_measurement, label_name='Negative-Pull-out', col=0, row=3).grid(sticky='e',
                                                                                                 ipadx=tab_pad_x,
                                                                                                 ipady=tab_pad_x)
            self.text_pull_out_minus_test = tk.Text(frame_test_measurement, width=15, height=1, wrap=tk.WORD,
                                                    border=4, borderwidth=2,
                                                    relief=tk.SUNKEN,
                                                    font=('Bahnschrift Light', 10))  # Negative Pull-out
            self.text_pull_out_minus_test.grid(column=1, row=3, sticky='n', columnspan=5)

            add_label(frame_test_measurement, label_name='Isolation at PI(+)', col=0, row=4).grid(sticky='e',
                                                                                                  ipadx=tab_pad_x,
                                                                                                  ipady=tab_pad_x)

            self.text_iso_pull_in_plus_test = tk.Text(frame_test_measurement, width=15, height=1, wrap=tk.WORD,
                                                      border=4, borderwidth=2,
                                                      relief=tk.SUNKEN,
                                                      font=('Bahnschrift Light', 10))  # Isolation at PI (+)
            self.text_iso_pull_in_plus_test.grid(column=1, row=4, sticky='n', columnspan=5)

            add_label(frame_test_measurement, label_name='Isolation at PO (+)', col=0, row=5).grid(sticky='e',
                                                                                                   ipadx=tab_pad_x,
                                                                                                   ipady=tab_pad_x)
            self.text_iso_pull_out_plus_test = tk.Text(frame_test_measurement, width=15, height=1, wrap=tk.WORD,
                                                       border=4,
                                                       borderwidth=2, relief=tk.SUNKEN,
                                                       font=('Bahnschrift Light', 10))  # Isolation at PO (+)
            self.text_iso_pull_out_plus_test.grid(column=1, row=5, sticky='n', columnspan=5)

            add_label(frame_test_measurement, label_name='Isolation at PI (-)', col=0, row=6).grid(sticky='e',
                                                                                                   ipadx=tab_pad_x,
                                                                                                   ipady=tab_pad_x)
            self.text_iso_pull_in_minus_test = tk.Text(frame_test_measurement, width=15, height=1, wrap=tk.WORD,
                                                       border=4,
                                                       borderwidth=2, relief=tk.SUNKEN,
                                                       font=('Bahnschrift Light', 10))  # Isolation at PI (-)
            self.text_iso_pull_in_minus_test.grid(column=1, row=6, sticky='n', columnspan=5)

            add_label(frame_test_measurement, label_name='Isolation at PO (-)', col=0, row=7).grid(sticky='e',
                                                                                                   ipadx=tab_pad_x,
                                                                                                   ipady=tab_pad_x)
            self.text_iso_pull_out_minus_test = tk.Text(frame_test_measurement, width=15, height=1, wrap=tk.WORD,
                                                        border=4,
                                                        borderwidth=2, relief=tk.SUNKEN,
                                                        font=('Bahnschrift Light', 10))  # Isolation at PO (-)
            self.text_iso_pull_out_minus_test.grid(column=1, row=7, sticky='n', columnspan=5)
            frame_test_measurement.pack(fill='both')

        def setup_snp_measurement():
            frame_snp_compo_info = add_label_frame(tab_snp_meas, frame_name='Component information', col=0,
                                                   row=0)  # s3p frame
            frame_snp_sig_gen = add_label_frame(tab=tab_snp_meas, frame_name='Signal Generator', col=0, row=1)
            frame_snp_zva = add_label_frame(tab=tab_snp_meas, frame_name='ZVA', col=3, row=1)
            frame_snp_gene_controls = add_label_frame(tab=tab_snp_meas, frame_name='General controls', col=3, row=0)
            frame_snp_measurement = add_label_frame(tab=tab_snp_meas, frame_name='SNP measurement', col=1, row=0,
                                                    row_span=2)
            frame_test_snp_measurement = ttk.Frame(frame_snp_measurement)
            frame_test_snp_measurement.pack(anchor='nw')

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
            self.chosen_bias_voltage = add_entry(tab=frame_snp_compo_info, text_var=self.pull_in_v, width=20, col=1,
                                                 row=6)

            self.file_s3p = tk.StringVar(value=r'test')

            add_button(tab=frame_snp_compo_info, button_name='Create-file',
                       command=lambda: [file_name_creation(
                           data_list=[self.test_s3p_project.get(), self.test_s3p_cell.get(),
                                      self.test_s3p_reticule.get(),
                                      self.test_s3p_device.get(), self.chosen_component_state.get(),
                                      self.chosen_bias_voltage.get()], text=self.text_file_name_s3p_test,
                           end_characters='V')], col=2,
                       row=0)

            add_label(frame_snp_sig_gen, label_name='Bias Voltage', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x,
                                                                                       ipady=tab_pad_x)
            add_label(frame_snp_sig_gen, label_name='Pulse Width', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                                      ipady=tab_pad_x)
            self.entered_pull_in_volt = add_entry(frame_snp_sig_gen, text_var=self.pull_in_v, width=10, col=1, row=0)
            self.entered_pulse_width = add_entry(frame_snp_sig_gen, text_var=self.pulse_width, width=10, col=1, row=1)
            add_label(frame_snp_sig_gen, label_name='(V)', col=2, row=0).grid(sticky='w', ipadx=tab_pad_x,
                                                                              ipady=tab_pad_x)
            add_label(frame_snp_sig_gen, label_name='(s)', col=2, row=1).grid(sticky='w', ipadx=tab_pad_x,
                                                                              ipady=tab_pad_x)

            add_label(frame_snp_sig_gen, label_name='Pulse Frequency', col=0, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                                          ipady=tab_pad_x)
            self.entered_pulse_freq = add_entry(frame_snp_sig_gen, text_var=self.pulse_freq, width=10, col=1, row=2)
            add_label(frame_snp_sig_gen, label_name='(Hz)', col=2, row=2).grid(sticky='w', ipadx=tab_pad_x,
                                                                               ipady=tab_pad_x)

            add_button(tab=frame_snp_sig_gen, button_name='Set Bias Voltage', command=self.set_bias_voltage, col=3,
                       row=0).grid(
                sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
            add_button(tab=frame_snp_sig_gen, button_name='Set Pulse Width', command=self.set_ramp_width, col=3,
                       row=1).grid(
                sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
            add_button(tab=frame_snp_sig_gen,
                       button_name='Set prf', command=self.set_prf, col=3, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                                       ipady=tab_pad_x)
            add_button(tab=frame_snp_sig_gen, button_name='Set Pulse Gen', command=self.set_pulse_gen, col=3,
                       row=3).grid(
                sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
            # ------------------------------------------------------------------------------
            self.canvas_snp_meas = create_canvas(figure=self.fig_snp_meas, frame=frame_snp_measurement,
                                                 toolbar_frame=frame_test_snp_measurement, toolbar=True)
            # ------------------------------------------------------------------------------

            self.text_file_name_s3p_test.grid(column=0, row=0, sticky='n', columnspan=5)
            self.f_start = tk.DoubleVar(value=1)
            self.f_stop = tk.DoubleVar(value=10)
            self.nb_points = tk.DoubleVar(value=100)

            add_label(frame_snp_zva, label_name='Fstart', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x,
                                                                             ipady=tab_pad_x)
            add_label(frame_snp_zva, label_name='Fstop', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                            ipady=tab_pad_x)
            add_label(frame_snp_zva, label_name='Nb Points', col=0, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                                ipady=tab_pad_x)
            self.entered_f_start = add_entry(frame_snp_zva, text_var=self.f_start, width=10, col=1, row=0)
            self.entered_fstop = add_entry(frame_snp_zva, text_var=self.f_stop, width=10, col=1, row=1)
            self.entered_nb_points = add_entry(frame_snp_zva, text_var=self.nb_points, width=10, col=1, row=2)
            add_label(frame_snp_zva, label_name='(GHz)', col=2, row=0).grid(sticky='w', ipadx=tab_pad_x,
                                                                            ipady=tab_pad_x)
            add_label(frame_snp_zva, label_name='(GHz)', col=2, row=1).grid(sticky='w', ipadx=tab_pad_x,
                                                                            ipady=tab_pad_x)
            add_label(frame_snp_zva, label_name='(Pts)', col=2, row=2).grid(sticky='w', ipadx=tab_pad_x,
                                                                            ipady=tab_pad_x)

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
            add_button(tab=frame_snp_gene_controls, button_name='Exit',
                       command=lambda: [self._quit(), close_resources()],
                       col=1,
                       row=1).grid(ipadx=tab_pad_x, ipady=tab_pad_x)
            add_button(tab=frame_snp_gene_controls, button_name='Reset Signal Gen',
                       command=self.set_pulse_gen_pulse_mode,
                       col=1,
                       row=2).grid(ipadx=tab_pad_x, ipady=tab_pad_x)
            add_button(tab=frame_snp_gene_controls, button_name='S1P config', command=call_s1p_config, col=0,
                       row=4).grid(
                ipadx=tab_pad_x, ipady=tab_pad_x)
            add_button(tab=frame_snp_gene_controls, button_name='S2P config', command=call_s2p_config, col=1,
                       row=4).grid(
                ipadx=tab_pad_x, ipady=tab_pad_x)
            add_button(tab=frame_snp_gene_controls, button_name='S3P config', command=call_s3p_config, col=2,
                       row=4).grid(
                ipadx=tab_pad_x, ipady=tab_pad_x)

        def setup_power_measurement():
            frame_power_compo_info = add_label_frame(tab_power_meas, frame_name='Component information', col=0,
                                                     row=0)  # power sweep frame
            frame_power_meas = add_label_frame(tab=tab_power_meas, frame_name='General controls', col=2, row=0)
            frame_power_meas_graph = add_label_frame(tab=tab_power_meas, frame_name='Power test Graph', col=1, row=0,
                                                     row_span=3)
            frame_power_meas_sig_gen = add_label_frame(tab=tab_power_meas, frame_name='Signal Generator', col=0, row=1,
                                                       row_span=1)
            frame_power_meas_rf_gen = add_label_frame(tab=tab_power_meas, frame_name='RF Generator', col=2, row=1,
                                                      row_span=2)
            frame_power_meas_powermeter = add_label_frame(tab=tab_power_meas, frame_name='Powermeter', col=0, row=2,
                                                          row_span=1)
            frame_test_power_measurement = ttk.Frame(frame_power_meas_graph)
            frame_test_power_measurement.pack(anchor='nw')

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

            add_label(frame_power_meas_powermeter, label_name='Input Attenuation (A)', col=0, row=0).grid(
                sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
            add_label(frame_power_meas_powermeter, label_name='Output Attenuation (B)', col=0, row=1).grid(
                sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
            add_label(frame_power_meas_powermeter, label_name='(dB)', col=2, row=0).grid(
                sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
            add_label(frame_power_meas_powermeter, label_name='(dB)', col=2, row=1).grid(
                sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)

            self.test_pow_dir = tk.StringVar(
                value=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\Power handling')
            self.test_pow_project = tk.StringVar(value=r'Project_Name')
            self.test_pow_cell = tk.StringVar(value=r'Cell_Name')
            self.test_pow_reticule = tk.StringVar(value=r'Reticule')
            self.test_pow_device = tk.StringVar(value=r'Device_name')
            self.test_pow_file_created = tk.StringVar(value=r'EMPTY')
            self.test_pow_state = tk.StringVar(value=r'EMPTY')
            self.bias_voltage_pow = tk.StringVar(value=r'Bias_Voltage')
            self.test_pow_input_atten = tk.DoubleVar(value=0)
            self.test_pow_output_atten = tk.DoubleVar(value=0)

            self.chosen_component_state_pow = add_combobox(frame_power_compo_info, text=self.test_pow_state, col=1,
                                                           row=5,
                                                           width=20)
            self.chosen_component_state_pow['values'] = ('Active', 'Frozen')
            self.chosen_component_state_pow.current(0)

            add_entry(tab=frame_power_compo_info, text_var=self.test_pow_dir, width=20, col=1, row=0)
            add_entry(tab=frame_power_compo_info, text_var=self.test_pow_project, width=20, col=1, row=1)
            add_entry(tab=frame_power_compo_info, text_var=self.test_pow_cell, width=20, col=1, row=2)
            add_entry(tab=frame_power_compo_info, text_var=self.test_pow_reticule, width=20, col=1, row=3)
            add_entry(tab=frame_power_compo_info, text_var=self.test_pow_device, width=20, col=1, row=4)
            add_entry(tab=frame_power_compo_info, text_var=self.bias_voltage_pow, width=20, col=1, row=6)

            add_entry(tab=frame_power_meas_powermeter, text_var=self.test_pow_input_atten, width=20, col=1, row=0)
            add_entry(tab=frame_power_meas_powermeter, text_var=self.test_pow_output_atten, width=20, col=1, row=1)

            self.power_test_file_name = tk.StringVar(value=r'test')

            add_button(tab=frame_power_compo_info, button_name='Create-file',
                       command=lambda: [
                           file_name_creation(data_list=[self.test_pow_project.get(), self.test_pow_cell.get(),
                                                         self.test_pow_reticule.get(),
                                                         self.test_pow_device.get(),
                                                         self.chosen_component_state_pow.get(),
                                                         self.bias_voltage_pow.get()],
                                              text=self.text_power_file_name, end_characters='V')],
                       col=2, row=0)
            add_button(tab=frame_power_compo_info, button_name='Send trigger', command=scripts_and_functions.send_trig,
                       col=2, row=1)
            # General controls---------------------------------------------------------------

            rf_gen_min_power = tk.DoubleVar(value=-20)
            rf_gen_max_power = tk.DoubleVar(value=-10)
            rf_gen_step = tk.DoubleVar(value=1)
            rf_gen_frequency = tk.DoubleVar(value=10)
            add_entry(tab=frame_power_meas_rf_gen, text_var=rf_gen_min_power, width=20, col=1, row=0)
            add_entry(tab=frame_power_meas_rf_gen, text_var=rf_gen_max_power, width=20, col=1, row=1)
            add_entry(tab=frame_power_meas_rf_gen, text_var=rf_gen_step, width=20, col=1, row=2)
            add_entry(tab=frame_power_meas_rf_gen, text_var=rf_gen_frequency, width=20, col=1, row=3)

            add_label(tab=frame_power_meas_rf_gen, label_name="Min Power (dBm)", col=0, row=0)
            add_label(tab=frame_power_meas_rf_gen, label_name="Max Power (dBm)", col=0, row=1)
            add_label(tab=frame_power_meas_rf_gen, label_name="Step Power (dB)", col=0, row=2)
            add_label(tab=frame_power_meas_rf_gen, label_name="Frequency (GHz)", col=0, row=3)

            add_button(tab=frame_power_meas_rf_gen, button_name='Set RF Gen\nParameters',
                       command=lambda: scripts_and_functions.rf_gen_power_lim(), col=0, row=4).grid()

            self.text_power_file_name = tk.Text(frame_power_meas, width=40, height=1, wrap=tk.WORD, border=4,
                                                borderwidth=2, relief=tk.SUNKEN,
                                                font=('Bahnschrift Light', 10))  # Filename
            self.text_power_file_name.grid(column=0, row=0, sticky='n', columnspan=5)
            self.text_power_debug = tk.Text(frame_power_meas,
                                            width=40, height=10, wrap=tk.WORD, border=4, borderwidth=2,
                                            relief=tk.SUNKEN,
                                            font=('Bahnschrift Light', 10))  # Debug text_file_name_s3p_test display
            self.text_power_debug.grid(column=0, row=3, sticky='n', columnspan=4)

            add_button(tab=frame_power_meas_sig_gen, button_name='Reset\nSignal Generator',
                       command=self.set_pulse_gen_pulse_mode, col=0,
                       row=0)
            add_button(tab=frame_power_meas, button_name='Exit', command=lambda: [self._quit(), close_resources()],
                       col=1,
                       row=1).grid(ipadx=tab_pad_x, ipady=tab_pad_x)

            add_button(tab=frame_power_meas, button_name='Launch Test',
                       command=lambda: [os.chdir(self.test_pow_dir.get()), self.start_power_test_sequence(
                           self, filename=file_name_creation(data_list=[self.test_pow_project.get(),
                                                                        self.test_pow_cell.get(),
                                                                        self.test_pow_reticule.get(),
                                                                        self.test_pow_device.get()],
                                                             text=self.text_power_file_name),
                           start=rf_gen_min_power.get(),
                           stop=rf_gen_max_power.get(),
                           step=rf_gen_step.get(),
                           sleep_duration=1,
                           offset_b1=self.test_pow_output_atten.get(),
                           offset_a1=self.test_pow_input_atten.get(),
                       )], col=1, row=5).grid(ipadx=tab_pad_x, ipady=tab_pad_x)

            add_button(tab=frame_power_meas_sig_gen,
                       button_name='Power Handling\nTest setup'.format(align="=", fill=' '),
                       command=lambda: [scripts_and_functions.setup_power_test_sequence()], col=0, row=1).grid()

            add_button(tab=frame_power_meas_powermeter, button_name='Attenuation\nConfig',
                       command=lambda: [scripts_and_functions.set_channel_attenuation(
                           atts={"A": self.test_pow_input_atten.get(), "B": self.test_pow_output_atten.get()})],
                       col=0, row=2).grid()

            add_button(tab=frame_power_meas_rf_gen, button_name="Reset RF gen",
                       command=lambda: [scripts_and_functions.rf_gen_power_setup()], col=0, row=5)

            add_button(tab=frame_power_meas_rf_gen, button_name="Set RF gen\nFrequency",
                       command=lambda: [scripts_and_functions.rf_gen_set_freq(rf_gen_frequency.get())], col=0,
                       row=6)
            create_canvas(figure=self.fig_power_meas, frame=frame_power_meas_graph,
                          toolbar_frame=frame_test_power_measurement, toolbar=True)

        def setup_cycling_measurement():
            frame_cycling_comp_info = add_label_frame(tab=tab_cycling, frame_name='Component information', col=0,
                                                      row=0)  # Resource frame
            frame_oscilloscope = add_label_frame(tab=tab_cycling, frame_name='Oscilloscope', col=0, row=2)
            frame_sig_gen = add_label_frame(tab=tab_cycling, frame_name='Signal Generator', col=0, row=1)
            frame_cycling_monitor = add_label_frame(tab=tab_cycling, frame_name='Cycling monitor', col=1, row=0,
                                                    row_span=4)
            frame_rf_gen = add_label_frame(tab=tab_cycling, frame_name='RF generator', col=0, row=3)

            frame_osc_toolbar = ttk.Frame(frame_cycling_monitor)
            frame_osc_toolbar.pack(anchor='nw')

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
                      label_name='Header info', col=0, row=7).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
            add_label(frame_cycling_comp_info,
                      label_name='x10^5', col=2, row=5).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)

            add_button(tab=frame_cycling_comp_info, button_name="Exit", command=self._quit,
                       col=0, row=8).grid(ipadx=tab_pad_x, ipady=tab_pad_x)
            add_button(tab=frame_cycling_comp_info, button_name="Start Cycling", command=self.cycling_test,
                       col=1, row=8).grid(ipadx=tab_pad_x, ipady=tab_pad_x)
            add_button(tab=frame_oscilloscope, button_name="Set event count",
                       command=lambda: [scripts_and_functions.set_osc_event_count(self.test_cycling_events.get())],
                       col=1, row=1).grid(ipadx=tab_pad_x, ipady=tab_pad_x)

            self.test_cycling_dir = tk.StringVar(value=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement '
                                                       r'Data\Mechanical cycling')
            self.test_cycling_project = tk.StringVar(value=r'Project_Name')
            self.test_cycling_cell = tk.StringVar(value='Cell_name')
            self.test_cycling_ret = tk.StringVar(value='Reticule')
            self.test_cycling_device = tk.StringVar(value='Device_Name')
            self.test_cycling_var_bias = tk.StringVar(value='Bias_voltage')
            self.test_cycling_var_nb_cycles = tk.DoubleVar(value=1)
            self.test_cycling_file_comment = tk.StringVar(value='')
            self.test_cycling_events = tk.DoubleVar(value=100)
            self.test_cycling_gen_power = tk.DoubleVar(value=0)
            self.test_cycling_gen_frequency = tk.DoubleVar(value=10)
            self.test_cycling_detector_conversion = tk.DoubleVar(value=0.040)

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
                frame_cycling_comp_info, text_var=self.test_cycling_file_comment, width=20, col=1, row=7)
            self.entered_test_cycling_events = add_entry(
                frame_cycling_comp_info, text_var=self.test_cycling_events, width=20, col=1, row=6)

            add_label(frame_sig_gen, label_name='Bias voltage', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x,
                                                                                   ipady=tab_pad_x)
            add_label(frame_sig_gen, label_name='V', col=2, row=0).grid(sticky='w', ipadx=tab_pad_x,
                                                                        ipady=tab_pad_x)
            add_label(frame_sig_gen, label_name='Number of Cycles', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                                       ipady=tab_pad_x)
            add_label(frame_sig_gen, label_name='Cycles (x10^5)', col=2, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                                     ipady=tab_pad_x)
            self.test_cycling_var_bias = tk.StringVar(value='40')

            self.entered_var_cycling_bias = add_entry(frame_sig_gen, text_var=self.test_cycling_var_bias, width=15,
                                                      col=1,
                                                      row=0)
            self.entered_var_cycling_nb_cycles = add_entry(frame_sig_gen, text_var=self.test_cycling_var_nb_cycles,
                                                           width=15, col=1, row=1)

            add_button(tab=frame_sig_gen, button_name='Cycling config',
                       command=lambda: [scripts_and_functions.sig_gen_cycling_config()], col=0,
                       row=2).grid(
                ipadx=tab_pad_x, ipady=tab_pad_x)

            add_button(tab=frame_sig_gen, button_name='Set Bias Voltage',
                       command=lambda: self.set_symmetrical_voltage_bias(voltage=self.test_cycling_var_bias.get()),
                       col=1,
                       row=2).grid(ipadx=tab_pad_x, ipady=tab_pad_x)

            add_label(frame_oscilloscope,
                      label_name='Detector conversion\n coefficient', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x,
                                                                                         ipady=tab_pad_x)
            self.entered_var_cycling_detector = add_entry(frame_oscilloscope,
                                                          text_var=self.test_cycling_detector_conversion,
                                                          width=15, col=1, row=0)
            add_label(frame_oscilloscope,
                      label_name='V', col=2, row=0).grid(sticky='e', ipadx=tab_pad_x,
                                                         ipady=tab_pad_x)
            add_button(tab=frame_oscilloscope, button_name='Cycling config',
                       command=scripts_and_functions.osc_cycling_config, col=0,
                       row=1).grid(ipadx=tab_pad_x, ipady=tab_pad_x)

            add_label(frame_rf_gen,
                      label_name='RF Power', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
            add_label(frame_rf_gen,
                      label_name='dBm', col=2, row=0).grid(sticky='w', ipadx=tab_pad_x, ipady=tab_pad_x)
            add_label(frame_rf_gen,
                      label_name='Frequency', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
            add_label(frame_rf_gen,
                      label_name='GHz', col=2, row=1).grid(sticky='w', ipadx=tab_pad_x, ipady=tab_pad_x)
            add_button(tab=frame_rf_gen, button_name='Gen config',
                       command=lambda: scripts_and_functions.rf_gen_cycling_setup(
                           power=self.test_cycling_gen_power.get(),
                           frequency=self.test_cycling_gen_frequency.get()), col=0,
                       row=2).grid(ipadx=tab_pad_x, ipady=tab_pad_x)
            self.entered_gen_power = add_entry(
                frame_rf_gen, text_var=self.test_cycling_gen_power, width=20, col=1, row=0)
            self.entered_gen_power = add_entry(
                frame_rf_gen, text_var=self.test_cycling_gen_frequency, width=20, col=1, row=1)

            self.canvas_cycling = create_canvas(figure=self.fig_cycling, frame=frame_cycling_monitor,
                                                toolbar_frame=frame_osc_toolbar, toolbar=True)

        def setup_scpi_configuration():
            frame_resources = add_label_frame(tab_resources, frame_name='Ressouce Configuration', col=0, row=0)
            # Resource frame

            self.zva_inst = tk.StringVar(value=r'TCPIP0::ZNA67-101810::inst0::INSTR')
            self.sig_gen_inst = tk.StringVar(value=r'TCPIP0::A-33521B-00526::inst0::INSTR')
            self.osc_inst = tk.StringVar(value=r'TCPIP0::DPO5054-C011738::inst0::INSTR')
            self.powermeter_inst = tk.StringVar(value=u'TCPIP0::A-N1912A-00589::inst0::INSTR')
            self.rf_gen_inst = tk.StringVar(value=u'TCPIP0::rssmb100a179766::inst0::INSTR')

            add_label(frame_resources, label_name='ZVA', col=1, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                            ipady=tab_pad_x)
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
            self.entered_var_powermeter_address = add_entry(frame_resources, text_var=self.powermeter_inst, width=70,
                                                            col=2,
                                                            row=4)
            self.entered_var_rf_gen_address = add_entry(frame_resources, text_var=self.rf_gen_inst, width=70, col=2,
                                                        row=5)

        setup_s3p_display_tab()
        setup_s2p_display_tab()
        setup_pull_in_measurement()
        setup_pull_in_display_tab()
        setup_snp_measurement()
        setup_power_measurement()
        setup_cycling_measurement()
        setup_scpi_configuration()

        # Schedule the next update

    # ==============================================================================
    # Methods
    # ==============================================================================
    # General APP functions -------------------------------------------------------
    def start_power_test_sequence(
            self,
            new_data_event,
            filename,
            start,
            stop,
            step,
            sleep_duration,
            offset_a1,
            offset_b1):
        """
        Starts the power test sequence in a separate thread.
        """
        test_thread = threading.Thread(
            target=scripts_and_functions.power_test_sequence_v2,
            args=(self, new_data_event, filename, start, stop, step, sleep_duration, offset_a1, offset_b1)
        )
        test_thread.start()

    def update_plot_power_sweep(self):
        """
        Updates the power sweep plot with the latest data in self.file_power_sweep.
        """
        # Clear the previous plot
        self.ax_power_meas.clear()
        self.ax_power_meas_secondary.clear()

        # Plot the new data
        if not self.file_power_sweep.empty:
            self.ax_power_meas_secondary.plot(
                self.file_power_sweep['Power Input DUT Avg (dBm)'],
                (self.file_power_sweep['Power Output DUT Avg (dBm)'] - self.file_power_sweep[
                    'Power Input DUT Avg (dBm)']),
                marker='o', linestyle='-', label=self.test_pow_cell.get(), color='blue'
            )
            self.ax_power_meas.plot(
                self.file_power_sweep['Power Input DUT Avg (dBm)'],
                (self.file_power_sweep['Power Output DUT Avg (dBm)']),
                marker='o', linestyle='-', label=self.test_pow_cell.get(), color='red'
            )

        # Set plot labels and title
        self.ax_power_meas.set_xlabel('Power Input DUT Avg (dBm)')
        self.ax_power_meas.set_ylabel('Power Output DUT Avg (dBm)/ Losses (dB)')
        self.ax_power_meas.set_title('Power Sweep Test')
        self.ax_power_meas.grid('both')
        self.ax_power_meas.legend()

        # Redraw the plot
        self.fig_power_meas.canvas.draw()

    def update_plot(self):
        """Update the plot with new data from the dataframe."""
        if self.is_cycling:
            # Clear the axes
            self.fig_cycling.clear()
            # for ax in self.fig_cycling.axes:
            #     ax.clear()
            self.create_cycling_axes()
            # Plot the data
            if not self.file_df.empty:
                cycles_so_far = self.file_df["cycles"]
                self.ax_cycling_pull_in.plot(cycles_so_far, self.file_df["vpullin_plus"])
                self.ax_cycling_pull_in.grid("both")

                self.ax_cycling_pull_out.plot(cycles_so_far, self.file_df["vpullout_plus"])
                self.ax_cycling_pull_out.grid("both")

                self.ax_cycling_isolation.plot(cycles_so_far, self.file_df["iso_ascent"])
                self.ax_cycling_isolation.grid("both")

                self.ax_cycling_insertion_loss.plot(cycles_so_far, self.file_df["amplitude_variation"])
                self.ax_cycling_insertion_loss.grid("both")

                self.ax_cycling_t_down.plot(cycles_so_far, self.file_df["switching_time"])
                self.ax_cycling_t_down.grid("both")

                self.ax_cycling_t_up.plot(cycles_so_far, self.file_df["release_time"])
                self.ax_cycling_t_up.grid("both")

            self.canvas_cycling.draw()

            self.new_data_event.clear()  # Clear the event after updating the plot

        # Schedule the next update
        self.after(self.update_interval, self.update_plot)

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
        scripts_and_functions.setup_zva_with_rst(dir_and_var_declaration.zva_parameters['ip_zva'])

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
        scripts_and_functions.sig_gen.write("TRIG")
        scripts_and_functions.time.sleep(2 + float(scripts_and_functions.zva.query_str_with_opc('SENSe1:SWEep:TIME?')))
        scripts_and_functions.triggered_data_acquisition(
            filename=self.text_file_name_s3p_test.get(index1="1.0", index2="end-1c"),
            zva_file_dir=dir_and_var_declaration.zva_parameters["zva_traces"],
            pc_file_dir=self.test_s3p_dir.get(),
            file_format='s3p')
        self.plot_snp_test(filetype='.s3p')
        scripts_and_functions.print_error_log()
        self.set_txt()

    def data_acquire_s2p(self):
        scripts_and_functions.sig_gen.write("TRIG")
        scripts_and_functions.time.sleep(2 + float(scripts_and_functions.zva.query_str_with_opc('SENSe1:SWEep:TIME?')))
        scripts_and_functions.triggered_data_acquisition(
            filename=self.text_file_name_s3p_test.get(index1="1.0", index2="end-1c"),
            zva_file_dir=dir_and_var_declaration.zva_parameters["zva_traces"],
            pc_file_dir=self.test_s3p_dir.get(),
            file_format='s2p')
        self.plot_snp_test(filetype='.s2p')
        scripts_and_functions.print_error_log()
        self.set_txt()

    def data_acquire_s1p(self):
        scripts_and_functions.sig_gen.write("TRIG")
        scripts_and_functions.time.sleep(2 + float(scripts_and_functions.zva.query_str_with_opc('SENSe1:SWEep:TIME?')))
        scripts_and_functions.triggered_data_acquisition(
            filename=self.text_file_name_s3p_test.get(index1="1.0", index2="end-1c"),
            zva_file_dir=dir_and_var_declaration.zva_parameters["zva_traces"],
            pc_file_dir=self.test_s3p_dir.get(),
            file_format='s1p')
        self.plot_snp_test(filetype='.s1p')
        scripts_and_functions.print_error_log()
        self.set_txt()

    # sig_gen Functions -----------------------------------------------------------
    def reset_sig_gen(self):  # Reset sig_gen using the IP address at Ressource Page (used in TAB4)
        ip = self.sig_gen_inst.get()
        scripts_and_functions.setup_sig_gen_ramp_with_rst(ip)

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

    def set_pulse_gen(self):  # Configure sig_gen bias voltage, pulse width and prf (used in TAB5)
        self.set_bias_voltage()
        self.set_prf()
        self.set_pulse_width()
        self.text_snp_debug.delete("1.0", "end")
        self.text_snp_debug.insert(index="%d.%d" % (0, 0), chars=scripts_and_functions.sig_gen_set_output_ramp_log())

    def set_pulse_gen_ramp(
            self):  # Calls set_bias_pull_in() & set_ramp_width() to Configure sig_gen ramp bias voltage and pulse
        # width (used in TAB4)
        self.set_bias_pull_in()
        self.set_ramp_width()
        self.text_gen_controls_pull_in_debug.delete("1.0", "end")
        self.text_gen_controls_pull_in_debug.insert(index="%d.%d" % (0, 0),
                                                    chars=scripts_and_functions.sig_gen_set_output_ramp_log())

    def set_pulse_gen_pulse_mode(self):
        # Calls scripts_and_functions module's configuration_sig_gen() to reset the sig_gen and sends an
        # error log (used
        # in TAB7)
        scripts_and_functions.configuration_sig_gen_power()
        self.text_power_debug.delete("1.0", "end")
        self.text_power_debug.insert(index="%d.%d" % (0, 0), chars=scripts_and_functions.sig_gen_set_output_log())

    def set_power_test_mode(self):
        pass

    def set_bias_voltage(self):
        # Calls scripts_and_functions modules's bias_voltage_s3p() function using the voltage provided by
        # entry pull_in_v as
        # an input (used in TAB5)
        bias = self.pull_in_v.get()
        scripts_and_functions.bias_voltage(bias)
        self.error_log(scripts_and_functions.sig_gen)

    def set_symmetrical_voltage_bias(self, voltage: str = '10'):
        scripts_and_functions.bias_pullin(voltage)
        self.error_log(scripts_and_functions.sig_gen)

    def set_bias_pull_in(
            self):  # Calls scripts_and_functions modules's bias_voltage_s3p() function using the voltage provided by
        # entry pull_in_v as
        # an input (used in TAB4) !!!!FUNCTION IS LIKELY REDUNDANT!!!!
        bias = self.pull_in_v_bias.get()
        scripts_and_functions.bias_pullin(bias)
        self.error_log(scripts_and_functions.sig_gen)

    def set_ramp_width(self):  # Calls scripts_and_functions module's ramp_width(width) to set ramp width
        width = self.ramp_width.get()
        scripts_and_functions.ramp_width(width)
        self.error_log(scripts_and_functions.sig_gen)

    def set_prf(self):  # Calls scripts_and_functions modules's set_prf(prf) to set set pulse repetition frequency
        prf = self.pulse_freq.get()
        scripts_and_functions.set_prf(prf)
        self.error_log(scripts_and_functions.sig_gen)

    def set_pulse_width(self):  # Calls scripts_and_functions modules's set_pulse_width(width) to set pulse width
        width = self.pulse_width.get()
        scripts_and_functions.set_pulse_width(width)
        self.error_log(scripts_and_functions.sig_gen)

    # Plots functions -------------------------------------------------------------
    def trace_pull_down(self, conversion_coeff=0.040):
        # Measurement function that calls scripts_and_functions Module to trigger sig_gen to figure pull in trace and
        # display the measurement values in the text_file_name_s3p_test boxes(used in TAB6)
        # try:
        scripts_and_functions.sig_gen.write('TRIG')
        curve_det = scripts_and_functions.get_curve(channel=4)
        curve_bias = scripts_and_functions.get_curve(channel=2)
        t = curve_det[:, 1]
        rf_detector = -max(3 * curve_det[:, 0] / conversion_coeff) + 3 * curve_det[:, 0] / conversion_coeff
        v_bias = curve_bias[:, 0]
        # measurement_values = self.calculate_pull_in_out_voltage_measurement(v_bias, curve_det[:, 0])
        measurement_values = scripts_and_functions.calculate_pull_in_out_voltage_measurement(v_bias, curve_det[:, 0])
        plt.figure(num=4)
        number_of_graphs = len(self.ax_pull_in_meas.get_lines()[0:])
        for axes in self.ax_pull_in_meas.get_lines():
            axes.remove()
        self.ax_pull_in_meas.plot(v_bias, rf_detector, label='Cell {}'.format(self.test_pull_in_cell.get()),
                                  color='#1f77b4')
        self.ax_pull_in_meas.set(xlabel='Bias voltage (V)')
        self.ax_pull_in_meas.set(ylabel='Isolation (dB)')
        self.ax_pull_in_meas.grid(visible=True)
        self.ax_pull_in_meas.legend(fancybox=True, shadow=True)
        self.canvas_v_pull_in_meas.draw()
        self.text_pull_in_plus_test.delete("1.0", "end")
        self.text_pull_in_minus_test.delete("1.0", "end")
        self.text_pull_out_plus_test.delete("1.0", "end")
        self.text_pull_out_minus_test.delete("1.0", "end")
        self.text_iso_pull_in_plus_test.delete("1.0", "end")
        self.text_iso_pull_out_plus_test.delete("1.0", "end")
        self.text_iso_pull_in_minus_test.delete("1.0", "end")
        self.text_iso_pull_out_minus_test.delete("1.0", "end")
        self.text_pull_in_plus_test.insert(index="%d.%d" % (0, 0), chars=measurement_values['Vpullin_plus'])
        self.text_pull_in_minus_test.insert(index="%d.%d" % (0, 0), chars=measurement_values['Vpullin_minus'])
        self.text_pull_out_plus_test.insert(index="%d.%d" % (0, 0), chars=measurement_values['Vpullout_plus'])
        self.text_pull_out_minus_test.insert(index="%d.%d" % (0, 0), chars=measurement_values['Vpullout_minus'])
        self.text_iso_pull_in_plus_test.insert(index="%d.%d" % (0, 0),
                                               chars=measurement_values['Isolation_at_pullin_plus'])
        self.text_iso_pull_out_plus_test.insert(index="%d.%d" % (0, 0),
                                                chars=measurement_values['Isolation_at_pullout_plus'])
        self.text_iso_pull_in_minus_test.insert(index="%d.%d" % (0, 0),
                                                chars=measurement_values['Isolation_at_pullin_minus'])
        self.text_iso_pull_out_minus_test.insert(index="%d.%d" % (0, 0),
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
        time.sleep(1)
        os.chdir('{}'.format(self.test_s3p_dir.get()))
        try:
            s_par_network = rf.Network('{}'.format(entered_filename))
            s_par_network.frequency.unit = 'GHz'
            plt.figure(num=5, tight_layout=True)
            s_par_network.plot_s_db()
            self.ax_snp_meas.grid(visible=True)
            self.ax_snp_meas.legend(fancybox=True, shadow=True)
            self.canvas_snp_meas.draw()
        except Exception as e:
            print(e)

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
        except IndexError as ind:
            print("No more graphs to delete\n{ind}")

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
        except IndexError as ind:
            print("No more graphs to delete\n{ind}")

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
        self.text_gen_controls_pull_in_debug.delete("1.0", "end")
        error_logs = scripts_and_functions.print_error_log()
        self.text_snp_debug.insert(index="%d.%d" % (0, 0), chars=error_logs)
        self.text_gen_controls_pull_in_debug.insert(index="%d.%d" % (0, 0), chars=error_logs)

    def error_log(self, resource):
        error_log_resource = resource.query('SYSTem:ERRor?')
        time.sleep(1)
        error_string_resource = error_log_resource.split(",")[1]
        resource_name = resource.query('*IDN?').split(",")[:2]
        error_output = '{} ERROR LOG: {}\n'.format(resource_name, error_string_resource)
        self.text_snp_debug.delete("1.0", "end")
        self.text_snp_debug.insert(index="%d.%d" % (0, 0), chars=error_output)
        self.text_gen_controls_pull_in_debug.delete("1.0", "end")
        self.text_gen_controls_pull_in_debug.insert(index="%d.%d" % (0, 0), chars=error_output)
        return error_output

    def calculate_pull_in_out_voltage_measurement(self, v_bias,
                                                  v_log_amp):  # same function as in display implemented in measurement
        self.text_gen_controls_pull_in_debug.delete('1.0', tk.END)
        list_graph_ax4 = self.ax_pull_in_meas.lines[:]
        if not (list_graph_ax4 == []):
            list_graph_ax4[-1].remove()
        self.ax_pull_in_meas.legend(fancybox=True)
        self.canvas_v_pull_in_meas.draw()

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

        self.text_gen_controls_pull_in_debug.insert(index="%d.%d" % (1, 0),
                                                    chars='Isolation_at_pullout_minus = {} dB \n'.format(
                                                        tenpercent_iso_ascent))
        self.text_gen_controls_pull_in_debug.insert(index="%d.%d" % (1, 0),
                                                    chars='Vpullout_minus = {} V  \n'.format(Vpullout_minus))

        self.text_gen_controls_pull_in_debug.insert(index="%d.%d" % (1, 0),
                                                    chars='Isolation_at_pullin_minus = {} dB \n'.format(
                                                        ninetypercent_iso_descent))
        self.text_gen_controls_pull_in_debug.insert(index="%d.%d" % (1, 0),
                                                    chars='Vpullin_minus = {} V  \n'.format(Vpullin_minus))

        self.text_gen_controls_pull_in_debug.insert(index="%d.%d" % (1, 0),
                                                    chars='Isolation_at_pullout_plus = {} dB  \n'.format(
                                                        tenpercent_iso))
        self.text_gen_controls_pull_in_debug.insert(index="%d.%d" % (1, 0),
                                                    chars='Vpullout_plus = {} V  \n'.format(Vpullout))

        self.text_gen_controls_pull_in_debug.insert(index="%d.%d" % (1, 0),
                                                    chars='Isolation_at_pullin_plus = {} dB \n'.format(
                                                        ninetypercent_iso))
        self.text_gen_controls_pull_in_debug.insert(index="%d.%d" % (1, 0),
                                                    chars='Vpullin_plus = {} V  \n'.format(Vpullin))

        pull_dict = {'Vpullin_plus': Vpullin, 'Vpullout_plus': Vpullout, 'Isolation_at_pullin_plus': ninetypercent_iso,
                     'Isolation_at_pullout_plus': tenpercent_iso,
                     'Vpullin_minus': Vpullin_minus, 'Vpullout_minus': Vpullout_minus,
                     'Isolation_at_pullin_minus': ninetypercent_iso_descent,
                     'Isolation_at_pullout_minus': tenpercent_iso_ascent}
        return pull_dict

    def send_trig(self):
        scripts_and_functions.trigger_measurement_zva()
        self.error_log(scripts_and_functions.sig_gen)

    def sig_gen_cycling_config(self):
        scripts_and_functions.sig_gen_cycling_config()
        time.sleep(3)
        self.error_log(scripts_and_functions.sig_gen)

    def cycling_test(self):
        print("Started cycling")
        scripts_and_functions.set_osc_event_count(self.test_cycling_events.get())
        self.is_cycling = True

        # Clear previous data and plots
        self.file_df = pd.DataFrame(columns=["vpullin_plus", "vpullin_minus", "vpullout_plus", "vpullout_minus",
                                             "iso_ascent", "iso_descent_minus", "switching_time",
                                             "amplitude_variation", "release_time", "cycles"])

        self.update_plot()
        scripts_and_functions.set_osc_event_count(self.test_cycling_events.get())

        def run_cycling_sequence():
            scripts_and_functions.cycling_sequence(
                self,
                self.new_data_event,
                number_of_cycles=(self.test_cycling_var_nb_cycles.get()) * 1e5,
                number_of_pulses_in_wf=1000,
                filename=r'{}-{}-{}-{}-{}x10e5'.format(
                    self.test_cycling_project.get(),
                    self.test_cycling_ret.get(),
                    self.test_cycling_cell.get(),
                    self.test_cycling_device.get(),
                    self.test_cycling_var_nb_cycles.get(),
                    self.test_cycling_var_bias.get()
                ),
                events=self.test_cycling_events.get(),
                df_path=self.test_cycling_dir.get(),
                header=r"Comment:{},frequency:10GHz,Convertion coeff volts/dB:3*V/{}".format(
                    self.test_cycling_file_comment.get(), self.test_cycling_detector_conversion.get()),
                conversion_coeff=self.test_cycling_detector_conversion.get()
            )

        threading.Thread(target=run_cycling_sequence, daemon=True).start()

    def run_new_data_event(self):
        """
        Continuously checks for new data and updates the plot when new data is available.
        """
        while True:
            self.new_data_event_power_sweep.wait()  # Wait until the event is set
            if self.is_power_sweeping:
                self.update_plot_power_sweep()
            self.new_data_event_power_sweep.clear()  # Clear the event after updating the plot


if __name__ == "__main__":
    # root = tk.Tk()
    app = Window()
    app.mainloop()
