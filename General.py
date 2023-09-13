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
errors = ["machine overload","human overload","impossible delivery date"]

# orders catergories
# Status: 0 = Order unfinished; 1 = Order finished
order_categories = ['Kalenderwoche', 'Datum', 'Auftragsnummer', 'Kunde', 'Liefertermin', 'Anlage',
                    'Bearbeitungsdauer', 'BearbeitungsdauerProg', 'Fremdbearbeitungsdauer',
                    'ProduktionsPlanung','Status','Placeholder1','Placeholder2','Placeholder3','Placeholder4','Placeholder5']

def acceptable_error(error):
    # check if in error array there is either none or errors[0] or errors[1]
    if(error == None):
        return True
    if(errors[0] in error):
        return True
    if(errors[1] in error):
        return True
    return False
