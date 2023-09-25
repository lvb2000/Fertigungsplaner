import pandas as pd
import datetime
""" General Parameters for the whole Project"""

# Mac Data path: /Users/lukas/Dokumente/Fertigungsplaner/Data/
# Markus windowes Data Path: G:/Meine Ablage/CnC_Metzger/FuckExcel/Data/
data_path = "/Users/lukas/Dokumente/Fertigungsplaner/Data/"

# Text sizes
text_size = 20
list_size = 14
planner_size = 16

# Length of general working day in hours
arbeitsTag = 8.0

# error list
errors = ["mazak overload","haas overload","DMG overload","human overload","impossible delivery date","entries_missing","Fertigungsstart unvalid","Lieferdatum unvalid"]

# orders catergories
# Status: 0 = Order unfinished; 1 = Order finished
order_categories = ['Kalenderwoche', 'Datum', 'Auftragsnummer', 'Kunde', 'Liefertermin', 'Mazak', 'Haas', 'DMG_Mori','ProgrammierDauer', 'Fremdbearbeitungsdauer',
                    'ProduktionsPlanungMazak','ProduktionsPlanungHaas','ProduktionsPlanungDMG_Mori','Status','Placeholder1','Placeholder2','Placeholder3','Placeholder4','Placeholder5']

def acceptable_error(error):
    # check if in error array there is either none or errors[0] or errors[1]
    if(error == None):
        return True
    for err in error:
        if(err!=errors[0] and err!=errors[1] and err!=errors[2] and err!=errors[3]):
            return False
    return True

def date1_before_date2(date1,date2):
    # reformat date1 from dd.mm.yyyy to yymmdd
    date1 = date1[6:10]+date1[3:5]+date1[0:2]
    # reformat date2 from dd.mm.yyyy to yymmdd
    date2 = date2[6:10]+date2[3:5]+date2[0:2]
    # check if date1 is before date2
    if(int(date1) < int(date2)):
        return True
    else:
        return False

def get_weeks(start,end):
    kw = []
    # get the start date
    start_date = datetime.datetime.strptime(start, '%d.%m.%Y')
    # get the end date
    end_date = datetime.datetime.strptime(end, '%d.%m.%Y')
    # loop over all days
    for i in range((end_date - start_date).days + 1):
        # get the date of the day plus i
        date = start_date + datetime.timedelta(days=i)
        # get the kw of the date
        kw.append(date.strftime("%V"))
    # get the unique kw
    return list(set(kw))
