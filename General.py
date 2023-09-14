import pandas as pd
""" General Parameters for the whole Project"""

# Mac Data path: /Users/lukas/Dokumente/Fertigungsplaner/Data/
# Markus windowes Data Path: G:/Meine Ablage/CnC_Metzger/FuckExcel/Data/
data_path = "/Users/lukas/Dokumente/Fertigungsplaner/Data/"

# Text sizes
text_size = 20
list_size = 14
planner_size = 16

# Length of general working day in hours
arbeitsTag = 8

# error list
errors = ["machine overload","human overload","impossible delivery date","entries_missing","Fertigungsstart unvalid","Lieferdatum unvalid"]

# orders catergories
# Status: 0 = Order unfinished; 1 = Order finished
order_categories = ['Kalenderwoche', 'Datum', 'Auftragsnummer', 'Kunde', 'Liefertermin', 'Anlage',
                    'Bearbeitungsdauer', 'BearbeitungsdauerProg', 'Fremdbearbeitungsdauer',
                    'ProduktionsPlanung','Status','Placeholder1','Placeholder2','Placeholder3','Placeholder4','Placeholder5']

def acceptable_error(error):
    # check if in error array there is either none or errors[0] or errors[1]
    if(error == None):
        return True
    for err in error:
        if(err!=errors[0] and err!=errors[1]):
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
