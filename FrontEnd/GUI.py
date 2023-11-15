import tkinter as tk
from functools import partial
from FrontEnd import GUI_Table, GUI_Overview, GUI_Input
from General import text_size,data_path

"""Create a button to quit the program."""
def create_exit_button(root):
    # create a button
    exit = tk.Button(root, text="Exit", command=root.destroy, font=("Helvetica", text_size))
    # place the button
    exit.pack()
    exit.place(relx=0.9, rely=0.9)

"""Create a button to switch between different panels."""
def input_switch(root):
    panel_mode = "input"
    GUI_Input.main(root, False)
    GUI_Table.main(root, False)
    GUI_Overview.main(root, False)
    GUI_Input.main(root)

def create_input_button(root):
    # create a button
    overview = tk.Button(root, text="Eingabe", command=partial(input_switch, root),font=("Helvetica", text_size))
    # place the button
    overview.pack()
    overview.place(relx=0.05, rely=0.02)

def table_switch(root):
    panel_mode = "table"
    GUI_Input.main(root, False)
    GUI_Table.main(root, False)
    GUI_Overview.main(root, False)
    GUI_Table.main(root)

def create_table_button(root):
    # create a button
    overview = tk.Button(root, text="Aufträge", command=partial(table_switch,root),font=("Helvetica", text_size))
    # place the button
    overview.pack()
    overview.place(relx=0.15, rely=0.02)

def overview_switch(root):
    panel_mode = "overview"
    GUI_Input.main(root, False)
    GUI_Table.main(root, False)
    GUI_Overview.main(root, False)
    GUI_Overview.main(root)
def create_overview_button(root):
    #create a button
    overview = tk.Button(root, text="Übersicht", command=partial(overview_switch,root),font=("Helvetica", text_size))
    # place the button
    overview.pack()
    overview.place(relx=0.25, rely=0.02)

def start_gui():
    # create the Tk object
    root = tk.Tk()
    # set cnc logo in background with high transparency (alpha)
    cnc_logo = tk.PhotoImage(file=data_path+"cncLogoLowOp.png")
    cnc_logo_label = tk.Label(root, image=cnc_logo)
    cnc_logo_label.image = cnc_logo
    cnc_logo_label.place(x=0, y=0, relwidth=1, relheight=1)
    # create a button to quit the program
    create_exit_button(root)
    # create buttons to switch between different panels
    create_input_button(root)
    create_table_button(root)
    create_overview_button(root)
    # set the title of the window
    root.title("CNC Metzger")

    #increase the starting size of the window
    root.geometry("1920x1080")
    # run the GUI
    root.mainloop()