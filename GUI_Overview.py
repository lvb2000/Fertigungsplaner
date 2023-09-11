import os
import tkinter as tk
import datetime
from functools import partial
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from General import data_path,text_size

"""Keep Log of the displayed week"""
current_kw = datetime.date.today().isocalendar()[1]
current_year = datetime.date.today().isocalendar()[0]
reset = False
reset_kw = 0
reset_year = 0
target_kw = 0
target_year = 0

"""Global tkinter widgets"""
previous = None
next = None
entry = None

"""Global chart frames"""
Mazak_frame = None
Haas_frame = None
DMG_frame = None

def update_kw_and_year(root,entry,factor):
    global reset
    global reset_kw
    global reset_year
    reset = True
    entry = entry.get().split(' - ')
    reset_kw = int(entry[0]) + factor
    reset_year = int(entry[1])
    if(reset_kw < 1):
        reset_kw = 52
        reset_year = int(entry[1]) - 1
    if(reset_kw > 52):
        reset_kw = 1
        reset_year = int(entry[1]) + 1
    # destroy table
    destroy_overview(root)
    # create table
    create_overview(root)

def previous_kw(root,entry):
    update_kw_and_year(root,entry,-1)

def next_kw(root,entry):
    update_kw_and_year(root,entry,1)

def create_week_select(root):
    global previous
    global next
    global entry
    global reset
    global padx
    global target_kw
    global target_year
    # create a entry
    entry = tk.Entry(root, width=9,font=("Helvetica", text_size))
    target_kw = current_kw
    target_year = current_year
    if(reset):
        reset = False
        target_kw = reset_kw
        target_year = reset_year
    entry.insert(0, str(target_kw)+" - "+str(target_year))
    # create a button
    previous = tk.Button(root, text="Vorherige Kalenderwoche", command=partial(previous_kw, root, entry),font=("Helvetica", text_size))
    next = tk.Button(root, text="Nächste Kalenderwoche", command=partial(next_kw, root, entry),font=("Helvetica", text_size))
    # place everything
    previous.place(relx=0.42, rely=0.02)
    next.place(relx=0.77, rely=0.02)
    entry.place(relx=0.66, rely=0.02)
    # update the root to fix entry widget bug (not showing up)
    root.update_idletasks()

def destroy_week_select(root):
    global previous
    global next
    global entry
    if(previous != None and next != None and entry != None):
        previous.destroy()
        next.destroy()
        entry.destroy()

def create_bar_chart(df_data,frame,Maschine):
    global target_kw
    # remove all rows except 'Datum' and 'BearbeitungsdauerProg'
    df_data = df_data[['Datum', 'Bearbeitungsdauer']]
    # accumulate all values in the column 'BearbeitungsdauerProg' for every date in the week individually and safe in a array
    df_data = df_data.groupby(['Datum']).sum()
    # get a list of all dates in the target week
    dates = []
    # get the first day of the target week
    target_date = datetime.datetime.strptime(str(target_year) + "-" + str(target_kw) + "-1", '%Y-%W-%w').date()
    for i in range(0, 7):
        # add day to list in format "%%d.%m.%y" and increase day by i
        dates.append(str((target_date + datetime.timedelta(days=i)).strftime("%d.%m.%Y")))

    # add missing dates to the dataframe
    for date in dates:
        if not date in df_data.index:
            df_data.loc[date] = 0
    # sort the dataframe by index
    df_data.sort_index(inplace=True)

    # cut the year of all dates
    df_data.index = df_data.index.str[0:5]

    # Create the bar chart
    fig, ax = plt.subplots(figsize=(8, 2))  # Set the figure size as needed

    # Extract the dates and values
    dates = df_data.index
    values = df_data['Bearbeitungsdauer']

    # Create a bar plot
    ax.bar(dates, values, color='black')

    # Set labels and title
    ax.set_xlabel('Datum')
    ax.set_ylabel('Nutzung in Stunden')
    ax.set_title(Maschine + ' - Auslastung pro Tag')

    # add a horizontal red line at 8 hours
    ax.axhline(y=8, color='r', linestyle='-')

    # add the value on the top of each bar
    for i, v in enumerate(values):
        ax.text(i-0.05, v + 0.25, str(v), color='black', fontweight='bold')

    # Rotate x-axis labels for better readability (optional)
    plt.xticks(rotation=45)

    # set y-axis to fixed size of 8 Hours
    ax.set_ylim(0, 10)

    # Ensures the labels fit within the figure
    fig.tight_layout()

    # Create a Tkinter canvas to embed the Matplotlib plot
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.LEFT)

    # delete figure to prevent memory leak
    plt.close(fig)


def create_all_bar_chart(root):
    global target_kw
    global target_year
    global Mazak_frame
    global Haas_frame
    global DMG_frame
    # create frame for the chart
    Mazak_frame = tk.Frame(root, width=1920, height=350)
    Haas_frame = tk.Frame(root, width=1920, height=350)
    DMG_frame = tk.Frame(root, width=1920, height=350)
    # read data from csv
    if os.path.isfile(data_path+str(target_kw)+"_"+str(target_year)+'_orders.csv'):
        df_data = pd.read_csv(data_path+str(target_kw)+"_"+str(target_year)+'_orders.csv')
    else:
        # create empty dataframe
        df_data = pd.DataFrame(columns=['Kalenderwoche', 'Datum', 'Auftragsnummer', 'Kunde', 'Liefertermin', 'Anlage', 'Bearbeitungsdauer',
         'BearbeitungsdauerProg', 'Fremdbearbeitungsdauer'])

    # create a list of all machines
    machines = ["Mazak","Haas","DMG Mori"]
    frames = [Mazak_frame,Haas_frame,DMG_frame]

    for(i,machine) in enumerate(machines):
        create_bar_chart(df_data[df_data['Anlage'] == machine],frames[i],machine)

def create_pie_chart(df_data,frame,Maschine):
    # get the sum of all values in the column 'Bearbeitungsdauer'
    sum = df_data['Bearbeitungsdauer'].sum()
    # define total hours of a week
    total = 40
    # calculate the percentage of the sum
    percentage = sum / total * 100

    # Create a color map from bright green to dark red
    cmap = cm.get_cmap('RdYlGn_r')
    color = cmap(percentage / 150.0)  # Normalize the percentage to the range [0, 1]

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(4, 1))

    # Create a horizontal bar with the color representing the percentage
    bar = ax.barh(0, percentage, color=color)

    # Set the x-axis limit to accommodate the percentage (from 0% to 150%)
    ax.set_xlim(0, 150)

    # Add a label to the bar to display the percentage value
    ax.text(percentage + 5, 0, f"{percentage}%", va='center', fontsize=12)

    # Remove y-axis ticks and labels
    ax.set_yticks([])
    ax.set_yticklabels([])
    # Remove x-axis ticks and labels
    ax.set_xticks([])
    ax.set_xticklabels([])

    # Set the title
    ax.set_title(Maschine+ ' - Prozentuale Auslastung')

    # Ensures the labels fit within the figure
    fig.tight_layout()

    # Create a Tkinter canvas to embed the Matplotlib plot
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.RIGHT)
    # delete figure to prevent memory leak
    plt.close(fig)

def create_all_pie_chart(df_data):
    global target_kw
    global target_year
    global Mazak_frame
    global Haas_frame
    global DMG_frame
    # read data from csv
    if os.path.isfile(data_path+str(target_kw)+"_"+str(target_year)+'_orders.csv'):
        df_data = pd.read_csv(data_path+str(target_kw)+"_"+str(target_year)+'_orders.csv')
    else:
        # create empty dataframe
        df_data = pd.DataFrame(columns=['Kalenderwoche', 'Datum', 'Auftragsnummer', 'Kunde', 'Liefertermin', 'Anlage', 'Bearbeitungsdauer',
         'BearbeitungsdauerProg', 'Fremdbearbeitungsdauer'])

    # create a list of all machines
    machines = ["Mazak","Haas","DMG Mori"]
    frames = [Mazak_frame,Haas_frame,DMG_frame]

    for(i,machine) in enumerate(machines):
        create_pie_chart(df_data[df_data['Anlage'] == machine],frames[i],machine)

    # place frame under top buttons
    Mazak_frame.place(relx=0.1, rely=0.12)
    Haas_frame.place(relx=0.1, rely=0.34)
    DMG_frame.place(relx=0.1, rely=0.56)


def create_charts(root):
    create_all_bar_chart(root)
    create_all_pie_chart(root)

def destroy_charts(root):
    global Mazak_frame
    global Haas_frame
    global DMG_frame
    # if frames != None destroy
    if(Mazak_frame != None):
        Mazak_frame.destroy()
    if(Haas_frame != None):
        Haas_frame.destroy()
    if(DMG_frame != None):
        DMG_frame.destroy()

def create_overview(root):
    create_week_select(root)
    create_charts(root)

def destroy_overview(root):
    destroy_week_select(root)
    destroy_charts(root)

def main(root,on = True):
    if (on):
        create_overview(root)
    else:
        destroy_overview(root)