import os
import tkinter as tk
import datetime
from functools import partial
import pandas as pd
from General import data_path,text_size,list_size,order_categories

"""Geometrics of tkinter"""
padx=33

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
    destroy_table(root)
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
    # get the ProduktionsPlanung which is a list but saved as string
    ProduktionsPlanung = eval(row['ProduktionsPlanung'])
    # get the machine
    machine = row['Anlage']
    # loop over produktionsplanung
    for Tag in ProduktionsPlanung:
        # add to df_occupation at date of Tag[0] and column of machine the value of Tag[1]
        df_occupation.loc[df_occupation['date'] == Tag[0], machine] += Tag[1]
    # save df_occupation
    df_occupation.to_csv(data_path + "occupation.csv", index=False)
    # delete row from data
    df_data.drop(index, inplace=True)
    # save data
    df_data.to_csv(data_path+str(reset_kw)+"_"+str(reset_year)+'_orders.csv', index=False)
    # destroy table
    destroy_table(root)
    # create table
    create_table(root)

def create_table(root):
    global frame
    global previous
    global next
    global entry
    global reset
    global padx
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
    categories = ['Datum', 'Auftrag', 'Kunde', 'Liefertermin', 'Anlage', 'Fräsen[h]', 'Prog[h]', 'Extern[h]','Löschen']
    for i in range(len(categories)):
        label = tk.Label(frame, text=categories[i],font=("Helvetica", text_size))
        label.grid(row=0, column=i,padx=padx)

    # draw a line between categories and data
    separator = tk.Canvas(frame, width=1500, height=2, bg="black")
    separator.grid(row=1, column=0, columnspan=9)

    # read data from csv
    if os.path.isfile(data_path+str(target_kw)+"_"+str(target_year)+'_orders.csv'):
        df_data = pd.read_csv(data_path+str(target_kw)+"_"+str(target_year)+'_orders.csv')

        # conversion category
        conversion_categories = order_categories
        # Iterate through data rows using iterrows()
        for index, row in df_data.iterrows():
            # create a label for each data entry in row
            for i in range(len(row)):
                # get position to the corresponding category
                position = conversion_categories.index(df_data.columns[i])
                # create label for each entry
                if(1<= position <= 8):
                    label = tk.Label(frame, text=row[i],font=("Helvetica", list_size))
                    label.grid(row=index+2, column=position-1,padx=padx)
            # create a button to delete the row
            delete = tk.Button(frame, text="X", command=partial(delete_row,entry,root,index,df_data),font=("Helvetica", list_size))
            # place the button
            delete.grid(row=index+2, column=8,padx=padx)

    # place frame under top buttons
    frame.place(relx=0, rely=0.1)

    # update the root to fix entry widget bug (not showing up)
    root.update_idletasks()

def destroy_table(root):
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
        destroy_table(root)
