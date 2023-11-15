from FrontEnd import GUI
from BackEnd import SQL_handler

"""Main function for the application."""
if __name__ == '__main__':
    SQL_handler.init_sqllite_database()
    GUI.start_gui()
