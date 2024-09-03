import tkinter
import customtkinter as ctk
from connection import connection_db
from tkinter import messagebox, ttk, filedialog
import shutil
import os
import sys
from app_utils import restart_application
class Settings_frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.settings()

    def settings(self):
        # FRAME Settings
        frame_settings = ctk.CTkFrame(self, fg_color="#333232")
        frame_settings.grid(row=0, column=0, columnspan=6, pady=(50, 0), padx=(50, 20), sticky="ew")

        label_settings = ctk.CTkLabel(frame_settings, text="Nastavení systému")
        label_settings.configure(font=("Arial", 22, "bold"))
        label_settings.grid(row=0, column=0, pady=(0,0) ,padx=(0,0), sticky="w")


        canvas = ctk.CTkCanvas(self, width=1600, height=1, bg="#333232", highlightthickness=0)
        canvas.grid(row=1, column=0, pady=(20, 0), padx=(45, 20), sticky="w")
        canvas.create_line(0, 0, 1600, 0, fill="#5e5e5e", width=1)


        # FRAME Database settings
        frame_settings_database = ctk.CTkFrame(self, fg_color="#333232")
        frame_settings_database.grid(row=2, column=0, pady=(40, 0), padx=(80, 20), sticky="ew")

        label_settings_database = ctk.CTkLabel(frame_settings_database, text="Nastavení databáze")
        label_settings_database.configure(font=("Arial", 18, "bold"))
        label_settings_database.grid(row=0, column=0, pady=(0,0), padx=(0,0), sticky="w")

        label_settings_database_export = ctk.CTkLabel(frame_settings_database, text="Exportovat databáze IT manager")
        label_settings_database_export.configure(font=("Arial", 14, "bold"))
        label_settings_database_export.grid(row=1, column=0, pady=(50,0), padx=(20,0), sticky= "w")

        button_settings_database_export = ctk.CTkButton(frame_settings_database, text="Export", command=self.database_export)
        button_settings_database_export.grid(row=1, column=1, pady=(50,0), padx=(90,0), sticky= "e")

        label_settings_database_import = ctk.CTkLabel(frame_settings_database, text="Importovat databáze IT manager")
        label_settings_database_import.configure(font=("Arial", 14, "bold"))
        label_settings_database_import.grid(row=2, column=0, pady=(50, 0), padx=(20, 0), sticky= "w")

        button_settings_database_import = ctk.CTkButton(frame_settings_database, text="Import", command=self.database_import)
        button_settings_database_import.grid(row=2, column=1, pady=(50, 0), padx=(90, 0), sticky= "e")

        canvas = ctk.CTkCanvas(self, width=1600, height=1, bg="#333232", highlightthickness=0)
        canvas.grid(row=3, column=0, pady=(70, 0), padx=(45, 20), sticky="w")
        canvas.create_line(0, 0, 1600, 0, fill="#5e5e5e", width=1)


    def database_export(self):
        source_db = os.path.join("Data", "ITmanager.db")

        default_backup_name = "ITmanager.db"

        destination_path = filedialog.asksaveasfilename(
            initialfile=default_backup_name,
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )

        if destination_path:
            try:
                shutil.copy(source_db, destination_path)
                messagebox.showinfo("Export databáze", f"Export databáze do \n\n{destination_path}\n\n proběhla v pořádku.")
            except Exception as e:
                messagebox.showerror("Export databáze", f"Došlo k chybě při exportu databáze: \n\n{e}")

    def database_import(self):
        target_db = os.path.join("Data", "ITmanager.db")

        source_path = filedialog.askopenfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )

        if source_path:
            try:
                connection = connection_db()
                if connection:
                    connection.close()
                shutil.copy(source_path, target_db)
                messagebox.showinfo("Import databáze", f"Import databáze do \n\n{source_path}\n\n proběhla v pořádku.")
                messagebox.showinfo("Restart aplikace", "Nyní bude proveden restart aplikace.")
                restart_application(self.parent)
            except Exception as e:
                messagebox.showerror("Import databáze", f"Došlo k chybě při importu databáze: \n\n{e}")
