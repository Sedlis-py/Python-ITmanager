import tkinter
import customtkinter as ctk
from connection import connection_db
from tkinter import messagebox, ttk
import pandas as pd
from cryptography.fernet import Fernet
import os
import globals
from passlib.context import CryptContext
import sys

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Others_rights_frame(ctk.CTkFrame):
    def __init__(self, parent, show_frame_callback):
        super().__init__(parent)
        self.show_frame_callback = show_frame_callback
        self.sort_reverse = False
        self.cipher_suite = self.get_cipher_suite()

        #messagebox.showinfo("key", self.cipher_suite)

    # 1. varianta získat itmanager_key z proměnné z Windows
    #def get_cipher_suite(self):
        #key = os.getenv('itmanager_key')
        #if not key:
        #    raise ValueError("Environment variable itmanager_key not set")
        #return Fernet(key)

    # 2. varianta získat itmanager_key ze složky "Data" soubor "itmanager_key", jedná se pouze o testování, itmanager_key by neměl být ve složce "Data", ale
    # buď jako proměnná systému, ale nejlépe na flash disku jako hardware klíč. Musela by se udělat úprava skriptu "others_rights.py"
    def get_cipher_suite(self):
        key_path = os.path.join("Data", "itmanager_key.key")
        with open(key_path, "rb") as key_file:
            key = key_file.read()

        if not key:
            raise ValueError("Environment variable itmanager_key not set")
        return Fernet(key)

    def encrypt_data(self, data):
        """Zašifruje zadaná data."""
        try:
            return self.cipher_suite.encrypt(data.encode()).decode()
        except Exception as e:
            raise RuntimeError(f"Chyba při šifrování dat: {e}")

    def decrypt_data(self, encrypted_data):
        """Dešifruje zadaná data."""
        try:
            return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            raise RuntimeError(f"Chyba při dešifrování dat: {e}")
            sys.exit()

    def show_login_and_frame(self):
        self.login_screen()

    def login_screen(self):
        if globals.login_screen_open:
            globals.login_screen.destroy()
        globals.login_screen_open = True

        globals.login_screen = ctk.CTkToplevel(fg_color="#242222")
        globals.login_screen.title("Ověření přístupu")
        globals.login_screen.resizable(width=False, height=False)
        globals.login_screen_open = True

        globals.login_screen.protocol("WM_DELETE_WINDOW", self.on_closing)

        window_width = 500
        windows_height = 160
        screen_width = globals.login_screen.winfo_screenwidth()
        screen_heigth = globals.login_screen.winfo_screenheight()

        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_heigth / 2 - windows_height / 2)

        globals.login_screen.geometry(f"{window_width}x{windows_height}+{center_x}+{center_y}")


        # FRAME - login
        frame_login = ctk.CTkFrame(globals.login_screen, fg_color="#2b2b2b")
        frame_login.grid(row=0, column=0, columnspan=2, sticky="nsew")

        globals.login_screen.grid_rowconfigure(0, weight=1)
        globals.login_screen.grid_columnconfigure(0, weight=1)

        # LABEL, TEXTBOX login name
        label_login_name = ctk.CTkLabel(frame_login, text="Přihlašovací jméno")
        label_login_name.configure(font=("Arial", 12, "bold"))
        label_login_name.grid(row=0, column=0, pady=(25,0), padx=(65,0))

        self.textbox_login_name = ctk.CTkEntry(frame_login, width=150)
        self.textbox_login_name.configure(font=("Arial", 12))
        self.textbox_login_name.grid(row=1, column=0, pady=(10,0), padx=(65,0))

        # LABEL, TEXTBOX password
        label_password = ctk.CTkLabel(frame_login, text="Přístupové heslo")
        label_password.configure(font=("Arial", 12, "bold"))
        label_password.grid(row=0, column=1, pady=(25,0), padx=(70,0))

        self.textbox_password = ctk.CTkEntry(frame_login, show="*", width=150)
        self.textbox_password.configure(font=("Arial", 12))
        self.textbox_password.grid(row=1, column=1, pady=(10,0), padx=(70,0))

        # BUTTON
        self.button_cancel = ctk.CTkButton(frame_login, text="Smazat", width=10, command=self.clear_login)
        self.button_cancel.configure(font=("Arial", 12, "bold"))
        self.button_cancel.grid(row=2, column=1, pady=(20, 0), padx=(20, 0))

        button_login = ctk.CTkButton(frame_login, text="Přihlásit", width=10, command=self.approve_login)
        button_login.configure(font=("Arial", 12, "bold"))
        button_login.grid(row=2, column=1, pady=(20, 0), padx=(160, 0))

    def on_closing(self):
        globals.login_screen_open = False
        globals.login_screen.destroy()
        self.show_frame_callback("Menu_frame")

    def clear_login(self):
        self.textbox_login_name.delete(0, "end")
        self.textbox_password.delete(0,"end")
        self.button_cancel.focus()

    def approve_login(self):
        connection = connection_db()
        cursor = connection.cursor()
        login = self.textbox_login_name.get().strip()
        password = self.textbox_password.get().strip()

        cursor.execute("SELECT login_name, password, role FROM ITmanager_users WHERE login_name=?", (login,))
        existing_user = cursor.fetchone()


        if existing_user and pwd_context.verify(password, existing_user[1]) and existing_user[2] == "admin":
            globals.login_screen.destroy()
            self.access_table_show()
        else:
            messagebox.showerror("Chybné přihlášení", "Přihlašovací jméno nebo heslo je chybné.")
            self.on_closing()

    def find_access(self):
        messagebox.showinfo("Vyhledat přístup", "Bohoužel tato funkce není dostupná.")

    def configure_treeview_style(self):
        style = ttk.Style()
        style.theme_use("classic")
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), anchor="center", background="#92ff75")
        style.configure("Treeview", rowheight=30, font=("Arial", 10))
        style.configure("Treeview", background="#333232", fieldbackground="#333232", foreground="white")
        style.map("Treeview", background=[("selected", "#347083")], foreground=[("selected", "white")])
        style.map("Treeview.Heading", background=[("active", "#63cc47")], foreground=[("active", "black")])
        style.configure("Vertical.TScrollbar", background="#4A4A4A", troughcolor="#333333", bordercolor="#333333", arrowcolor="#FFFFFF", relief="flat")

    def reset_row_colors(self):
        for row in self.tree.get_children():
            self.tree.item(row, tags=())
        self.tree.tag_configure('selected', background='#4e6b47')

    def load_data(self):
        connection = connection_db()
        cursor = connection.cursor()
        df = pd.read_sql_query("SELECT * FROM ITmanager_access", connection)

        # Použít bezpečnou funkci pro dešifrování na příslušné sloupce
        try:
            df["access_password"] = df["access_password"].apply(self.decrypt_data)
            df["access_pin"] = df["access_pin"].apply(self.decrypt_data)
        except Exception as e:
            messagebox.showerror("Chyba při dešifrování", f"Chyba při dešifrování: {e}")

        self.df = df
        cursor.close()
        connection.close()

    def access_table_show(self):
        # FRAME
        frame_buttons = ctk.CTkFrame(self, fg_color="#333232")
        frame_buttons.grid(row=0, column=0, columnspan=6, pady=(20, 0), padx=(20, 20), sticky="ew")

        # BUTTON
        button_other_rights_add = ctk.CTkButton(frame_buttons, text="Vložit nový přístup", width=10, command=self.access_add_event)
        button_other_rights_add.configure(font=("Arial", 12, "bold"))
        button_other_rights_add.grid(row=0, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        button_other_rights_find = ctk.CTkButton(frame_buttons, text="Vyhledat přístup", width=10, command=self.find_access)
        button_other_rights_find.configure(font=("Arial", 12, "bold"))
        button_other_rights_find.grid(row=0, column=1, pady=(0, 0), padx=(10, 0), sticky="w")

        frame_buttons.grid_columnconfigure(2, weight=1)
        frame_buttons.grid_columnconfigure(3, weight=1)
        frame_buttons.grid_columnconfigure(4, weight=1)

        label_description = ctk.CTkLabel(frame_buttons, text="Přehled přístupů")
        label_description.configure(font=("Arial", 24, "bold"))
        label_description.grid(row=1, column=0, columnspan=5, pady=(40, 25), padx=(0, 0), sticky="ew")

        self.tree = ttk.Treeview(self, columns=(
        "access_device_service", "access_ip_www", "access_login", "access_password", "access_pin", "access_info1",
        "access_info2"), show='headings', height=25)
        self.tree.heading("access_device_service", text="Zařízení / Služba", command=lambda: self.sort_column("access_device_service", False))
        self.tree.heading("access_ip_www", text="IP adresa / www odkaz", command=lambda: self.sort_column("access_ip_www", False))
        self.tree.heading("access_login", text="Login", command=lambda: self.sort_column("access_login", False))
        self.tree.heading("access_password", text="Heslo", command=lambda: self.sort_column("access_password", False))
        self.tree.heading("access_pin", text="Pin", command=lambda: self.sort_column("access_pin", False))
        self.tree.heading("access_info1", text="Informace 1", command=lambda: self.sort_column("access_info1", False))
        self.tree.heading("access_info2", text="Informace 2", command=lambda: self.sort_column("access_info2", False))

        self.tree.column("access_device_service", width=300, anchor="center")
        self.tree.column("access_ip_www", width=300, anchor="center")
        self.tree.column("access_login", width=150, anchor="center")
        self.tree.column("access_password", width=150, anchor="center")
        self.tree.column("access_pin", width=150, anchor="center")
        self.tree.column("access_info1", width=200, anchor="center")
        self.tree.column("access_info2", width=200, anchor="center")

        for column in self.tree["columns"]:
            self.tree.column(column, anchor="center")

        self.tree.grid(row=1, column=0, columnspan=5, pady=(0, 0), padx=(20, 0), sticky="nsew")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=5, sticky="ns")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(5, weight=0)  # For the scrollbar

        # Bind to resize event
        self.tree.bind("<Configure>", lambda e: self.adjust_column_widths())

        self.load_data()
        self.show_page()
        self.lock_columns()

    def adjust_column_widths(self):
        total_width = self.tree.winfo_width()
        num_columns = len(self.tree["columns"])
        column_width = total_width // num_columns
        for column in self.tree["columns"]:
            self.tree.column(column, width=column_width)

    def reset_row_colors(self):
        for row in self.tree.get_children():
            self.tree.item(row, tags=())
        self.tree.tag_configure('selected', background='#4e6b47')

    def show_page(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for index, row in self.df.iterrows():
            self.tree.insert("", "end", text=row["access_id"], values=(row["access_device_service"], row["access_ip_www"], row["access_login"],
                                                row["access_password"], row["access_pin"], row["access_info1"],
                                                row["access_info2"]))

    def lock_columns(self):
        # Uzamčení sloupců, aby nebylo možné měnit jejich šířku
        for col in self.tree["columns"]:
            self.tree.column(col, stretch=False, minwidth=self.tree.column(col, option='width'))

        # Bind událostí, aby se zabránilo změně šířky sloupců
        self.tree.bind('<Button-1>', self.handle_click)

    def toggle_sort(self, col_name):
        self.sort_reverse = not self.sort_reverse
        self.sort_column(col_name, self.sort_reverse)

    def handle_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "separator":
            return "break"
        elif region == "heading":
            col_id = self.tree.identify_column(event.x)
            if col_id:
                col_name = self.tree.column(col_id)["id"]
                self.toggle_sort(col_name)
            return "break"
        elif region == "cell":
            self.on_row_click(event)
        return "break"

    def on_row_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.reset_row_colors()
            self.tree.item(item_id, tags=('selected',))
            record_id = self.tree.item(item_id, "text")
            item_data = self.tree.item(item_id, "values")
            self.access_edit_event(record_id)

    def sort_column(self, col, reverse):
        if col not in self.df.columns:
            print(f"Sloupec {col} není v datovém rámci.")
            return

        # Příprava sloupce pro třídění
        self.df = self.df.sort_values(by=col, ascending=not reverse)

        self.show_page()
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def on_detail_window_close(self, window):
        self.reset_row_colors()
        window.destroy()

    def access_add_event(self):
        if globals.access_event_open:
            globals.access_event.destroy()

        globals.access_event = ctk.CTkToplevel(fg_color="#242222")
        globals.access_event.title("Informace o novém přístupu")
        globals.access_event.resizable(width=False, height=False)
        globals.access_event_open = True

        window_width = 440
        windows_height = 550
        screen_width = globals.access_event.winfo_screenwidth()
        screen_heigth = globals.access_event.winfo_screenheight()

        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_heigth / 2 - windows_height / 2)

        globals.access_event.geometry(f"{window_width}x{windows_height}+{center_x}+{center_y}")


        def access_message_success(title, message):
            response = messagebox.showinfo(title, message)

        def access_message_error(title, message):
            response = messagebox.showerror(title, message)
            globals.access_event.lift()

        def cancel_form():
            textbox_access_device_service.delete(0, "end")
            textbox_access_ip_www.delete(0, "end")
            textbox_access_login.delete(0, "end")
            textbox_access_password.delete(0, "end")
            textbox_access_pin.delete(0, "end")
            textbox_access_information1.delete(0, "end")
            textbox_access_information2.delete(0, "end")
            button_access_cancel.focus_set()

        def hardware_refresh_table():
            frame_labels_db = ctk.CTkFrame(self, fg_color="#242222")
            frame_labels_db.pack(pady=(0, 0), padx=(100, 0), anchor="w")

            connection = connection_db()
            df = pd.read_sql_query("SELECT * FROM ITmanager_hardware WHERE hardware_type='Tiskárna'", connection)
            self.hardware_show_data(df)

        def access_add():
            connection = connection_db()
            cursor = connection.cursor()

            if (textbox_access_device_service.get().strip() != "" and textbox_access_ip_www.get().strip() != "" and textbox_access_login.get().strip() != "" and
                textbox_access_password.get().strip() != "" and textbox_access_pin.get().strip() != "" and textbox_access_information1.get().strip() and
                textbox_access_information2.get().strip() != ""):

                device_service = textbox_access_device_service.get().strip()
                ip_www = textbox_access_ip_www.get().strip()
                login = textbox_access_login.get().strip()
                password = textbox_access_password.get().strip()
                encrypted_password = self.encrypt_data(password)
                pin = textbox_access_pin.get().strip()
                encrypted_pin = self.encrypt_data(pin)
                info1 = textbox_access_information1.get().strip()
                info2 = textbox_access_information2.get().strip()

                cursor.execute("""
                            INSERT INTO ITmanager_access (access_device_service, access_ip_www, access_login, access_password, access_pin, access_info1, access_info2)
                            Values(?,?,?,?,?,?,?)""", (device_service, ip_www, login, encrypted_password, encrypted_pin, info1, info2))
                connection.commit()
                cursor.close()
                connection.close()

                self.reset_row_colors()
                self.load_data()
                self.access_table_show()
                self.sort_column("access_device_service", False)
                globals.access_event.destroy()
                access_message_success("Info", "Nové zařízení bylo přidáno.")
            else:
                access_message_error("Chyba!", "Nejsou vyplněna správně všechna pole. \nProsím zkontrolujte formulář.")


        # Main header
        label_header = ctk.CTkLabel(globals.access_event, text="Informace o novém přístupu")
        label_header.configure(font=("Arial", 14, "bold"))
        label_header.pack(pady=(25, 0), padx=(0, 0))


        # Settings for device and service
        frame_access_device_service = ctk.CTkFrame(globals.access_event,  fg_color="#242222")
        frame_access_device_service.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_access_device_service = ctk.CTkLabel(frame_access_device_service, text="Zařízení / Služba")
        label_access_device_service.configure(font=("Arial", 13, "bold"))
        label_access_device_service.grid(row=0, column=0, pady=(0,0), padx=(0,0), sticky="w")

        textbox_access_device_service = ctk.CTkEntry(frame_access_device_service, width=200)
        textbox_access_device_service.grid(row=0, column=1, pady=(0,0), padx=(70,0), sticky="w")


        # Settings for ip and www
        frame_access_ip_www = ctk.CTkFrame(globals.access_event, fg_color="#242222")
        frame_access_ip_www.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_access_ip_www = ctk.CTkLabel(frame_access_ip_www, text="IP adresa / www odkaz")
        label_access_ip_www.configure(font=("Arial", 13, "bold"))
        label_access_ip_www.grid(row=2, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_access_ip_www = ctk.CTkEntry(frame_access_ip_www, width=200)
        textbox_access_ip_www.grid(row=2, column=1, pady=(0, 0), padx=(30, 0), sticky="w")


        # Settings for login
        frame_access_login = ctk.CTkFrame(globals.access_event, fg_color="#242222")
        frame_access_login.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_access_login = ctk.CTkLabel(frame_access_login, text="Login")
        label_access_login.configure(font=("Arial", 13, "bold"))
        label_access_login.grid(row=3, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_access_login = ctk.CTkEntry(frame_access_login, width=200)
        textbox_access_login.grid(row=3, column=1, pady=(0, 0), padx=(140, 0), sticky="w")


        # Settings for password
        frame_access_password = ctk.CTkFrame(globals.access_event, fg_color="#242222")
        frame_access_password.pack(pady=(30, 0), padx=(35, 0), anchor="w")

        label_access_password = ctk.CTkLabel(frame_access_password, text="Password")
        label_access_password.configure(font=("Arial", 13, "bold"))
        label_access_password.grid(row=4, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_access_password = ctk.CTkEntry(frame_access_password, width=200)
        textbox_access_password.grid(row=4, column=1, pady=(0, 0), padx=(115, 0), sticky="w")


        # Settings for pin
        frame_access_pin = ctk.CTkFrame(globals.access_event, fg_color="#242222")
        frame_access_pin.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_access_pin = ctk.CTkLabel(frame_access_pin, text="PIN")
        label_access_pin.configure(font=("Arial", 13, "bold"))
        label_access_pin.grid(row=5, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_access_pin = ctk.CTkEntry(frame_access_pin, width=200)
        textbox_access_pin.grid(row=5, column=1, pady=(0, 0), padx=(155, 0), sticky="w")


        # Settings for information 1
        frame_access_information1 = ctk.CTkFrame(globals.access_event, fg_color="#242222")
        frame_access_information1.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_access_information1 = ctk.CTkLabel(frame_access_information1, text="Informace I")
        label_access_information1.configure(font=("Arial", 13, "bold"))
        label_access_information1.grid(row=6, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_access_information1 = ctk.CTkEntry(frame_access_information1, width=200)
        textbox_access_information1.grid(row=6, column=1, pady=(0, 0), padx=(105, 0), sticky="w")


        # Settings for information 2
        frame_access_information2 = ctk.CTkFrame(globals.access_event, fg_color="#242222")
        frame_access_information2.pack(pady=(30, 0), padx=(35, 0), anchor="w")

        label_access_information2 = ctk.CTkLabel(frame_access_information2, text="Informace II")
        label_access_information2.configure(font=("Arial", 13, "bold"))
        label_access_information2.grid(row=6, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_access_information2 = ctk.CTkEntry(frame_access_information2, width=200)
        textbox_access_information2.grid(row=6, column=1, pady=(0, 0), padx=(100, 0), sticky="w")


        # Setting for buttons
        frame_access_buttons = ctk.CTkFrame(globals.access_event, fg_color="#242222")
        frame_access_buttons.pack(pady=(15, 0), padx=(45, 0), anchor="w")

        button_access_cancel = ctk.CTkButton(frame_access_buttons, text="Storno", width=10, command=cancel_form)
        button_access_cancel.configure(font=("Arial", 14, "bold"))
        button_access_cancel.grid(row=7, column=0, pady=(15, 0), padx=(242, 0))

        button_access_add = ctk.CTkButton(frame_access_buttons, text="Uložit", width=10, command=access_add)
        button_access_add.configure(font=("Arial", 14, "bold"))
        button_access_add.grid(row=7, column=1, pady=(15, 0), padx=(10, 0))


    def access_edit_event(self, index):
        if globals.access_event_open:
            globals.access_event.destroy()

        globals.access_event = ctk.CTkToplevel(fg_color="#242222")
        globals.access_event.title("Informace o přístupu")
        globals.access_event.resizable(width=False, height=False)
        globals.access_event_open = True

        globals.access_event.protocol("WM_DELETE_WINDOW", lambda: self.on_detail_window_close(globals.access_event))

        window_width = 440
        windows_height = 550
        screen_width = globals.access_event.winfo_screenwidth()
        screen_heigth = globals.access_event.winfo_screenheight()

        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_heigth / 2 - windows_height / 2)

        globals.access_event.geometry(f"{window_width}x{windows_height}+{center_x}+{center_y}")

        connection = connection_db()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM ITmanager_access WHERE access_id=?", (index,))
        access_info = cursor.fetchone()


        def access_message_success(title, message):
            response = messagebox.showinfo(title, message)

        def access_message_error(title, message):
            response = messagebox.showerror(title, message)
            globals.access_event.lift()

        def cancel_form():
            textbox_access_device_service.delete(0, "end")
            textbox_access_device_service.insert(0, access_info[1])
            textbox_access_ip_www.delete(0, "end")
            textbox_access_ip_www.insert(0, access_info[2])
            textbox_access_login.delete(0, "end")
            textbox_access_login.insert(0, access_info[3])
            textbox_access_password.delete(0, "end")
            password = self.decrypt_data(access_info[4])
            textbox_access_password.insert(0, password)
            textbox_access_pin.delete(0, "end")
            pin = self.decrypt_data(access_info[5])
            textbox_access_pin.insert(0, pin)
            textbox_access_information1.delete(0, "end")
            textbox_access_information1.insert(0, access_info[6])
            textbox_access_information2.delete(0, "end")
            textbox_access_information2.insert(0, access_info[7])
            button_access_cancel.focus_set()

        def hardware_refresh_table():
            frame_labels_db = ctk.CTkFrame(self, fg_color="#242222")
            frame_labels_db.pack(pady=(0, 0), padx=(100, 0), anchor="w")

            connection = connection_db()
            df = pd.read_sql_query("SELECT * FROM ITmanager_hardware WHERE hardware_type='Tiskárna'", connection)
            self.hardware_show_data(df)

        def access_edit():
            connection = connection_db()
            cursor = connection.cursor()

            if (textbox_access_device_service.get().strip() != "" and textbox_access_ip_www.get().strip() != "" and textbox_access_login.get().strip() != "" and
                textbox_access_password.get().strip() != "" and textbox_access_pin.get().strip() != "" and textbox_access_information1.get().strip() and
                textbox_access_information2.get().strip() != ""):

                device_service = textbox_access_device_service.get().strip()
                ip_www = textbox_access_ip_www.get().strip()
                login = textbox_access_login.get().strip()
                password = textbox_access_password.get().strip()
                encrypted_password = self.encrypt_data(password)
                pin = textbox_access_pin.get().strip()
                encrypted_pin = self.encrypt_data(pin)
                info1 = textbox_access_information1.get().strip()
                info2 = textbox_access_information2.get().strip()

                cursor.execute("""
                            UPDATE ITmanager_access
                            SET access_device_service = ?, access_ip_www = ?, access_login = ?, access_password = ?, access_pin = ?, access_info1 = ?,
                            access_info2 = ? WHERE access_id = ?""", (device_service, ip_www, login, encrypted_password, encrypted_pin, info1, info2, index))
                connection.commit()
                cursor.close()
                connection.close()

                self.reset_row_colors()
                self.load_data()
                self.access_table_show()
                self.sort_column("access_device_service", False)
                globals.access_event.destroy()
                access_message_success("Info", "Nové zařízení bylo přidáno.")
            else:
                access_message_error("Chyba!", "Nejsou vyplněna správně všechna pole. \nProsím zkontrolujte formulář.")

        def access_delete():
            device_service = access_info[1]
            ip_www = access_info[2]
            login = access_info[3]
            password = self.decrypt_data(access_info[4])
            pin = self.decrypt_data(access_info[5])
            info1 = access_info[6]
            info2 = access_info[7]

            response = messagebox.askyesno("Odstranit záznam", f"Opravdu chcete odstranit přístup ze seznamu?\n\nZařízení / služba: {device_service} \nIp adresa / www odkaz: {ip_www} \nLogin: {login} \nPassword: {password} \nPin: {pin} \nInformace 1: {info1} \nInformace 2: {info2}")

            if response:
                cursor.execute("DELETE FROM ITmanager_access WHERE access_id=?", (index,))
                connection.commit()
                cursor.close()
                connection.close()
                self.load_data()
                self.show_page()
                messagebox.showinfo("Odstranit záznam", "Záznam byl smazán.")
            else:
                globals.access_event.destroy()
                self.reset_row_colors()

        def close_form():
            self.reset_row_colors()
            globals.access_event.destroy()

        # Main header
        label_header = ctk.CTkLabel(globals.access_event, text="Informace o přístupu")
        label_header.configure(font=("Arial", 14, "bold"))
        label_header.pack(pady=(25, 0), padx=(0, 0))


        # Settings for device and service
        frame_access_device_service = ctk.CTkFrame(globals.access_event,  fg_color="#242222")
        frame_access_device_service.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_access_device_service = ctk.CTkLabel(frame_access_device_service, text="Zařízení / Služba")
        label_access_device_service.configure(font=("Arial", 13, "bold"))
        label_access_device_service.grid(row=0, column=0, pady=(0,0), padx=(0,0), sticky="w")

        textbox_access_device_service = ctk.CTkEntry(frame_access_device_service, width=200)
        textbox_access_device_service.insert(0, access_info[1])
        textbox_access_device_service.grid(row=0, column=1, pady=(0,0), padx=(70,0), sticky="w")


        # Settings for ip and www
        frame_access_ip_www = ctk.CTkFrame(globals.access_event, fg_color="#242222")
        frame_access_ip_www.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_access_ip_www = ctk.CTkLabel(frame_access_ip_www, text="IP adresa / www odkaz")
        label_access_ip_www.configure(font=("Arial", 13, "bold"))
        label_access_ip_www.grid(row=2, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_access_ip_www = ctk.CTkEntry(frame_access_ip_www, width=200)
        textbox_access_ip_www.insert(0, access_info[2])
        textbox_access_ip_www.grid(row=2, column=1, pady=(0, 0), padx=(30, 0), sticky="w")


        # Settings for login
        frame_access_login = ctk.CTkFrame(globals.access_event, fg_color="#242222")
        frame_access_login.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_access_login = ctk.CTkLabel(frame_access_login, text="Login")
        label_access_login.configure(font=("Arial", 13, "bold"))
        label_access_login.grid(row=3, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_access_login = ctk.CTkEntry(frame_access_login, width=200)
        textbox_access_login.insert(0, access_info[3])
        textbox_access_login.grid(row=3, column=1, pady=(0, 0), padx=(140, 0), sticky="w")


        # Settings for password
        frame_access_password = ctk.CTkFrame(globals.access_event, fg_color="#242222")
        frame_access_password.pack(pady=(30, 0), padx=(35, 0), anchor="w")

        label_access_password = ctk.CTkLabel(frame_access_password, text="Password")
        label_access_password.configure(font=("Arial", 13, "bold"))
        label_access_password.grid(row=4, column=0, pady=(0, 0), padx=(0, 0), sticky="w")


        password = self.decrypt_data(access_info[4])
        textbox_access_password = ctk.CTkEntry(frame_access_password, width=200)
        textbox_access_password.insert(0, password)
        textbox_access_password.grid(row=4, column=1, pady=(0, 0), padx=(115, 0), sticky="w")


        # Settings for pin
        frame_access_pin = ctk.CTkFrame(globals.access_event, fg_color="#242222")
        frame_access_pin.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_access_pin = ctk.CTkLabel(frame_access_pin, text="PIN")
        label_access_pin.configure(font=("Arial", 13, "bold"))
        label_access_pin.grid(row=5, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        pin = self.decrypt_data(access_info[5])
        textbox_access_pin = ctk.CTkEntry(frame_access_pin, width=200)
        textbox_access_pin.insert(0, pin)
        textbox_access_pin.grid(row=5, column=1, pady=(0, 0), padx=(155, 0), sticky="w")


        # Settings for information 1
        frame_access_information1 = ctk.CTkFrame(globals.access_event, fg_color="#242222")
        frame_access_information1.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_access_information1 = ctk.CTkLabel(frame_access_information1, text="Informace I")
        label_access_information1.configure(font=("Arial", 13, "bold"))
        label_access_information1.grid(row=6, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_access_information1 = ctk.CTkEntry(frame_access_information1, width=200)
        textbox_access_information1.insert(0, access_info[6])
        textbox_access_information1.grid(row=6, column=1, pady=(0, 0), padx=(105, 0), sticky="w")


        # Settings for information 2
        frame_access_information2 = ctk.CTkFrame(globals.access_event, fg_color="#242222")
        frame_access_information2.pack(pady=(30, 0), padx=(35, 0), anchor="w")

        label_access_information2 = ctk.CTkLabel(frame_access_information2, text="Informace II")
        label_access_information2.configure(font=("Arial", 13, "bold"))
        label_access_information2.grid(row=6, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_access_information2 = ctk.CTkEntry(frame_access_information2, width=200)
        textbox_access_information2.insert(0, access_info[7])
        textbox_access_information2.grid(row=6, column=1, pady=(0, 0), padx=(100, 0), sticky="w")


        # Setting for buttons
        frame_access_buttons = ctk.CTkFrame(globals.access_event, fg_color="#242222")
        frame_access_buttons.pack(pady=(15, 0), padx=(45, 0), anchor="w")

        button_access_cancel = ctk.CTkButton(frame_access_buttons, text="Vrátit zpět", width=10, command=cancel_form)
        button_access_cancel.configure(font=("Arial", 14, "bold"))
        button_access_cancel.grid(row=7, column=0, pady=(15, 0), padx=(53, 0))

        button_access_add = ctk.CTkButton(frame_access_buttons, text="Upravit", width=10, command=access_edit)
        button_access_add.configure(font=("Arial", 14, "bold"))
        button_access_add.grid(row=7, column=1, pady=(15, 0), padx=(10, 0))

        button_access_delete = ctk.CTkButton(frame_access_buttons, text="Odstranit", width=10, command=access_delete)
        button_access_delete.configure(font=("Arial", 14, "bold"))
        button_access_delete.grid(row=7, column=2, pady=(15, 0), padx=(10, 0))

        button_access_close = ctk.CTkButton(frame_access_buttons, text="Zavřít", width=10, command=close_form)
        button_access_close.configure(font=("Arial", 14, "bold"))
        button_access_close.grid(row=7, column=3, pady=(15, 0), padx=(10, 0))




