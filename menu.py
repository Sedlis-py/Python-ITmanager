import sys
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from CTkMenuBar import *
from tkinter import messagebox
from connection import connection_db
from printers import Printers_frame
from printers_event import Printers_event_frame
from printers_material_frame import Printers_material_frame
from software_eset import Software_eset_frame
from software_ms_office import Software_ms_office_frame
from software_user_cal import Software_user_cal_frame
from hardware_loans import Hardware_loans_frame
from hardware_ip_addresses import Hardware_ip_addresses_frame
from hardware_end_devices_pc import Hardware_end_devices_pc_frame
from others_rights import Others_rights_frame
from settings import Settings_frame
import globals
from app_utils import is_log_in

class Menu_frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.label = ctk.CTkLabel(self, text="Vítejte v aplikaci IT manager.")
        self.label.configure(font=("",14, "bold"))
        self.label.pack(pady=350)


def main():
    args = sys.argv

    if len(args) > 1:
        if args[1] == "true":
            globals.is_login_in = True
        else:
            globals.is_login_in = False

    is_log_in()

    global material_event_open, material_event, hardware_event_open, hardware_event
    # Main Windows
    root = ctk.CTk()
    root.title("ITmanager - hlavní program")
    root.geometry("600x400")
    root._state_before_windows_set_titlebar_color = "zoomed"

    menu = CTkMenuBar(root)
    menu.configure(bg_color="#2b2b2b")
    menu_file = menu.add_cascade("Soubor")

    def app_close():
        if messagebox.askyesnocancel("Zavřít aplikaci", "Opravdu chcete zavřít aplikaci?"):
            root.destroy()

    def close_all_events():

        if globals.material_event_open and globals.material_event is not None:
            globals.material_event.destroy()
            globals.glomaterial_event_open = False
        if globals.hardware_event_open and globals.hardware_event is not None:
            globals.hardware_event.destroy()
            globals.hardware_event_open = False
        if globals.printer_event_open and globals.printer_event is not None:
            globals.printer_event.destroy()
            globals.printer_event_open = False
        if globals.login_screen_open and globals.login_screen is not None:
            globals.login_screen.destroy()
            globals.login_screen_open = False
        if globals.access_event_open and globals.access_event is not None:
            globals.access_event.destroy()
            globals.access_event_open = False


    def create_frame(name, frame_class):
        if frame_class is Others_rights_frame:
            frame = frame_class(container, show_frame)
        else:
            frame = frame_class(container)
        frames[name] = frame

    def show_frame(frame_name):
        close_all_events()

        for frame in frames.values():
            frame.destroy()

        if frame_name == "Menu_frame":
            frame = Menu_frame(container)
        elif frame_name == "Settings_frame":
            frame = Settings_frame(container)
        elif frame_name == "Hardware_ip_addresses_frame":
            frame = Hardware_ip_addresses_frame(container)
        elif frame_name == "Hardware_end_devices_pc_frame":
            frame = Hardware_end_devices_pc_frame(container)
        elif frame_name == "Hardware_loans_frame":
            frame = Hardware_loans_frame(container)
        elif frame_name == "Printers_frame":
            frame = Printers_frame(container)
        elif frame_name == "Printers_event_frame":
            frame = Printers_event_frame(container)
        elif frame_name == "Printers_material_frame":
            frame = Printers_material_frame(container)
        elif frame_name == "Software_user_cal_frame":
            frame = Software_user_cal_frame(container)
        elif frame_name == "Software_eset_frame":
            frame = Software_eset_frame(container)
        elif frame_name == "Software_ms_office_frame":
            frame = Software_ms_office_frame(container)
        elif frame_name == "Others_rights_frame":
            frame = Others_rights_frame(container, show_frame)
            frame.show_login_and_frame()

        frames[frame_name] = frame
        frame.pack(fill="both", expand=True)
        frame.tkraise()


    # Main menu
    dropdown_file = CustomDropdownMenu(widget=menu_file)
    dropdown_file.add_option(option="Nastavení", command=lambda: show_frame("Settings_frame"))
    dropdown_file.add_option(option="Ukončit", command=app_close)


    # Menu for printers
    menu_printers = menu.add_cascade("Tiskárny")
    dropdown_printers = CustomDropdownMenu(widget=menu_printers)
    dropdown_printers.add_option("Přehled tiskáren", command=lambda: show_frame("Printers_frame"))
    dropdown_printers.add_option("Přehled údalosti tiskáren", command=lambda: show_frame("Printers_event_frame"))
    dropdown_printers.add_option("Přehled cen spotřebního materiálu", command=lambda: show_frame("Printers_material_frame"))


    # Menu for software
    menu_software = menu.add_cascade("Software")
    dropdown_software = CustomDropdownMenu(widget=menu_software)
    dropdown_software.add_option("USER CAL & RDS licence", command=lambda: show_frame("Software_user_cal_frame"))
    dropdown_software.add_option("ESET licence", command=lambda: show_frame("Software_eset_frame"))
    dropdown_software.add_option("MS Office licence", command=lambda: show_frame("Software_ms_office_frame"))


    # Menu for hardware
    menu_hardware = menu.add_cascade("Hardware")
    dropdown_hardware = CustomDropdownMenu(widget=menu_hardware)
    dropdown_hardware.add_option("Zařízení - IP adresy", command=lambda: show_frame("Hardware_ip_addresses_frame"))
    dropdown_hardware.add_option("Koncová zařízení PC / NB", command=lambda: show_frame("Hardware_end_devices_pc_frame"))
    dropdown_hardware.add_option("Zápůjčky HW", command=lambda: show_frame("Hardware_loans_frame"))

    # Menu for others
    menu_others = menu.add_cascade("Ostatní")
    dropdown_others = CustomDropdownMenu(widget=menu_others)
    dropdown_others.add_option("Přístupy", command=lambda: show_frame("Others_rights_frame"))

    # Container for all frames
    container = ctk.CTkFrame(root)
    container.pack(fill="both",expand=True)

    frames = {}


    create_frame("Menu_frame", Menu_frame)
    create_frame("Settings_frame", lambda parent: Settings_frame(parent))

    create_frame("Printers_frame", Printers_frame)
    create_frame("Printers_event_frame", Printers_event_frame)
    create_frame("Printers_material_frame", Printers_material_frame)

    create_frame("Software_user_cal_frame", Software_user_cal_frame)
    create_frame("Software_eset_frame", Software_eset_frame)
    create_frame("Software_ms_office_frame", Software_ms_office_frame)

    create_frame("Hardware_ip_addresses_frame", Hardware_ip_addresses_frame)
    create_frame("Hardware_end_devices_pc_frame", Hardware_end_devices_pc_frame)
    create_frame("Hardware_loans_frame", Hardware_loans_frame)

    create_frame("Others_rights_frame", Others_rights_frame)

    show_frame("Menu_frame")

    root.mainloop()


if __name__ == "__main__":
    main()


