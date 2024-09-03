import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from connection import connection_db
from passlib.context import CryptContext
import menu
import os
import sys
from app_utils import check_db
import globals

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


check_db()

def login_cancel():
    textbox_login_name.delete("0","end")
    textbox_password.delete("0","end")
    textbox_login_name.focus()

def login_login():
    connection = connection_db()
    cursor = connection.cursor()
    login = textbox_login_name.get().strip()
    password = textbox_password.get().strip()

    cursor.execute("SELECT login_name, password, role FROM ITmanager_users WHERE login_name=?", (login,))
    existing_user = cursor.fetchone()


    if existing_user and pwd_context.verify(password, existing_user[1]) and existing_user[2] != "admin":
        root.destroy()
        os.execl(sys.executable, sys.executable, "menu.py", "true")
    else:
        messagebox.showerror("Chybné přihlášení", "Zadali jste špatné přihlašovací jméno nebo heslo. \nOpakujte akci.")


# Main Window
root = ctk.CTk(fg_color="#2b2b2b")
root.title("ITmanager - Přihlášení")
root.resizable(width=False, height=False)

window_width = 500
windows_height = 250
screen_width = root.winfo_screenwidth()
screen_heigth = root.winfo_screenheight()

center_x = int(screen_width/2 - window_width/2)
center_y = int(screen_heigth/2 - windows_height/2)

root.geometry(f"{window_width}x{windows_height}+{center_x}+{center_y}")

# Header
label_header = ctk.CTkLabel(root, text="Přihlášení do systému ITmanager", fg_color="#2b2b2b", text_color="#85abff")
label_header.configure(font=("Arial", 16, "bold"))
label_header.grid(row=0, column=0, columnspan=2, pady=(30, 10), padx=(50, 0))


# FRAME - login
frame_login = ctk.CTkFrame(root, fg_color="#2b2b2b")
frame_login.grid(row=1, column=0, columnspan=2, pady=(20, 0), padx=(70, 20))


# LABEL, TEXTBOX login name
label_login_name = ctk.CTkLabel(frame_login, text="Přihlašovací jméno")
label_login_name.configure(font=("Arial", 12, "bold"))
label_login_name.grid(row=0, column=0, padx=0, pady=10)

textbox_login_name = ctk.CTkEntry(frame_login, width=150)
textbox_login_name.configure(font=("Arial", 12))
textbox_login_name.grid(row=1, column=0, padx=0, pady=0)


# LABEL, TEXTBOX password
label_password = ctk.CTkLabel(frame_login, text="Přístupové heslo")
label_password.configure(font=("Arial", 12, "bold"))
label_password.grid(row=0, column=1, pady=10, padx=(45,0))

textbox_password = ctk.CTkEntry(frame_login, show="*", width=150)
textbox_password.configure(font=("Arial", 12))
textbox_password.grid(row=1, column=1, pady=0, padx=(50,0))


# BUTTON
button_cancel = ctk.CTkButton(frame_login, text="Smazat", width=10, command=login_cancel)
button_cancel.configure(font=("Arial", 12, "bold"))
button_cancel.grid(row=2, column=1, pady=(25,0), padx=(10,0))

button_login = ctk.CTkButton(frame_login, text="Přihlásit", width=10, command=login_login)
button_login.configure(font=("Arial", 12, "bold"))
button_login.grid(row=2, column=1, pady=(25,0), padx=(140,0))


root.mainloop()

