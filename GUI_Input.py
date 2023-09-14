import os
import tkinter as tk
import datetime
import calendar
from functools import partial
import pandas as pd
from General import data_path, text_size, order_categories
import General
import Error_Handler
import Planner

month, year = datetime.datetime.now().month, datetime.datetime.now().year
calendar_active = False

padx = 50
pady_top = 100
pady_bottom = 20

"""All widges or frames shown up"""
HinzufuegenButton_frame = None
FremdbearbeitungDauer_frame = None
BearbeitungsdauerProg_frame = None
Anlage_frame = None
calendar_frame = None
Liefertermin_frame = None
kunde_frame = None
auftragsnummer_frame = None
date_frame = None
kw_frame = None

# create global entrys and lists
kw_entry = None
date_entry = None
auftragsnummer_entry = None
kunden_liste = None
Liefertermin_entry = None
Anlagen_liste = None
Bearbeitungsdauer_entry = None
BearbeitungsdauerProg_entry = None
Fremdbearbeitungsdauer_entry = None
error_frame = None
kundennummer_entry = None

def start_Planner(root, df_orders, data):
    destroy_descriptions()
    Planner.main(root, df_orders, data)

def get_all_data():
    data = [None]*10
    # get the values from the entry boxes and lists
    data[0] = kw_entry.get()
    data[1] = date_entry.get()
    data[2] = auftragsnummer_entry.get()
    kunde = ""
    if(len(kunden_liste.curselection())!=0):
        kunde = kunden_liste.get(kunden_liste.curselection()[0])
    data[3] = kunde
    data[4] = Liefertermin_entry.get()
    Anlage = ""
    if(len(Anlagen_liste.curselection())!=0):
        Anlage = Anlagen_liste.get(Anlagen_liste.curselection()[0])
    data[5] = Anlage
    data[6] = Bearbeitungsdauer_entry.get()
    data[7] = BearbeitungsdauerProg_entry.get()
    data[8] = Fremdbearbeitungsdauer_entry.get()
    data[9] = kundennummer_entry.get()
    data[2] = data[2] + " / " + kundennummer_entry.get()
    return data

def create_error_messages(error_kind):
    error_message = ""
    for error in error_kind:
        if(error == "machine overload"):
            error_message += "Der Auftrag kann nicht in der regulären Arbeitstzeit erledigt werden.\n\r"
        if(error == "human overload"):
            error_message += "Markus hat nicht genügend Zeit, um den Auftrag in der regulären Zeit zu erledigen.\n\r"
        if(error == "impossible delivery date"):
            error_message += "Der Liefertermin ist nicht möglich, da er vor dem Fertigungsstart liegt.\n\r"
        if(error == "entries_missing"):
            error_message += "Es fehlen Eingaben.\n\r"
        if(error == "Fertigungsstart unvalid"):
            error_message += "Der Fertigungsstart ist kein gültiges Datum.\n\r"
        if(error == "Lieferdatum unvalid"):
            error_message += "Der Liefertermin ist kein gültiges Datum.\n\r"
    return error_message

def Hinzufuegen_button(root):
    global error_frame
    error_kind = []
    # get csv called "orders.csv" file from data folder if it exists
    df_orders = pd.DataFrame(columns=order_categories)
    # get KW from entry box
    kw = kw_entry.get()
    if(len(kw)==0):
        kw = datetime.date.today().isocalendar()[1]
    # get year from date entry box
    date = date_entry.get()
    if(len(date)==0):
        date = datetime.datetime.now().strftime("%d.%m.%Y")
    year = date.split(".")[2]
    # if there is data in the csv file named (kw_year_oders.csv), add it to the entry box
    if os.path.isfile(data_path+str(kw)+"_"+str(year)+"_orders.csv"):
        df_orders = pd.read_csv(data_path+str(kw)+"_"+str(year)+"_orders.csv")
    # get all inputs
    data = get_all_data()
    # check if input is valid
    if Error_Handler.main(error_kind, data):
        # create error frame
        error_frame = tk.Frame(root)
        # create error message
        error_message = create_error_messages(error_kind)
        # create a label with red text color
        error_label = tk.Label(error_frame, text=error_message, fg="red",font=("Helvetica", text_size))
        if General.acceptable_error(error_kind):
            # create a button to add the order anyway
            error_button = tk.Button(error_frame, text="Trotzdem Hinzufügen", command=partial(start_Planner, root, df_orders, data),font=("Helvetica", text_size))
            # place the button
            error_button.pack(side=tk.BOTTOM)
        # place the label
        error_label.pack(side=tk.TOP)
        # place the frame
        error_frame.place(relx=0.5, rely=0.9, anchor=tk.CENTER)
    else:
        destroy_descriptions()
        Planner.main(root, df_orders, data)

def Hinzufuegen(root):
    global HinzufuegenButton_frame
    HinzufuegenButton_frame = tk.Frame(root)
    # create a button
    Hinzufuegen = tk.Button(HinzufuegenButton_frame, text="Weiter", command=partial(Hinzufuegen_button, root),font=("Helvetica", text_size))
    # place the button
    Hinzufuegen.pack()
    HinzufuegenButton_frame.place(relx=0.75, rely=0.9)
    # update the root to fix entry widget bug (not showing up)
    root.update_idletasks()

def FremdbearbeitungDauer(root):
    # create a frame
    global FremdbearbeitungDauer_frame
    global Fremdbearbeitungsdauer_entry
    FremdbearbeitungDauer_frame = tk.Frame(root)
    # create a label
    FBD_lable = tk.Label(FremdbearbeitungDauer_frame, text="Fremdbearbeitungszeit:",font=("Helvetica", text_size))
    # create a entry box
    Fremdbearbeitungsdauer_entry = tk.Entry(FremdbearbeitungDauer_frame, width=3,font=("Helvetica", text_size))
    # place the label
    FBD_lable.pack(side=tk.TOP)
    Fremdbearbeitungsdauer_entry.pack(side=tk.BOTTOM)
    FremdbearbeitungDauer_frame.grid(row=1,column=3,padx=padx,pady=pady_bottom)
    # update the root to fix entry widget bug (not showing up)
    root.update_idletasks()

def BearbeitungsdauerProg(root):
    # create a frame
    global BearbeitungsdauerProg_frame
    global BearbeitungsdauerProg_entry
    BearbeitungsdauerProg_frame = tk.Frame(root)
    # create a label
    BearbeitungsdauerProg_lable = tk.Label(BearbeitungsdauerProg_frame, text="Entwicklungszeit:",font=("Helvetica", text_size))
    # create a entry box
    BearbeitungsdauerProg_entry = tk.Entry(BearbeitungsdauerProg_frame, width=3,font=("Helvetica", text_size))
    # place the label
    BearbeitungsdauerProg_lable.pack(side=tk.TOP)
    BearbeitungsdauerProg_entry.pack(side=tk.BOTTOM)
    BearbeitungsdauerProg_frame.grid(row=1,column=2,padx=padx,pady=pady_bottom)


def Anlage(root):
    # create frame
    global Anlage_frame
    global Bearbeitungsdauer_entry
    global Anlagen_liste
    Anlage_frame = tk.Frame(root)
    # create a label
    Bearbeitungsdauer_lable = tk.Label(Anlage_frame, text="Laufzeit:",font=("Helvetica", text_size))
    # create a entry box
    Bearbeitungsdauer_entry = tk.Entry(Anlage_frame, width=3,font=("Helvetica", text_size))
    # place the label
    Bearbeitungsdauer_lable.pack()
    Bearbeitungsdauer_entry.pack()

    # create a label
    Anlage_lable = tk.Label(Anlage_frame, text="Anlage:",font=("Helvetica", text_size))
    # create a entry box
    Anlagen_liste = tk.Listbox(Anlage_frame, height=3, width=8, selectmode=tk.EXTENDED,exportselection=False,font=("Helvetica", text_size))
    Anlagen_liste.insert(1, "Mazak")
    Anlagen_liste.insert(2, "Haas")
    Anlagen_liste.insert(3, "DMG Mori")
    # place the label and list
    Anlage_lable.pack()
    Anlagen_liste.pack()
    # place the frame
    Anlage_frame.grid(row=1,column=1,padx=padx,pady=pady_bottom)

def clear_grid(button_array):
    for button in button_array:
        button.grid_forget()

def update_calendar(month_text,button_array):
    # update corresponding month
    global month, year
    month_text.set(calendar.month_name[month]+ " " + str(year))
    clear_grid(button_array)
    # update corresponding days
    first_day = datetime.datetime(year, month, 1).weekday()
    for day in range(0, calendar.monthrange(year, month)[1]):
        row_num, col_num = divmod(day + 1 + first_day, 7)
        button_array[day].grid(row=row_num + 2, column=col_num + 1)

def prev_month(month_text,button_array):
    global month, year
    month -= 1
    if month == 0:
        month = 12
        year -= 1
    update_calendar(month_text,button_array)


def next_month(month_text,button_array):
    global month, year
    month += 1
    if month == 13:
        month = 1
        year += 1
    update_calendar(month_text,button_array)

def insert_entry(day,lt_entry):
    lt_entry.delete(0, tk.END)
    month_str = "{:02d}".format(month)
    lt_entry.insert(0, str(day) + "." + str(month_str) + "." + str(year))
    calendar_frame.destroy()

def Kalender(root,lt_entry):
    global calendar_active
    global calendar_frame

    if(calendar_active):
        calendar_frame.destroy()
        calendar_active = False
        return

    calendar_active = True
    # create frame to hold calendar
    calendar_frame = tk.Frame(root)
    calendar_frame.place(relx=0.2, rely=0.35)
    # create month label
    month_text = tk.StringVar()
    month_text.set(calendar.month_name[month]+ " " + str(year))
    # Create the calendar buttons
    button_array = []
    for day in range(1, 32):
        day_button = tk.Button(calendar_frame, text=str(day), command=partial(insert_entry, day, lt_entry),font=("Helvetica", text_size))
        button_array.append(day_button)
    first_day = datetime.datetime(year, month, 1).weekday()
    for day in range(0, calendar.monthrange(year, month)[1]):
        row_num, col_num = divmod(day  + first_day, 7)
        button_array[day].grid(row=row_num + 2, column=col_num + 1)
    # Create and configure widgets
    prev_button = tk.Button(calendar_frame, text="Vorheriger Monat", command=partial(prev_month,month_text,button_array),font=("Helvetica", text_size))
    next_button = tk.Button(calendar_frame, text="Nächster Monat", command=partial(next_month,month_text,button_array),font=("Helvetica", text_size))
    # Grid layout
    prev_button.grid(row=4, column=0)
    next_button.grid(row=4, column=8)
    label = tk.Label(calendar_frame, textvariable=month_text, justify="left",font=("Helvetica", text_size))
    label.grid(row=0, column=1, columnspan=7)
    for(column, day) in enumerate(["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]):
        label = tk.Label(calendar_frame, text=day,font=("Helvetica", text_size))
        label.grid(row=1, column=column+1)

def Liefertermin(root):
    #create a frame
    global Liefertermin_frame
    global Liefertermin_entry
    Liefertermin_frame = tk.Frame(root)
    # create a label
    Liefertermin_lable = tk.Label(Liefertermin_frame, text="Liefertermin:",font=("Helvetica", text_size))
    # create a entry box
    Liefertermin_entry = tk.Entry(Liefertermin_frame, width=10,font=("Helvetica", text_size))
    # create a button
    lt_button = tk.Button(Liefertermin_frame, text="Kalender", command=partial(Kalender, root, Liefertermin_entry),font=("Helvetica", text_size))
    # place the label
    Liefertermin_lable.pack(side=tk.TOP)
    Liefertermin_entry.pack(side=tk.BOTTOM)
    lt_button.pack(side=tk.RIGHT)
    Liefertermin_frame.grid(row=1, column=0,padx=padx, pady=pady_bottom)

def KundeAddButton(root, kunde_entry, df_kunden):
    kunde = kunde_entry.get()
    if(kunde == ""):
        return
    kunde_entry.delete(0, tk.END)
    # check if kunde already exists in df_kunden
    if(df_kunden[df_kunden['kunde'] == kunde].shape[0] == 0):
        neuer_kunde = {'kunde': kunde}
        if(df_kunden.empty):
            df_kunden = pd.DataFrame(columns=['kunde'])
        # New customer as a dictionary
        new_customer = {'kunde': kunde}
        # Convert the dictionary to a DataFrame and use pd.concat() to add it to the existing DataFrame
        new_df = pd.DataFrame([new_customer])
        df_kunden = pd.concat([df_kunden, new_df], ignore_index=True)
        df_kunden.to_csv(data_path+"kunden.csv",index=False)
        # reload kunden frame
        kunde_frame.destroy()
        Kunde(root)


def KundeHinzufuegen(root,kunde_frame,df_kunden):
    kunde_entry = tk.Entry(kunde_frame, width=12,font=("Helvetica", text_size))
    kunde_button = tk.Button(kunde_frame, text="Kunde Hinzufügen", command=partial(KundeAddButton, root, kunde_entry, df_kunden),font=("Helvetica", text_size))

    kunde_entry.pack(side=tk.BOTTOM)
    kunde_button.pack(side=tk.BOTTOM)
    # update the root to fix entry widget bug (not showing up)
    root.update_idletasks()

def KundeRemoveButton(root,df_kunden, kunden_liste):
    if(len(kunden_liste.curselection())==0):
        return
    kunde = kunden_liste.get(kunden_liste.curselection()[0])
    # find index of kunde in data frame
    index = df_kunden[df_kunden['kunde'] == kunde].index
    # delete row from data frame
    df_kunden.drop(index, inplace=True)
    # save data frame to csv
    df_kunden.to_csv(data_path + "kunden.csv", index=False)
    # reload kunden frame
    kunde_frame.destroy()
    Kunde(root)


def KundeLoeschen(root,kunde_frame,df_kunden,kunden_liste):
    kunde_button = tk.Button(kunde_frame, text="Kunde Löschen", command=partial(KundeRemoveButton, root, df_kunden,kunden_liste),font=("Helvetica", text_size))
    kunde_button.pack(side=tk.RIGHT)
    # update the root to fix entry widget bug (not showing up)
    root.update_idletasks()

def Kunde(root):
    # create a frame
    global kunde_frame
    global kunden_liste
    kunde_frame = tk.Frame(root)
    # create a label
    kunde_lable = tk.Label(kunde_frame, text="Kunde:", font=("Helvetica", text_size))
    # get csv called "kunden.csv" file from data folder if it exists
    df_kunden = pd.DataFrame()
    # create a listbox
    kunden_liste = tk.Listbox(kunde_frame, width=12, height=6, selectmode=tk.EXTENDED,exportselection=False, font=("Helvetica", text_size))
    # if there is data in the csv file, add it to the entry box
    if os.path.isfile(data_path+"kunden.csv"):
        df_kunden = pd.read_csv(data_path + "kunden.csv")
        if(df_kunden.shape[0] != 0):
            for(index, row) in df_kunden.iterrows():
                kunden_liste.insert(index, row['kunde'])

    # add button to add and remove customer
    KundeLoeschen(root, kunde_frame, df_kunden, kunden_liste)
    KundeHinzufuegen(root, kunde_frame, df_kunden)
    # place the label and list
    kunde_lable.pack(side=tk.TOP)
    kunden_liste.pack(side=tk.TOP)
    # place the frame
    kunde_frame.grid(row=0, column=3,padx=padx, pady=pady_top)
    # update the root to fix entry widget bug (not showing up)
    root.update_idletasks()

def Auftragsnummer(root):
    # create a frame
    global auftragsnummer_frame
    global auftragsnummer_entry
    global kundennummer_entry
    auftragsnummer_frame = tk.Frame(root)
    # create a label
    auftragsnummer_lable = tk.Label(auftragsnummer_frame, text="Auftragsnummer:", font=("Helvetica", text_size))
    # create a entry box
    auftragsnummer_entry = tk.Entry(auftragsnummer_frame, width=15, font=("Helvetica", text_size))
    # create a label
    kundennummer_lable = tk.Label(auftragsnummer_frame, text="Kundennummer:", font=("Helvetica", text_size))
    # create a entry box
    kundennummer_entry = tk.Entry(auftragsnummer_frame, width=15, font=("Helvetica", text_size))
    # place the label
    auftragsnummer_lable.pack(side=tk.TOP)
    auftragsnummer_entry.pack(side=tk.TOP)
    kundennummer_lable.pack()
    kundennummer_entry.pack(side=tk.BOTTOM)
    auftragsnummer_frame.grid(row=0, column=2,padx=padx, pady=pady_top)

def date(root):
    # create frame
    global date_frame
    global date_entry
    date_frame = tk.Frame(root)
    # create a label
    date_lable = tk.Label(date_frame, text="Fertigungsstart:", font=("Helvetica", text_size))
    # create a entry box
    date_entry = tk.Entry(date_frame, width=10, font=("Helvetica", text_size))
    # place the label
    date_lable.pack(side=tk.TOP)
    date_entry.pack(side=tk.BOTTOM)
    date_frame.grid(row=0, column=1,padx=padx, pady=pady_top)
    # get current date
    current_date = datetime.date.today()
    date_as_string = current_date.strftime("%d.%m.%Y")
    date_entry.insert(0, str(date_as_string))

def kw(root):
    # create frame
    global kw_frame
    global kw_entry
    kw_frame = tk.Frame(root)
    # create a label
    kw_lable = tk.Label(kw_frame, text="Kalenderwoche:", font=("Helvetica", text_size))
    # create a entry box
    kw_entry = tk.Entry(kw_frame, width=2, font=("Helvetica", text_size))
    # place the label
    kw_lable.pack(side=tk.TOP)
    kw_entry.pack(side=tk.BOTTOM)
    kw_frame.grid(row=0, column=0,padx=padx, pady=pady_top)
    # get current calendar week
    current_date = datetime.date.today()
    current_kw = current_date.isocalendar()[1]
    kw_entry.insert(0, str(current_kw))


def create_descriptions(root):
    kw(root)
    date(root)
    Auftragsnummer(root)
    Kunde(root)
    Liefertermin(root)
    Anlage(root)
    BearbeitungsdauerProg(root)
    FremdbearbeitungDauer(root)
    Hinzufuegen(root)

def destroy_descriptions():
    if(kw_frame != None):
        kw_frame.destroy()
    if(date_frame != None):
        date_frame.destroy()
    if(auftragsnummer_frame != None):
        auftragsnummer_frame.destroy()
    if(kunde_frame != None):
        kunde_frame.destroy()
    if(Liefertermin_frame != None):
        Liefertermin_frame.destroy()
    if(Anlage_frame != None):
        Anlage_frame.destroy()
    if(BearbeitungsdauerProg_frame != None):
        BearbeitungsdauerProg_frame.destroy()
    if(FremdbearbeitungDauer_frame != None):
        FremdbearbeitungDauer_frame.destroy()
    if(HinzufuegenButton_frame != None):
        HinzufuegenButton_frame.destroy()
    if(error_frame != None):
        error_frame.destroy()
    if(calendar_frame != None):
        calendar_frame.destroy()
    Planner.destroy_planner()

def main(root, on = True):
    if(on):
        create_descriptions(root)
    else:
        destroy_descriptions()