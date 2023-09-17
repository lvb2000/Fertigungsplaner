import os
import tkinter as tk
import datetime
import calendar
from functools import partial
import pandas as pd
from General import data_path, planner_size, arbeitsTag, order_categories
import copy

df_new = None

hours_left_label = None
Laufzeit = None

weiter_button = None
save_button = None
autofill_button = None
frame = None
machine_label = None

machine = None

time_entries = []
available_time_labels = []
current_entries = []

padx=10
pady=10
def add_missing_days(df_occupation, Produktionsstart, Liefertermin):
    # get number of possibles days for production inclusive production start and exclusive delivery date
    max_days = (datetime.datetime.strptime(Liefertermin, '%d.%m.%Y') - datetime.datetime.strptime(Produktionsstart, '%d.%m.%Y')).days
    periode = []
    # loop over number of days
    for i in range(max_days):
        # get the date of the day plus i
        date = datetime.datetime.strptime(Produktionsstart, '%d.%m.%Y')
        date = date + datetime.timedelta(days=i)
        date = date.strftime('%d.%m.%Y')
        # append day to periode
        periode.append(date)
        # check if the date is in df_occupation
        if (date not in df_occupation['date'].values):
            # insert the day in df at the right index and fill the value for machine and human with 8
            # check if the day is a sunday
            if (calendar.day_name[datetime.datetime.strptime(date, '%d.%m.%Y').weekday()] == "Sunday"):
                df_occupation.loc[len(df_occupation)] = [date, 0,0,0,0]
            else:
                df_occupation.loc[len(df_occupation)] = [date, arbeitsTag,arbeitsTag,arbeitsTag,arbeitsTag]
    return periode

def destroy_planner(root):
    global frame
    global autofill_button
    global save_button
    global weiter_button
    global machine_label
    if(frame != None):
        frame.destroy()
    if(autofill_button != None):
        autofill_button.destroy()
    if(save_button != None):
        save_button.destroy()
    if(weiter_button != None):
        weiter_button.destroy()
    if(machine_label != None):
        machine_label.destroy()

def weiter_data(root,df_occupation,data):
    global current_entries
    global df_new
    global machine
    global Laufzeit
    Produktionsplanung = []
    for index,entry in enumerate(current_entries):
            # get the date of the day plus i
            date = datetime.datetime.strptime(data[1], '%d.%m.%Y')
            date = date + datetime.timedelta(days=index)
            date = date.strftime('%d.%m.%Y')
            Produktionsplanung.append([date,entry,1])
    # append Produktionsplanung to df_new
    df_new.loc[0, 'ProduktionsPlanung'+machine] = str(Produktionsplanung)
    # update machine
    if(machine == "Mazak"):
        machine = "Haas"
    elif(machine == "Haas"):
        machine = "DMG_Mori"
    # reset Laufzeit
    Laufzeit = None
    # open Planner Handler
    Planner_Handler(root, df_occupation, data)

def save_data(root,df_occupation,data):
    global current_entries
    global df_new
    Produktionsplanung = []
    for index,entry in enumerate(current_entries):
            # get the date of the day plus i
            date = datetime.datetime.strptime(data[1], '%d.%m.%Y')
            date = date + datetime.timedelta(days=index)
            date = date.strftime('%d.%m.%Y')
            Produktionsplanung.append([date,entry,1])
    # append Produktionsplanung to df_new
    df_new.loc[0, 'ProduktionsPlanung'+machine] = str(Produktionsplanung)
    # get all kw between data[1] and data[4]
    kw = []
    # get the start date
    start_date = datetime.datetime.strptime(data[1], '%d.%m.%Y')
    # get the end date
    end_date = datetime.datetime.strptime(data[4], '%d.%m.%Y')
    # loop over all days
    for i in range((end_date - start_date).days + 1):
        # get the date of the day plus i
        date = start_date + datetime.timedelta(days=i)
        # get the kw of the date
        kw.append(date.strftime("%V"))
    # get the unique kw
    kw = list(set(kw))
    # get the year of the order
    year = datetime.datetime.strptime(data[1], '%d.%m.%Y').year
    # for each kw read the csv file, append the new df and save it
    for week in kw:
        # check if csv exists
        if os.path.isfile(data_path + str(week) + "_" + str(year) + '_orders.csv'):
            # read csv file
            df = pd.read_csv(data_path + str(week) + "_" + str(year) + '_orders.csv')
        else:
            # create a new dataframe
            df = pd.DataFrame(columns=order_categories)
        # append df_new to df
        df = pd.concat([df, df_new], ignore_index=True)
        # save df
        df.to_csv(data_path + str(week) + "_" + str(year) + '_orders.csv', index=False)
    # safe df_occupation in a csv file
    df_occupation.to_csv(data_path + "occupation.csv", index=False)
    # destroy all Planer widgets
    destroy_planner(root)
    return

def reset_widget(df_occupation,index,date):
    global Laufzeit
    global time_entries
    global available_time_labels
    global current_entries
    # get current value
    current_value = current_entries[index]
    # add old value to Laufzeit
    Laufzeit += current_value
    # add old value on corresponding day and machine to data frame
    df_occupation.loc[df_occupation['date'] == date, machine] += current_value


def on_enter_pressed(root,df_occupation,index,date,data,event):
    global hours_left_label
    global Laufzeit
    global save_button

    global time_entries
    global available_time_labels
    global current_entries

    # get user input
    user_input = float(time_entries[index].get())
    # reset widges
    reset_widget(df_occupation,index,date)
    # limit user input to Laufzeit
    if (user_input > Laufzeit):
        user_input = Laufzeit
    # update occupation
    df_occupation.loc[df_occupation['date'] == date, machine] -= user_input
    # Get text from an input field or any other source
    # update current entry
    current_entries[index] = user_input
    # update the available time label
    available_time = df_occupation.loc[df_occupation['date'] == date, machine].iloc[0]
    available_time_labels[index].config(text=str(available_time)+" [h]")
    # update Laufzeit
    Laufzeit -= user_input
    # Update the text of the label
    if hours_left_label != None:
        hours_left_label.config(text="Noch " + str(Laufzeit) + " Stunden übrig.")
    # check if save is possible
    if (Laufzeit <= 0):
        Planner_Handler(root, df_occupation, data)


def reset_all_widgets(df_occupation,periode):
    global time_entries
    global available_time_labels
    global current_entries
    # reset all days
    for i,date in enumerate(periode):
        # get old value
        current_value = current_entries[i]
        # add old value on corresponding day and machine to data frame
        df_occupation.loc[df_occupation['date'] == date, machine] += current_value
        # clear entry
        time_entries[i].delete(0, tk.END)
        # update the available time label
        available_time = df_occupation.loc[df_occupation['date'] == date, machine].iloc[0]
        available_time_labels[i].config(text=str(available_time)+" [h]")
        # reset current entry
        current_entries[i] = 0
def autofill(root,df_occupation,data,periode,index):
    global hours_left_label
    global Laufzeit
    global save_button

    global time_entries
    global available_time_labels
    global current_entries

    # reset
    reset_all_widgets(df_occupation,periode)
    Laufzeit = float(copy.copy(data[index]))
    # set all days
    for i,date in enumerate(periode):
        # get the available time for the machine
        available_time = df_occupation.loc[df_occupation['date'] == date, machine].iloc[0]
        # get the entry and the available time label
        entry = time_entries[i]
        available_time_label = available_time_labels[i]
        # only update until Laufzeit is 0
        update_value = min(available_time,Laufzeit)
        if(update_value <= 0):
            update_value = 0
        # update occupation Data Frame
        df_occupation.loc[df_occupation['date'] == date, machine] -= update_value
        # update current entry
        current_entries[i] = update_value
        # update the entry
        entry.insert(0, str(update_value))
        # update the available time label
        available_time = df_occupation.loc[df_occupation['date'] == date, machine].iloc[0]
        available_time_label.config(text=str(available_time)+" [h]")
        # update the laufzeit
        Laufzeit -= update_value
        if (Laufzeit <= 0):
            Planner_Handler(root,df_occupation, data)
            break
    # Update the text of the label
    if hours_left_label != None:
        hours_left_label.config(text="Noch " + str(Laufzeit) + " Stunden übrig.")

def reset_arrays():
    global time_entries
    global available_time_labels
    global current_entries
    time_entries = []
    available_time_labels = []
    current_entries = []

def get_occupation():
    # get occupation statistics
    df = pd.DataFrame(columns=['date','Mazak','Haas','DMG_Mori','Marcus'])
    if os.path.isfile(data_path+"occupation.csv"):
        df = pd.read_csv(data_path + "occupation.csv")
    return df
def Planner(root,df_occupation,data,data_index):
    global hours_left_label
    global Laufzeit
    global autofill_button
    global frame
    global machine

    global time_entries
    global available_time_labels
    global current_entries

    # Laufzeit
    Laufzeit = float(copy.copy(data[data_index]))
    # reset all arrays
    reset_arrays()
    # built tkinter widgets
    frame = tk.Frame(root)
    # Hours left frame
    hours_left_frame = tk.Frame(frame)
    # make a label for the hours left
    hours_left_label = tk.Label(hours_left_frame, text="Noch " + str(data[data_index]) + " Stunden übrig.", font=("Helvetica", int(planner_size*1.5)))
    hours_left_label.pack()
    # make frame for the grid
    grid_frame = tk.Frame(frame)

    # add missing days
    periode = add_missing_days(df_occupation, data[1], data[4])
    # loop over number of days
    for i,date in enumerate(periode):
        # get the available time for the machine
        available_time = df_occupation.loc[df_occupation['date'] == date, machine].iloc[0]
        # get a lable for the weekday
        weekday_label = tk.Label(grid_frame, text=calendar.day_name[datetime.datetime.strptime(date, '%d.%m.%Y').weekday()], font=("Helvetica", planner_size))
        # get a lable for the date
        date_label = tk.Label(grid_frame, text=date, font=("Helvetica", planner_size))
        # get a lable for the available time
        available_time_label = tk.Label(grid_frame, text=str(available_time)+" [h]", font=("Helvetica", planner_size))
        # get a entry for inputing time
        time_entry = tk.Entry(grid_frame, width=3, font=("Helvetica", planner_size))
        # Bind the Enter key (Return) to the function
        time_entry.bind('<Return>', partial(on_enter_pressed,root,df_occupation,i,date,data))
        # place all tkinter widgets
        offset = 5
        weekday_label.grid(row=int(i%8), column=int(i/8)*offset, padx=padx, pady=pady)
        date_label.grid(row=int(i%8), column=int(i/8)*offset+1, padx=padx, pady=pady)
        available_time_label.grid(row=int(i%8), column=int(i/8)*offset+2, padx=padx, pady=pady)
        time_entry.grid(row=int(i%8), column=int(i/8)*offset+3, padx=padx, pady=pady)

        # save widgets in global arrays
        available_time_labels.append(available_time_label)
        time_entries.append(time_entry)
        current_entries.append(0)

    # pack frames
    hours_left_frame.pack(side=tk.TOP)
    grid_frame.pack(side=tk.BOTTOM)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    # add button to autofill the planner
    autofill_button = tk.Button(root, text="Autom. Füllen", command=partial(autofill,root,df_occupation,data,periode,data_index), font=("Helvetica", planner_size))
    autofill_button.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

def Planner_Handler(root,df_occupation, data):
    global machine
    global save_button
    global weiter_button
    global Laufzeit
    global machine_label
    if(machine == "Mazak" and Laufzeit==None):
        index = 5
        # create Label for the machine
        machine_label = tk.Label(root, text="Mazak", font=("Helvetica", 28))
        machine_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        # convert data array to only need entries for the planner
        Planner(root,df_occupation, data, index)
    if(machine == "Haas" and Laufzeit==None):
        index = 6
        destroy_planner(root)
        # create Label for the machine
        machine_label = tk.Label(root, text="Haas", font=("Helvetica", 28))
        machine_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        Planner(root, df_occupation, data, index)
    if(machine == "DMG_Mori" and Laufzeit==None):
        index = 7
        destroy_planner(root)
        # create Label for the machine
        machine_label = tk.Label(root, text="DMG_Mori", font=("Helvetica", 28))
        machine_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        Planner(root, df_occupation, data, index)

    if((machine == "Mazak" or machine=="Haas") and Laufzeit <= 0):
        # create weiter button
        weiter_button = tk.Button(root, text="Weiter", command=partial(weiter_data,root, df_occupation, data),
                                  font=("Helvetica", planner_size))
        weiter_button.place(relx=0.8, rely=0.9, anchor=tk.CENTER)
    else:
        if(weiter_button != None):
            weiter_button.destroy()
    if (machine == "DMG_Mori" and Laufzeit <= 0):
        # create save button
        save_button = tk.Button(root, text="Speichern", command=partial(save_data, root,df_occupation,  data),
                                  font=("Helvetica", planner_size))
        save_button.place(relx=0.8, rely=0.9, anchor=tk.CENTER)
    else:
        if (save_button != None):
            save_button.destroy()


def main(root, data):
    global machine
    global df_new
    machine = "Mazak"
    # set fixed values in df_new
    # create a new datafram with the new values
    df_new = pd.DataFrame([[data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7],data[8],data[9],None,None,None,0,"","","","",""]],
                          columns=order_categories)
    # get occupation statistics
    df_occupation = get_occupation()
    # built Planner
    Planner_Handler(root, df_occupation, data)