import sqlite3 as sq
import pandas as pd

def init_sqllite_database():
    # Connect to the database (this will create the file if it doesn't exist)
    conn = sq.connect('production_planner.db')

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Create a table to store tasks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auftrag(
            id INTEGER PRIMARY KEY,
            start_date DATE,
            due_date DATE,
            order_number_intern CHARACTER VARYING(50),
            order_number_extern CHARACTER VARYING(50),
            customer CHARACTER VARYING(50),
            mazak_duration REAL,
            haas_duration REAL,
            dmg_duration REAL,
            status INTEGER DEFAULT 0
        )
    ''')
    # Create a table to store schedule for each machine
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule_mazak(
            id INTEGER PRIMARY KEY,
            order_id INTEGER,
            working_date DATE,
            start_time TIME,
            end_time TIME,
            total_duration REAL,
            FOREIGN KEY (order_id) REFERENCES auftrag (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule_haas(
            id INTEGER PRIMARY KEY,
            order_id INTEGER,
            working_date DATE,
            start_time TIME,
            end_time TIME,
            total_duration REAL,
            FOREIGN KEY (order_id) REFERENCES auftrag (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule_dmg(
            id INTEGER PRIMARY KEY,
            order_id INTEGER,
            working_date DATE,
            start_time TIME,
            end_time TIME,
            total_duration REAL,
            FOREIGN KEY (order_id) REFERENCES auftrag (id)
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def add_auftrag_to_database(auftrag):
    # Connect to the database (this will create the file if it doesn't exist)
    with sq.connect('production_planner.db') as conn:
        # Create a cursor object
        cursor = conn.cursor()
        # Insert a row of data
        try:
            data = (auftrag.produktionsstart, auftrag.liefertermin, auftrag.auftragsnummer,
                    auftrag.produktionsnummer, auftrag.kunde, auftrag.mazak, auftrag.haas, auftrag.dmg,
                    auftrag.status)
            cursor.execute("INSERT INTO auftrag (id,start_date,due_date,order_number_intern,"
                           "order_number_extern,customer,mazak_duration,haas_duration,dmg_duration,"
                           "status)"
                           "VALUES (NULL,?,?,?,?,?,?,?,?,?)",
                           data)
            # add the assigned id to the auftrag object
            auftrag.sqllite_id = cursor.lastrowid
        except sq.IntegrityError:
            print("Diesen Auftrag gibt es schon.")
        # Save (commit) the changes
        conn.commit()
        # Close the connection
        conn.close()

def remove_auftrag_from_database(auftrag):
    # Connect to the database (this will create the file if it doesn't exist)
    with sq.connect('production_planner.db') as conn:
        # Create a cursor object
        cursor = conn.cursor()
        # Insert a row of data
        try:
            cursor.execute("DELETE FROM auftrag WHERE id = ?", (auftrag.sqllite_id,))
        except sq.IntegrityError:
            print("Diesen Auftrag gibt es nicht.")
        # Save (commit) the changes
        conn.commit()
        # Close the connection
        conn.close()

def update_existing_auftrag(auftrag):
    # Connect to the database (this will create the file if it doesn't exist)
    with sq.connect('production_planner.db') as conn:
        # Create a cursor object
        cursor = conn.cursor()
        # Insert a row of data
        try:
            data = (auftrag.produktionsstart, auftrag.liefertermin, auftrag.auftragsnummer,
                    auftrag.produktionsnummer, auftrag.kunde, auftrag.mazak, auftrag.haas, auftrag.dmg,
                    auftrag.status, auftrag.sqllite_id)
            cursor.execute("UPDATE auftrag SET start_date = ?, due_date = ?, order_number_intern = ?,"
                           "order_number_extern = ?, customer = ?, mazak_duration = ?, haas_duration = ?,"
                           "dmg_duration = ?, status = ? WHERE id = ?",
                           data)
        except sq.IntegrityError:
            print("Diesen Auftrag gibt es nicht.")
        # Save (commit) the changes
        conn.commit()
        # Close the connection
        conn.close()
