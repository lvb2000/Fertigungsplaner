import os
import datetime
import calendar
import pandas as pd
from General import data_path, errors, arbeitsTag

def check_machine_overload(df_occupation,date, Liefertermin, Anlage,Bearbeitungsdauer):
    # get maximum days to work on the order
    max_days = (datetime.datetime.strptime(Liefertermin, '%d.%m.%Y') - datetime.datetime.strptime(date, '%d.%m.%Y')).days
    availableHours = 0
    # counter for the number of days
    i = 0
    # loop over number of days
    while(availableHours < int(Bearbeitungsdauer)):
        if(i > max_days):
            return True
        # get the date of the day plus i
        date = datetime.datetime.strptime(date, '%d.%m.%Y')
        date = date + datetime.timedelta(days=i)
        date = date.strftime('%d.%m.%Y')
        # check if the date is in df_occupation
        if (date in df_occupation['date'].values):
            # get value of machine column at the index of the date
            availableHours += df_occupation.loc[df_occupation['date'] == date, Anlage].iloc[0]
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

def check_human_overload(df_occupation,date, Liefertermin, BearbeitungsdauerProg):
    return False
def main(error_kind, data):
    result = False
    df_occupation = pd.DataFrame(columns=['date','Mazak','Haas','DMG Mori','Marcus'])
    if os.path.isfile(data_path+"occupation.csv"):
        df_occupation = pd.read_csv(data_path + "occupation.csv")
    if(check_machine_overload(df_occupation,data[1], data[4],data[5],data[6]) or
    check_human_overload(df_occupation,data[1], data[4], data[7])):
        # append error to error_kind
        error_kind.append(errors[0])
        result = True

    return result