import os
import datetime
import calendar
import pandas as pd
from General import data_path, errors, arbeitsTag

def check_machine_overload(df_occupation,date, Liefertermin,Anlage,Bearbeitungsdauer):
    # get maximum days to work on the order
    max_days = (datetime.datetime.strptime(Liefertermin, '%d.%m.%Y') - datetime.datetime.strptime(date, '%d.%m.%Y')).days
    availableHours = 0
    # counter for the number of days
    i = 0
    # loop over number of days
    while(availableHours < int(Bearbeitungsdauer)):
        if(i >= max_days):
            return True
        # get the date of the day plus i
        date = datetime.datetime.strptime(date, '%d.%m.%Y')
        date = date + datetime.timedelta(days=i)
        date = date.strftime('%d.%m.%Y')
        # check if the date is in df_occupation
        if (date in df_occupation['date'].values):
            # get value of machine column at the index of the date
            occupation = df_occupation.loc[df_occupation['date'] == date, Anlage].iloc[0]
            if (occupation < 0):
                occupation = 0
            availableHours += occupation
        else:
            # insert the day in df at the right index and fill the value for machine and human with 8
            # check if the day is a sunday
            if (calendar.day_name[datetime.datetime.strptime(date, '%d.%m.%Y').weekday()] == "Sunday"):
                df_occupation.loc[len(df_occupation)] = [date, 0,0,0, 0]
            else:
                df_occupation.loc[len(df_occupation)] = [date, arbeitsTag,arbeitsTag,arbeitsTag, arbeitsTag]
                availableHours += 8
        i += 1
    return False

def check_entry_missing(data):
    # check if any entry is missing
    for entry in data:
        if(entry == ""):
            return True
    return False

def check_delivery_date(data):
    # check if the delivery date is in the past
    if(datetime.datetime.strptime(data[4], '%d.%m.%Y') < datetime.datetime.strptime(data[1], '%d.%m.%Y')):
        return True
    return False

def check_Fertigungsstart(data):
    # check if Fertigungsstart is a valid date in format dd.mm.yyyy
    try:
        datetime.datetime.strptime(data[1], '%d.%m.%Y')
        return False
    except ValueError:
        return True

def check_Liefertermin(data):
    # check if Liefertermin is a valid date in format dd.mm.yyyy
    try:
        datetime.datetime.strptime(data[4], '%d.%m.%Y')
        return False
    except ValueError:
        return True
def main(error_kind, data):
    result = False
    df_occupation = pd.DataFrame(columns=['date','Mazak','Haas','DMG Mori','Marcus'])
    if os.path.isfile(data_path+"occupation.csv"):
        df_occupation = pd.read_csv(data_path + "occupation.csv")
    if (check_Liefertermin(data)):
        # append error to error_kind
        error_kind.append(errors[5])
        result = True
    elif (check_Fertigungsstart(data)):
        # append error to error_kind
        error_kind.append(errors[4])
        result = True
    elif (check_delivery_date(data)):
        # append error to error_kind
        error_kind.append(errors[2])
        result = True
    elif(check_entry_missing(data)):
        # append error to error_kind
        error_kind.append(errors[3])
        result = True
    else:
        if(check_machine_overload(df_occupation,data[1], data[4],"Mazak",data[6])):
            # append error to error_kind
            error_kind.append(errors[0])
            result = True
        if(check_machine_overload(df_occupation,data[1], data[4],"Haas",data[7])):
            # append error to error_kind
            error_kind.append(errors[1])
            result = True
        if(check_machine_overload(df_occupation,data[1], data[4],"DMG Mori",data[8])):
            # append error to error_kind
            error_kind.append(errors[2])
            result = True

    return result