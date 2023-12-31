import os
import tkinter as tk
import datetime
from functools import partial
from tkinter import font

import pandas as pd
from General import data_path,text_size,list_size,order_categories,date1_before_date2,arbeitsTag,get_weeks

"""Geometrics of tkinter"""
padx=0

"""Keep Log of the displayed week"""
current_kw = datetime.date.today().isocalendar()[1]
current_year = datetime.date.today().isocalendar()[0]
reset = False
reset_kw = 0
reset_year = 0

"""Global tkinter widgets"""
frame = None
previous = None
next = None
entry = None

"""Order Status"""
Status = []

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
    destroy_table()
    # create table
    create_table(root)

def previous_kw(root,entry):
    update_kw_and_year(root,entry,-1)

def next_kw(root,entry):
    update_kw_and_year(root,entry,1)

def delete_row(entry,root,index,df_data):
    global reset
    global reset_kw
    global reset_year
    # get current value
    reset = True
    entry = entry.get().split(' - ')
    reset_kw = int(entry[0])
    reset_year = int(entry[1])
    # get the occuption csv as df
    df_occupation = pd.read_csv(data_path + "occupation.csv")
    # get row of index
    row = df_data.iloc[index]
    machines = ['Mazak','Haas','DMG_Mori']
    for machine in machines:
        # get the ProduktionsPlanung which is a list but saved as string
        ProduktionsPlanung = eval(row['ProduktionsPlanung'+ machine])
        # loop over produktionsplanung
        for Tag in ProduktionsPlanung:
            # add to df_occupation at date of Tag[0] and column of machine the value of Tag[1]
            df_occupation.loc[df_occupation['date'] == Tag[0], machine] += Tag[1]
    # save df_occupation
    df_occupation.to_csv(data_path + "occupation.csv", index=False)
    # get auftragsnummer
    auftragsnummer = row.iloc[2]
    # get all kw between data[1] and data[4]
    kw = []
    # get the start date
    start_date = datetime.datetime.strptime(row.iloc[1], '%d.%m.%Y')
    # get the end date
    end_date = datetime.datetime.strptime(row.iloc[4], '%d.%m.%Y')
    # loop over all days
    for i in range((end_date - start_date).days + 1):
        # get the date of the day plus i
        date = start_date + datetime.timedelta(days=i)
        # get the kw of the date
        kw.append(date.strftime("%V"))
    # get the unique kw
    kw = list(set(kw))
    # get the year of the order
    year = datetime.datetime.strptime(row.iloc[1], '%d.%m.%Y').year
    # for each kw read the csv file, append the new df and save it
    for week in kw:
        # read csv file
        df = pd.read_csv(data_path + str(week) + "_" + str(year) + '_orders.csv')
        # delete row from data with same auftragsnummer
        df = df[df['Auftragsnummer'] != auftragsnummer]
        # save df
        df.to_csv(data_path + str(week) + "_" + str(year) + '_orders.csv', index=False)
    # destroy table
    destroy_table()
    # create table
    create_table(root)

def toggle_status(root,df_data,index,target_kw,target_year):
    global reset
    global reset_kw
    global reset_year
    # toggle the status of df_data at index without getting SettingWithCopyWarning
    df_data.loc[index, 'Status'] = 1 - df_data.loc[index, 'Status']
    # get todays date in format dd.mm.yyyy
    today = datetime.date.today().strftime("%d.%m.%Y")

    kw = get_weeks(df_data.loc[index,'Datum'],df_data.loc[index, 'Liefertermin'])
    # get auftragsnummer at index
    auftragsnummer = df_data.loc[index, 'Auftragsnummer']
    # update occupation
    factor = None
    if(df_data.loc[index, 'Status'] == 1):
        factor = 1
        # add today to df_occupation placeholder 1
        df_data.loc[index, 'Placeholder1'] = today
        for week in kw:
            # read csv file
            df = pd.read_csv(data_path + str(week) + "_" + str(target_year) + '_orders.csv')
            # update produktionsplanung+machine at auftragsnummer
            df.loc[df['Auftragsnummer'] == auftragsnummer, 'Placeholder1'] = today
            # save df
            df.to_csv(data_path + str(week) + "_" + str(target_year) + '_orders.csv', index=False)
    else:
        factor = -1
        today = df_data.loc[index, 'Placeholder1']
        for week in kw:
            # read csv file
            df = pd.read_csv(data_path + str(week) + "_" + str(target_year) + '_orders.csv')
            # update produktionsplanung+machine at auftragsnummer
            df.loc[df['Auftragsnummer'] == auftragsnummer, 'Placeholder1'] = ""
            # save df
            df.to_csv(data_path + str(week) + "_" + str(target_year) + '_orders.csv', index=False)
    # get the occuption csv as df
    df_occupation = pd.read_csv(data_path + "occupation.csv")
    # get machines array
    machines = ['Mazak','Haas','DMG_Mori']
    for machine in machines:
        # from df_data get ProduktionsPlanung
        ProduktionsPlanung = eval(df_data.loc[index, 'ProduktionsPlanung'+machine])
        # for each day in ProduktionsPlanung which is larger than today add/remove the value of the order to occupation
        for Tag in ProduktionsPlanung:
            # check if Tag[0] is before today
            if(date1_before_date2(today,Tag[0])):
                # update occupation
                df_occupation.loc[df_occupation['date'] == Tag[0], machine] += Tag[1]*factor
                # update ProduktionsPlanung
                if(factor == 1):
                    Tag[2] = 0
                else:
                    Tag[2] = 1
                # if df_occupation is bigger than arbeitsTag set it to arbeitsTag
                if(df_occupation.loc[df_occupation['date'] == Tag[0], machine].values[0] > arbeitsTag):
                    df_occupation.loc[df_occupation['date'] == Tag[0], machine] = arbeitsTag
        # update ProduktionsPlanung
        for week in kw:
            # read csv file
            df = pd.read_csv(data_path + str(week) + "_" + str(target_year) + '_orders.csv')
            # update produktionsplanung+machine at auftragsnummer
            df.loc[df['Auftragsnummer'] == auftragsnummer, 'ProduktionsPlanung'+machine] = str(ProduktionsPlanung)
            df.loc[df['Auftragsnummer'] == auftragsnummer, 'Status'] = 1 - df.loc[df['Auftragsnummer'] == auftragsnummer, 'Status']
            # save df
            df.to_csv(data_path + str(week) + "_" + str(target_year) + '_orders.csv', index=False)
    # save df_occupation
    df_occupation.to_csv(data_path + "occupation.csv", index=False)


    reset = True
    reset_kw = target_kw
    reset_year = target_year
    # destroy table
    destroy_table()
    # create table
    create_table(root)



def create_table(root):
    global frame
    global previous
    global next
    global entry
    global reset
    global padx
    global Status
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
    previous = tk.Button(root, text="Vorherige Kalenderwoche", command=partial(previous_kw,root,entry),font=("Helvetica", text_size))
    next = tk.Button(root, text="Nächste Kalenderwoche", command=partial(next_kw,root,entry),font=("Helvetica", text_size))
    # place everything
    previous.place(relx=0.42, rely=0.02)
    next.place(relx=0.77, rely=0.02)
    entry.place(relx=0.66, rely=0.02)

    # create a table
    # create a frame
    frame = tk.Frame(root)
    # create lable for each category
    categories = ['Datum', 'A-Nummer / KD-Nummer', 'Kunde', 'Liefertermin', 'Anlage', 'Fräsen[h]', 'Prog[h]', 'Extern[h]','Status','Löschen']
    for i in range(len(categories)):
        label = tk.Label(frame, text=categories[i],font=("Helvetica", text_size))
        label.grid(row=0, column=i,padx=padx)

    # draw a line between categories and data
    separator = tk.Canvas(frame, width=1500, height=2, bg="black")
    separator.grid(row=1, column=0, columnspan=10)

    # narrow line spacing font
    #custom_font = font.Font(family="Helvetica", size=list_size, spacing=10)
    # reset status
    Status = []
    # read data from csv
    if os.path.isfile(data_path+str(target_kw)+"_"+str(target_year)+'_orders.csv'):
        df_data = pd.read_csv(data_path+str(target_kw)+"_"+str(target_year)+'_orders.csv')
        # move all orders with status 1 to the end
        df_data = df_data.sort_values(by=['Status'])
        # reset index
        df_data = df_data.reset_index(drop=True)
        # Iterate through data rows using iterrows()
        for index, row in df_data.iterrows():
            # create a label for each data entry in row
            label = tk.Label(frame, text=row.iloc[1],font=("Helvetica", list_size))
            label.grid(row=index+2, column=0,padx=padx)
            label = tk.Label(frame, text=row.iloc[2], font=("Helvetica", list_size))
            label.grid(row=index + 2, column=1, padx=padx)
            label = tk.Label(frame, text=row.iloc[3], font=("Helvetica", list_size))
            label.grid(row=index + 2, column=2, padx=padx)
            label = tk.Label(frame, text=row.iloc[4], font=("Helvetica", list_size))
            label.grid(row=index + 2, column=3, padx=padx)
            #label = tk.Label(frame, text=row[5], font=("Helvetica", list_size))
            #label.grid(row=index + 2, column=4, padx=padx)
            text_name=""
            text_value=""
            first=False
            if(row.iloc[5]!=0):
                text_name="Mazak"
                text_value=str(row.iloc[5])
                first=True
            if(row.iloc[6]!=0):
                if(first):
                    text_name+="\n"
                    text_value+="\n"
                first=True
                text_name+="Haas"
                text_value+=str(row.iloc[6])
            if(row.iloc[7]!=0):
                if(first):
                    text_name+="\n"
                    text_value+="\n"
                text_name+="DMG Mori"
                text_value+=str(row.iloc[7])
            label = tk.Label(frame, text=text_name, font=("Helvetica", list_size), wraplength=100)
            label.grid(row=index + 2, column=4, padx=padx)
            label = tk.Label(frame, text=text_value, font=("Helvetica", list_size), wraplength=100)
            label.grid(row=index + 2, column=5, padx=padx)
            label = tk.Label(frame, text=row.iloc[8], font=("Helvetica", list_size))
            label.grid(row=index + 2, column=6, padx=padx)
            label = tk.Label(frame, text=row.iloc[9], font=("Helvetica", list_size))
            label.grid(row=index + 2, column=7, padx=padx)
            if(row.iloc[13]==1 or date1_before_date2(row.iloc[4],datetime.date.today().strftime("%d.%m.%Y"))):
                Status.append(tk.IntVar(value=1))
            else:
                Status.append(tk.IntVar(value=0))
            # create a tkinter checkbox
            checkbox = tk.Checkbutton(frame, text='',variable=Status[index], onvalue=1, offvalue=0, command=partial(toggle_status,root,df_data,index,target_kw,target_year))
            checkbox.grid(row=index+2, column=8,padx=padx)
            if(Status[index].get() == 0):
                # create a button to delete the row
                delete = tk.Button(frame, text="X", command=partial(delete_row,entry,root,index,df_data),font=("Helvetica", list_size))
                # place the button
                delete.grid(row=index+2, column=9,padx=padx)

    # place frame under top buttons
    frame.place(relx=0, rely=0.1)

    # update the root to fix entry widget bug (not showing up)
    root.update_idletasks()

def destroy_table():
    global frame
    global previous
    global next
    global entry
    # destroy frame
    if(frame != None):
        frame.destroy()
    # destroy buttons
    if(previous != None):
        previous.destroy()
    if(next != None):
        next.destroy()
    # destroy entry
    if(entry != None):
        entry.destroy()

def main(root,on = True):
    if (on):
        create_table(root)
    else:
        destroy_table()
