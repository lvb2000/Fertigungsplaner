import os
import tkinter as tk
import datetime
from functools import partial
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from General import data_path,text_size,arbeitsTag,order_categories
import copy
import calendar

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
Customer_frame = None
# 0 machine; 1 customers
current_frame = 0
prev_button = None
next_button = None

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

def destroy_week_select():
    global previous
    global next
    global entry
    if(previous != None and next != None and entry != None):
        previous.destroy()
        next.destroy()
        entry.destroy()

def get_kunden_on_day(df_orders, date):
    df = copy.copy(df_orders)
    # append target year to date
    date = date + "." + str(target_year)
    # convert date from %d.%m.%Y to %Y%m%d
    date = datetime.datetime.strptime(date, '%d.%m.%Y').strftime('%Y%m%d')
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y')
    df['Datum'] = df['Datum'].dt.strftime('%Y%m%d')
    df['Liefertermin'] = pd.to_datetime(df['Liefertermin'], format='%d.%m.%Y')
    df['Liefertermin'] = df['Liefertermin'].dt.strftime('%Y%m%d')
    # get all rows where date is after Datum and before Liefertermin
    df = df[(df.Datum <= date) & (df.Liefertermin >= date)]
    df['Datum'] = pd.to_datetime(df['Datum'], format='%Y%m%d')
    df['Datum'] = df['Datum'].dt.strftime('%d.%m.%Y')
    df['Liefertermin'] = pd.to_datetime(df['Liefertermin'], format='%Y%m%d')
    df['Liefertermin'] = df['Liefertermin'].dt.strftime('%d.%m.%Y')
    date = datetime.datetime.strptime(date, '%Y%m%d').strftime('%d.%m.%Y')
    # iterate through all rows
    kunden = []
    for index, row in df.iterrows():
        # get ProduktionsPlanung
        ProduktionsPlanung = eval(row['ProduktionsPlanung'])
        # get kunde
        kunde = row['Kunde']
        # iterate through all entries in ProduktionsPlanung
        for entry in ProduktionsPlanung:
            # check if entry[0] is equal to date
            if(entry[0] == date):
                if(int(entry[1]) != 0):
                    if(int(entry[2])==1):
                        # append kunde to kunden
                        kunden.append(kunde)
    return kunden


def create_column_chart(df_data,df_orders, frame, Maschine):
    global target_kw
    # remove all columns except that of the date and the machine
    df_machine = copy.copy(df_data[['date', Maschine]])
    # get a list of all dates in the target week
    dates = []
    # get the first day of the target week
    target_date = datetime.datetime.strptime(str(target_year) + "-" + str(target_kw) + "-1", '%Y-%W-%w').date()
    for i in range(0, 7):
        # add day to list in format "%%d.%m.%y" and increase day by i
        dates.append(str((target_date + datetime.timedelta(days=i)).strftime("%d.%m.%Y")))

    # add missing dates to the dataframe
    for date in dates:
        if not date in df_machine['date'].values:
            # add arbeitsTag if not sunday else add 0
            if (calendar.day_name[datetime.datetime.strptime(date, '%d.%m.%Y').weekday()] == "Sunday"):
                df_machine.loc[len(df_machine)] = [date, 0]
            else:
                df_machine.loc[len(df_machine)] = [date, arbeitsTag]
    # remove any dates from the dataframe that are not in the target week
    for date in df_machine['date'].values:
        if not date in dates:
            df_machine = df_machine[df_machine.date != date]

    # reset index
    df_machine.reset_index(drop=True, inplace=True)

    # update the machine column from available time entries to production hours computing: arbeitsTag - available time except Sunday
    for i in range(len(df_machine[Maschine])):
        # check if the day is a sunday
        if (calendar.day_name[datetime.datetime.strptime(df_machine['date'].iloc[i], '%d.%m.%Y').weekday()] == "Sunday"):
            df_machine.loc[i, Maschine] = 0
        else:
            df_machine.loc[i, Maschine] = arbeitsTag - df_machine.loc[i, Maschine]

    # sort the dataframe by date to ensure the correct order
    # therefor bring that in format "%y%m%d" sort them and reformat them to "%d.%m.%y"
    df_machine['date'] = pd.to_datetime(df_machine['date'], format='%d.%m.%Y')
    df_machine['date'] = df_machine['date'].dt.strftime('%Y%m%d')
    df_machine.sort_values(by=['date'], inplace=True)
    df_machine['date'] = pd.to_datetime(df_machine['date'], format='%Y%m%d')
    df_machine['date'] = df_machine['date'].dt.strftime('%d.%m.%Y')

    # cut the year of all dates
    df_machine['date'] = df_machine['date'].str[0:5]

    # Create the bar chart
    fig, ax = plt.subplots(figsize=(8, 2))  # Set the figure size as needed

    # Extract the dates and values
    dates = df_machine['date'].values
    values = df_machine[Maschine].values

    # Create a bar plot
    ax.bar(dates, values, color='black')

    # Set labels and title
    ax.set_xlabel('Datum')
    ax.set_ylabel('Nutzung in Stunden')
    ax.set_title(Maschine + ' - Auslastung pro Tag')

    # add a horizontal red line at 8 hours
    ax.axhline(y=8, color='r', linestyle='-')

    # get columns Datum and Kunde
    df_orders = df_orders[df_orders.Anlage == Maschine]
    df_kunden = copy.copy(df_orders[['Datum','Liefertermin', 'Kunde','ProduktionsPlanung']])
    # remove all entries which do not have the machine as Anlage
    # add the value on the top of each bar
    for i, v in enumerate(values):
        ax.text(i-0.05, v + 0.25, str(v), color='black', fontweight='bold')
        kunden = get_kunden_on_day(df_kunden, dates[i])
        for j, kunde in enumerate(kunden):
            ax.text(i-0.1, v + 0.25 + (j+1)*4, kunde, color='black', fontweight='bold')


    # Rotate x-axis labels for better readability (optional)
    plt.xticks(rotation=45)

    # set y-axis to fixed size of 8 Hours
    ax.set_ylim(0, 24)

    # Ensures the labels fit within the figure
    fig.tight_layout()

    # Create a Tkinter canvas to embed the Matplotlib plot
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.LEFT)

    # delete figure to prevent memory leak
    plt.close(fig)


def create_all_column_chart(root):
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
    if os.path.isfile(data_path+'occupation.csv'):
        df_data = pd.read_csv(data_path+'occupation.csv')
    else:
        # create empty dataframe
        df_data = pd.DataFrame(columns=['date','Mazak','Haas','DMG Mori','Marcus'])
    # read orders from csv
    if os.path.isfile(data_path+str(target_kw)+"_"+str(target_year)+'_orders.csv'):
        df_orders = pd.read_csv(data_path+str(target_kw)+"_"+str(target_year)+'_orders.csv')
    else:
        df_orders = pd.DataFrame(columns= order_categories)
    # create a list of all machines
    machines = ["Mazak","Haas","DMG Mori"]
    frames = [Mazak_frame,Haas_frame,DMG_frame]

    for(i,machine) in enumerate(machines):
        create_column_chart(df_data,df_orders, frames[i], machine)

def create_bar_chart(df_data, frame, Maschine):
    # get a list of all dates in the target week
    dates = []
    # get the first day of the target week
    target_date = datetime.datetime.strptime(str(target_year) + "-" + str(target_kw) + "-1", '%Y-%W-%w').date()
    for i in range(0, 7):
        # add day to list in format "%%d.%m.%y" and increase day by i
        dates.append(str((target_date + datetime.timedelta(days=i)).strftime("%d.%m.%Y")))
    # remove any dates from the dataframe that are not in the target week
    for date in df_data['date'].values:
        if not date in dates:
            df_data = df_data[df_data.date != date]
    # get the sum of all values in the column maschine
    sum = df_data[Maschine].sum()
    # for each entry in the column maschine remove arbeitsTag from sum
    total_hours = 0
    for i in range(len(df_data[Maschine])):
        # add arbeitsTag to total_hours if not Sunday
        if (calendar.day_name[datetime.datetime.strptime(df_data['date'].iloc[i], '%d.%m.%Y').weekday()] != "Sunday"):
            total_hours += arbeitsTag
    sum = total_hours - sum
    # define total hours of a week
    total = 40
    # calculate the percentage
    percentage = int(sum / total * 100)

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

def create_all_bar_chart(df_data):
    global target_kw
    global target_year
    global Mazak_frame
    global Haas_frame
    global DMG_frame
    # read data from csv
    if os.path.isfile(data_path+'occupation.csv'):
        df_data = pd.read_csv(data_path+'occupation.csv')
    else:
        # create empty dataframe
        df_data = pd.DataFrame(columns=['date','Mazak','Haas','DMG Mori','Marcus'])
    # create a list of all machines
    machines = ["Mazak","Haas","DMG Mori"]
    frames = [Mazak_frame,Haas_frame,DMG_frame]

    for(i,machine) in enumerate(machines):
        create_bar_chart(df_data, frames[i], machine)

    # place frame under top buttons
    Mazak_frame.place(relx=0.1, rely=0.12)
    Haas_frame.place(relx=0.1, rely=0.34)
    DMG_frame.place(relx=0.1, rely=0.56)


def create_machine_overview(root):
    create_all_column_chart(root)
    create_all_bar_chart(root)

def destroy_machine_overview():
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

def add_to_df_display(df_display, df_data):
    # loop over all entries in enumerated df_data
    for i, row in enumerate(df_data.iterrows()):
        # get 'kunde' entry of row and add the value to the corresponding index in df_display at col hours
        df_display.loc[row[0], 'Hours'] += row[1]['Bearbeitungsdauer'] + row[1]['BearbeitungsdauerProg']

def create_pie_chart(root):
    global Customer_frame
    # get kunden csv if it exists
    df_kunden = pd.DataFrame(columns=['kunde'])
    if os.path.isfile(data_path+'kunden.csv'):
        df_kunden = pd.read_csv(data_path+'kunden.csv')
    # init display df
    df_display = pd.DataFrame(columns=['Hours'])
    # for all entries in df_kunden make a new index in df_display
    for kunde in df_kunden['kunde']:
        df_display.loc[kunde] = [0]
    # loop over all possible kws in current year
    for kw in range(1, 53):
        # get current year as integer in long format
        year = datetime.date.today().isocalendar()[0]
        # check if according data csv exists
        if os.path.isfile(data_path + str(kw) + "_" + str(year) + "_orders.csv"):
            # read data from csv
            df_data = pd.read_csv(data_path + str(kw) + "_" + str(year) + "_orders.csv")
            # remove all entries except Bearbeitungsdauer, BearbeitungsdauerProg, Kunde
            df_data = df_data[['Bearbeitungsdauer', 'BearbeitungsdauerProg', 'Kunde']]
            # group by Kunde and sum up the values
            df_data = df_data.groupby(['Kunde']).sum()
            # add the values to df_display
            add_to_df_display(df_display, df_data)
    # sort df_display by hours
    df_display.sort_values(by=['Hours'], inplace=True, ascending=False)
    # remove all entries with 0 hours
    df_display = df_display[df_display.Hours != 0]
    # display df_display as pie chart with one slice for each kunde with individual color
    fig, ax = plt.subplots(figsize=(6, 6))  # Set the figure size as needed
    # Create a pie chart
    ax.pie(df_display['Hours'], labels=df_display.index, startangle=90)
    # Set the title
    ax.set_title('Kunden - Vergleich')
    # Ensures the labels fit within the figure
    fig.tight_layout()
    # Create a Tkinter canvas to embed the Matplotlib plot
    canvas = FigureCanvasTkAgg(fig, master=Customer_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()
    # delete figure to prevent memory leak
    plt.close(fig)


def create_customer_overview(root):
    global Customer_frame
    # create frame for the chart
    Customer_frame = tk.Frame(root)
    create_pie_chart(root)
    Customer_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

def destroy_customer_overview():
    global Customer_frame
    # if frames != None destroy
    if(Customer_frame != None):
        Customer_frame.destroy()

def change_display(root,factor):
    global current_frame
    current_frame += factor
    if(current_frame > 1):
        current_frame = 1
        return
    if(current_frame < 0):
        current_frame = 0
        return
    if(current_frame == 0):
        destroy_customer_overview()
        create_week_select(root)
        create_machine_overview(root)
    if(current_frame == 1):
        destroy_machine_overview()
        destroy_week_select()
        create_customer_overview(root)
def create_overview(root):
    global prev_button
    global next_button
    create_week_select(root)
    create_machine_overview(root)
    # create buttons to change overview
    prev_button = tk.Button(root, text="Vorheriger", command=partial(change_display, root,-1),font=("Helvetica", text_size))
    next_button = tk.Button(root, text="Nächster", command=partial(change_display, root,+1),font=("Helvetica", text_size))
    prev_button.place(relx=0.1, rely=0.9)
    next_button.place(relx=0.8, rely=0.9)

def destroy_overview_select():
    global prev_button
    global next_button
    if(prev_button != None and next_button != None):
        prev_button.destroy()
        next_button.destroy()
def destroy_overview(root):
    destroy_week_select()
    destroy_machine_overview()
    destroy_customer_overview()
    destroy_overview_select()


def main(root,on = True):
    if (on):
        create_overview(root)
    else:
        destroy_overview(root)