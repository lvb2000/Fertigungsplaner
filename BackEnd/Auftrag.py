import pandas as pd
import numpy as np
import datetime
import calendar

class Auftrag:
    def __int__(self):
        self.sqllite_id = None
        self.produktionsstart = None
        self.liefertermin = None
        self.auftragsnummer = None
        self.produktionsnummer = None
        self.kunde = None
        self.mazak = None
        self.haas = None
        self.dmg = None
        self.status = None

    def __init__(self, data):
        self.kw = data[0]
        self.produktionsstart = data[1]
        self.auftragsnummer = data[2]
        self.kunde = data[3]
        self.liefertermin = data[4]
        self.mazak = data[5]
        self.haas = data[6]
        self.dmg_mori = data[7]
        self.programmierdauer = data[8]
        self.fremdbearbeitungsdauer = data[9]
        self.produktionsplanungmazak = None
        self.produktionsplanunghaas = None
        self.produktionsplanungdmg_mori = None
        self.status = 0
        self.placeholder1 = None
        self.placeholder2 = None
        self.placeholder3 = None
        self.placeholder4 = None
        self.placeholder5 = None

    def validate_auftrag(self):
        # check the kalenderweek
        if(self.__validate_kw__() == False):
            return False
        # check the Produktionsstart
        if(self.__validate_Produktionsstart__() == False):
            return False
        # check the liefertermin
        if(self.__validate_liefertermin__() == False):
            return False
        # check the mazak
        if(self.__validate_mazak__() == False):
            return False
        # check the haas
        if(self.__validate_haas__() == False):
            return False
        # check the dmg_mori
        if(self.__validate_dmg_mori__() == False):
            return False
        return True

    def __validate_kw__(self):
        # check if int between 1 and 52
        if(self.kw == ""):
            return False
        try:
            int(self.kw)
        except ValueError:
            return False
        if(int(self.kw) < 1 or int(self.kw) > 52):
            return False

    def __validate_Produktionsstart__(self):
        # check if date is valid
        if(self.produktionsstart == ""):
            return False
        try:
            datetime.datetime.strptime(self.produktionsstart, '%d.%m.%Y')
        except ValueError:
            return False

    def __validate_liefertermin__(self):
        # check if date is valid
        if(self.liefertermin == ""):
            return False
        try:
            datetime.datetime.strptime(self.liefertermin, '%d.%m.%Y')
        except ValueError:
            return False
        # check if liefertermin is before Produktionsstart
        if(datetime.datetime.strptime(self.liefertermin, '%d.%m.%Y') < datetime.datetime.strptime(self.produktionsstart, '%d.%m.%Y')):
            return False

    def __validate_mazak__(self):
        # check if hours are valid
        if(self.mazak == ""):
            return False
        try:
            float(self.mazak)
        except ValueError:
            return False
        if(float(self.mazak) < 0):
            return False
    def __validate_haas__(self):
        # check if hours are valid
        if(self.haas == ""):
            return False
        try:
            float(self.haas)
        except ValueError:
            return False
        if(float(self.haas) < 0):
            return False

    def __validate_dmg_mori__(self):
        # check if hours are valid
        if(self.dmg_mori == ""):
            return False
        try:
            float(self.dmg_mori)
        except ValueError:
            return False
        if(float(self.dmg_mori) < 0):
            return False




