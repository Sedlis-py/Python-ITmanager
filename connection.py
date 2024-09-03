import sqlite3
from tkinter import messagebox
import os
import sys

def connection_db():
    db_path = os.path.join("Data", "ITmanager.db")

    if not os.path.exists(db_path):
        messagebox.showerror("Chyba databáze", "Databáze nebyla nalezena. Program nemůže pokračovat.")
        sys.exit()

    try:
        connection = sqlite3.connect("Data/ITmanager.db")
        return connection
    except sqlite3.Error as e:
        print(f"Chyba při připojování k databázi: {e}")
        return None
