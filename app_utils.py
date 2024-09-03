import sqlite3
import sys
import os
from tkinter import messagebox
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import globals


def restart_application(root):
    root.destroy()  # Zavře hlavní okno
    python = sys.executable
    script_path = os.path.join(os.path.dirname(__file__), "__init__.py")
    os.execl(python, python, script_path, *sys.argv)  # Restart skriptu

def check_db():
    db_path = os.path.join("Data","ITmanager.db")

    if not os.path.exists(db_path):
        if messagebox.askyesno("První spuštění aplikace", "Nenašel jsem databázi dat, jedná se o první spustění aplikace?"):
            if messagebox.askyesno("Inicializace aplikace", "Mám provést základni inicializaci aplikace?\n\nVytvořím: \n   - novou databázi dat \n   - účet administátora \n   - účet superadmina pro přístupy a jeho bezpečnostní klíč"):
                create_empty_db()
                create_user()
                create_special_key()
                create_superadmin()
                messagebox.showinfo("První inicializace aplikace", "Inicializace aplikace proběhla v pořádku, nyní se můžete přihlásit")
            else:
                messagebox.showwarning("Inicializace aplikace", "Inicializace byla přerušena uživatelem.")
                sys.exit()
        else:
            messagebox.showwarning("Chyba databáze", "Proveď kontrolu databáze.")
            sys.exit()

def create_empty_db():
    db_path = os.path.join("Data", "ITmanager.db")

    create_tables_sql = """
        CREATE TABLE ITmanager_hardware (
            hardware_id INTEGER,
            hardware_ip TEXT (50),
            hardware_type TEXT (50),
            hardware_mark TEXT (50),
            hardware_place TEXT (100),
            hardware_name TEXT (100),
            hardware_link TEXT (250),
            hardware_info TEXT (250),
            PRIMARY KEY (
                hardware_id AUTOINCREMENT
            )
        );
        
        
        CREATE TABLE ITmanager_users (
            id_user    INTEGER,
            login_name VARCHAR (125) UNIQUE,
            password   VARCHAR (125),
            role       TEXT (50),
        PRIMARY KEY (
            id_user AUTOINCREMENT
        )
        );

        
        
        CREATE TABLE ITmanager_access (
            access_id             INTEGER    PRIMARY KEY AUTOINCREMENT,
            access_device_service TEXT (150),
            access_ip_www         TEXT (250),
            access_login          TEXT (150),
            access_password       TEXT (250),
            access_pin            TEXT (250),
            access_info1          TEXT (250),
            access_info2          TEXT (250) 
        );

        
        CREATE TABLE ITmanager_printer_materials (
            printer_material_id INTEGER PRIMARY KEY AUTOINCREMENT,
            printer_material_printer_id INTEGER REFERENCES ITmanager_hardware (hardware_id),
            printer_material_name TEXT (100),
            printer_material_price INTEGER,
            printer_material_info TEXT (250) 
        );


        CREATE TABLE ITmanager_printer_events (
            printer_event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            printer_event_printer_id INTEGER REFERENCES ITmanager_hardware (hardware_id),
            printer_event_type TEXT (250),
            printer_event_material_name TEXT (250),
            printer_event_other TEXT (250),
            printer_event_price TEXT,
            printer_event_date TEXT (100) 
        );
    """

    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.executescript(create_tables_sql)

        connection.commit()
        connection.close()

    except sqlite3.Error as e:
        messagebox.showerror("Chyba při vytváření databáze.", f"Došlo k chybě při vytváření databáze: \n\n{e}")
        sys.exit()

def create_user():
    db_path = os.path.join("Data", "ITmanager.db")

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    login = "test"
    hashed_password = pwd_context.hash("test")
    role = "user"

    # Uložení uživatelského jména a hashovaného hesla do databáze
    cursor.execute("INSERT INTO ITmanager_users (login_name, password, role) VALUES (?, ?, ?)", (login, hashed_password, role))
    connection.commit()

    # Uzavření připojení
    cursor.close()
    connection.close()

def create_special_key():
    key_path = os.path.join("Data", "itmanager_key.key")
    key = Fernet.generate_key()

    with open(key_path, "wb") as key_file:
        key_file.write(key)

def create_superadmin():
    db_path = os.path.join("Data", "ITmanager.db")

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    login = "superadmin"
    hashed_password = pwd_context.hash("superadmin")
    role = "admin"

    # Uložení uživatelského jména a hashovaného hesla do databáze
    cursor.execute("INSERT INTO ITmanager_users (login_name, password, role) VALUES (?, ?, ?)", (login, hashed_password, role))
    connection.commit()

    # Uzavření připojení
    cursor.close()
    connection.close()

def is_log_in():
    if not globals.is_login_in:
        messagebox.showerror("Chyba v přihlášení", "Nejste přihlášen, nejdříve se musíte přihlásit.")
        sys.exit()