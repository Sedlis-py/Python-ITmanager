import tkinter
import customtkinter as ctk
from connection import connection_db
from tkinter import messagebox, ttk
import pandas as pd
from functools import partial
import ipaddress
from reportlab.pdfgen import canvas
from fpdf import FPDF
import os
from datetime import datetime
import globals

class Hardware_ip_addresses_frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="#333232")
        self.sort_reverse = False
        self.df = self.load_data()
        self.configure_treeview_style()
        self.hardware_table_show()
        self.tree.tag_configure('selected', background='#4e6b47')
        self.sort_column("hardware_ip", False)

    def find_hardware(self):
        messagebox.showinfo("Vyhledat zařízení", "Bohoužel tato funkce není dostupná.")

    def create_pdf(self):
        connection = connection_db()
        cursor = connection.cursor()
        cursor.execute("PRAGMA table_info(ITmanager_hardware)")
        columns = cursor.fetchall()

        pdf = FPDF(orientation="L", unit="pt", format="A4")
        font_path = "Data/arial.ttf"
        if not os.path.exists(font_path):
            raise RuntimeError(f"Font file '{font_path}' not found")

        pdf.add_font("Arial", "", font_path, uni=True)
        pdf.set_font("Arial", size=12)
        pdf.set_font("Arial", style="B", size=12)
        pdf.add_page()

        column_widths = [80, 65, 75, 200, 150, 225]
        columns_names = ["ID hardwaru", "IP adresa", "Typ", "Identifikace", "Místo", "Název", "Link", "Poznámka"]
        skip_columns = [0, 6]
        col_idx = 0

        for i, column in enumerate(columns):  # Startujeme od druhého sloupce
            if i not in skip_columns:
                pdf.cell(w=column_widths[col_idx], h=15, txt=columns_names[i], border=1, align='C')
                col_idx += 1

        pdf.ln()

        rows = self.df.values.tolist()

        # Zápis dat
        pdf.set_font("Arial", size=10)
        for row in rows:
            col_idx = 0
            for i, element in enumerate(row):  # Startujeme od druhého sloupce
                if not i in skip_columns:
                    pdf.cell(w=column_widths[col_idx], h=15, txt=str(element), border=1, align='C')
                    col_idx += 1
            pdf.ln()  # Přidání nového řádku po každém řádku dat

        date = datetime.now()
        date_now = date.strftime("%Y_%m_%d-%H_%M")
        pdf.output(f"./Reporty/Hardware_seznam_{date_now}.pdf")
        messagebox.showinfo("PDF soubor",f"Soubor: \n\nHardware_seznam_{date_now}.pdf\n\nbyl vygenerován. \n\nReport naleznete ve složce 'reporty'.")

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
        df = pd.read_sql_query("SELECT * FROM ITmanager_hardware", connection)
        self.df = df

    def hardware_table_show(self):
        # FRAME
        frame_buttons = ctk.CTkFrame(self, fg_color="#333232")
        frame_buttons.grid(row=0, column=0, columnspan=6, pady=(20, 0), padx=(20, 20), sticky="ew")

        # BUTTONS
        button_hardware_add = ctk.CTkButton(frame_buttons, text="Vložit nové zařízení", command=self.hardware_add_event)
        button_hardware_add.configure(font=("Arial", 12, "bold"))
        button_hardware_add.grid(row=0, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        button_hardware_find = ctk.CTkButton(frame_buttons, text="Vyhledat zařízení", command=self.find_hardware)
        button_hardware_find.configure(font=("Arial", 12, "bold"))
        button_hardware_find.grid(row=0, column=1, pady=(0, 0), padx=(10, 0), sticky="w")

        button_hardware_print = ctk.CTkButton(frame_buttons, text="Tisk seznam zařízení", command=self.create_pdf)
        button_hardware_print.configure(font=("Arial", 12, "bold"))
        button_hardware_print.grid(row=0, column=2, pady=(0, 0), padx=(10, 0), sticky="w")

        # SPACE COLUMNS
        frame_buttons.grid_columnconfigure(3, weight=1)
        frame_buttons.grid_columnconfigure(4, weight=1)
        frame_buttons.grid_columnconfigure(5, weight=1)

        label_description = ctk.CTkLabel(frame_buttons, text="Přehled Hardwaru", anchor="center")
        label_description.configure(font=("Arial", 24, "bold"))
        label_description.grid(row=1, column=0, columnspan=6, pady=(40, 25), padx=(0, 0), sticky="ew")

        # TREEVIEW
        self.tree = ttk.Treeview(self, columns=(
        "hardware_ip", "hardware_type", "hardware_mark", "hardware_place", "hardware_name", "hardware_link",
        "hardware_info"), show='headings')
        self.tree.heading("hardware_ip", text="IP adresa", command=lambda: self.sort_column("hardware_ip", False))
        self.tree.heading("hardware_type", text="Typ", command=lambda: self.sort_column("hardware_type", False))
        self.tree.heading("hardware_mark", text="Označení", command=lambda: self.sort_column("hardware_mark", False))
        self.tree.heading("hardware_place", text="Umístění", command=lambda: self.sort_column("hardware_place", False))
        self.tree.heading("hardware_name", text="Název", command=lambda: self.sort_column("hardware_name", False))
        self.tree.heading("hardware_link", text="Odkaz", command=lambda: self.sort_column("hardware_link", False))
        self.tree.heading("hardware_info", text="Poznámka", command=lambda: self.sort_column("hardware_info", False))

        # Set initial column widths
        self.tree.column("hardware_ip", width=150, anchor="center")
        self.tree.column("hardware_type", width=100, anchor="center")
        self.tree.column("hardware_mark", width=100, anchor="center")
        self.tree.column("hardware_place", width=300, anchor="center")
        self.tree.column("hardware_name", width=300, anchor="center")
        self.tree.column("hardware_link", width=300, anchor="center")
        self.tree.column("hardware_info", width=350, anchor="center")

        # Add Treeview to grid
        self.tree.grid(row=1, column=0, columnspan=5, pady=(0, 0), padx=(20, 0), sticky="nsew")

        # SCROLLBAR
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=5, sticky="ns")

        # DYNAMIC RESIZING
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(5, weight=0)  # For the scrollbar

        # Bind to resize event
        self.tree.bind("<Configure>", lambda e: self.adjust_column_widths())

        # Load Data and Show Page
        self.load_data()
        self.show_page()
        self.lock_columns()

    def adjust_column_widths(self):
        total_width = self.tree.winfo_width()
        num_columns = len(self.tree["columns"])
        column_width = total_width // num_columns
        for column in self.tree["columns"]:
            self.tree.column(column, width=column_width)

    def show_page(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for index, row in self.df.iterrows():
            self.tree.insert("", "end", text=row["hardware_id"], values=(row["hardware_ip"], row["hardware_type"], row["hardware_mark"],
                                                row["hardware_place"], row["hardware_name"], row["hardware_link"],
                                                row["hardware_info"]))


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
            self.hardware_edit_event(record_id)

    def sort_column(self, col, reverse):
        if col == "hardware_ip":
            def ip_key(val):
                if val == "-" or pd.isnull(val):
                    return (1, val)
                try:
                    return (0, ipaddress.ip_address(val))
                except ValueError:
                    return (1, val)

            self.df["ip_key"] = self.df[col].apply(ip_key)
            self.df = self.df.sort_values(by="ip_key", ascending=not reverse).drop(columns=["ip_key"])
        else:
            self.df = self.df.sort_values(by=col, ascending=not reverse)
        self.show_page()
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def on_detail_window_close(self, window):
        self.reset_row_colors()  # Reset the row colors when the detail window is closed
        window.destroy()

    def hardware_add_event(self):
        if globals.hardware_event_open:
            globals.hardware_event.destroy()

        globals.hardware_event = ctk.CTkToplevel(fg_color="#242222")
        globals.hardware_event.title("Informace o novém HARDWARU")
        globals.hardware_event.resizable(width=False, height=False)
        globals.hardware_event_open = True

        window_width = 440
        windows_height = 550
        screen_width = globals.hardware_event.winfo_screenwidth()
        screen_heigth = globals.hardware_event.winfo_screenheight()

        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_heigth / 2 - windows_height / 2)

        globals.hardware_event.geometry(f"{window_width}x{windows_height}+{center_x}+{center_y}")


        def hardware_message_success(title, message):
            response = messagebox.showinfo(title, message)

        def hardware_message_error(title, message):
            response = messagebox.showerror(title, message)
            globals.hardware_event.lift()

        def cancel_form():
            textbox_hardware_ip.delete(0, "end")
            combobox_hardware_type.set(value="-    typ zařízení  -")
            textbox_hardware_mark.delete(0, "end")
            textbox_hardware_place.delete(0, "end")
            textbox_hardware_name.delete(0, "end")
            textbox_hardware_link.delete(0, "end")
            textbox_hardware_info.delete(0, "end")
            button_hardware_cancel.focus_set()

        def hardware_refresh_table():
            frame_labels_db = ctk.CTkFrame(self, fg_color="#242222")
            frame_labels_db.pack(pady=(0, 0), padx=(100, 0), anchor="w")

            connection = connection_db()
            df = pd.read_sql_query("SELECT * FROM ITmanager_hardware", connection)
            self.hardware_show_data(df)


        def hardware_add():
            connection = connection_db()
            cursor = connection.cursor()
            ip = textbox_hardware_ip.get().strip()

            if ip != "-":
                try:
                    ipaddress.ip_address(ip)  # Pokusíme se vytvořit instanci ip_address, kontrola platnosti IP adresy
                except ValueError:
                    hardware_message_error("Špatná IP adresa", f"Zadaná IP adresa '{ip}' není platná.")
                    return

                cursor.execute("SELECT * FROM ITmanager_hardware WHERE hardware_ip=?", (ip,))
                existing_ip = cursor.fetchone()

                if existing_ip:
                    hardware_message_error("Info", "Nelze založit nové zažízení. \nZařízení s IP adresou již existuje.")
                else:
                    if (textbox_hardware_ip.get().strip() != "" and textbox_hardware_mark.get().strip() != "" and textbox_hardware_place.get().strip() != "" and
                        textbox_hardware_name.get().strip() != "" and textbox_hardware_link.get().strip() != "" and textbox_hardware_info.get().strip() and
                        combobox_hardware_type.get().strip() != "-    typ zařízení  -"):

                        ip = textbox_hardware_ip.get().strip()
                        mark = textbox_hardware_mark.get().strip()
                        place = textbox_hardware_place.get().strip()
                        name = textbox_hardware_name.get().strip()
                        link = textbox_hardware_link.get()
                        info = textbox_hardware_info.get()
                        type = combobox_hardware_type.get().strip()

                        cursor.execute("""
                            INSERT INTO ITmanager_hardware (hardware_ip, hardware_type, hardware_mark, hardware_place, hardware_name, hardware_link, hardware_info)
                            Values(?,?,?,?,?,?,?)""", (ip, type, mark, place, name, link, info))
                        connection.commit()
                        cursor.close()
                        connection.close()

                        self.reset_row_colors()
                        self.load_data()
                        self.hardware_table_show()
                        self.sort_column("hardware_ip", False)
                        globals.hardware_event.destroy()
                        hardware_message_success("Info", "Nové zařízení bylo přidáno.")
                    else:
                        hardware_message_error("Chyba!","Nejsou vyplněna správně všechna pole. \nProsím zkontrolujte formulář.")

            else:
                if (textbox_hardware_ip.get().strip() != "" and textbox_hardware_mark.get().strip() != "" and textbox_hardware_place.get().strip() != "" and
                    textbox_hardware_name.get().strip() != "" and textbox_hardware_link.get().strip() != "" and textbox_hardware_info.get().strip() and
                    combobox_hardware_type.get().strip() != "-    typ zařízení  -"):

                    ip = textbox_hardware_ip.get().strip()
                    mark = textbox_hardware_mark.get().strip()
                    place = textbox_hardware_place.get().strip()
                    name = textbox_hardware_name.get().strip()
                    link = textbox_hardware_link.get()
                    info = textbox_hardware_info.get()
                    type = combobox_hardware_type.get().strip()

                    cursor.execute("""
                        INSERT INTO ITmanager_hardware (hardware_ip, hardware_type, hardware_mark, hardware_place, hardware_name, hardware_link, hardware_info)
                        Values(?,?,?,?,?,?,?)""", (ip, type, mark, place, name, link, info))
                    connection.commit()
                    cursor.close()
                    connection.close()

                    self.reset_row_colors()
                    self.load_data()
                    self.hardware_table_show()
                    self.sort_column("hardware_ip", False)
                    globals.hardware_event.destroy()
                    hardware_message_success("Info", "Nové zařízení bylo přidáno.")
                else:
                    hardware_message_error("Chyba!", "Nejsou vyplněna správně všechna pole. \nProsím zkontrolujte formulář." )



        # Main header
        label_header = ctk.CTkLabel(globals.hardware_event, text="Informace o novém HARDWARU")
        label_header.configure(font=("Arial", 14, "bold"))
        label_header.pack(pady=(25, 0), padx=(0, 0))


        # Settings for IP adrress
        frame_hardware_ip = ctk.CTkFrame(globals.hardware_event,  fg_color="#242222")
        frame_hardware_ip.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_hardware_ip = ctk.CTkLabel(frame_hardware_ip, text="IP adresa (nebo '-')")
        label_hardware_ip.configure(font=("Arial", 13, "bold"))
        label_hardware_ip.grid(row=0, column=0, pady=(0,0), padx=(0,0), sticky="w")

        textbox_hardware_ip = ctk.CTkEntry(frame_hardware_ip, width=200)
        textbox_hardware_ip.grid(row=0, column=1, pady=(0,0), padx=(47,0), sticky="w")


        # Setting for type of hardware
        frame_hardware_type = ctk.CTkFrame(globals.hardware_event, fg_color="#242222")
        frame_hardware_type.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_hardware_type = ctk.CTkLabel(frame_hardware_type, text="Typ zařízení")
        label_hardware_type.configure(font=("Arial", 13, "bold"))
        label_hardware_type.grid(row=1, column=0, pady=(0,0), padx=(0,0), sticky="w")

        combobox_hardware_type = ctk.CTkComboBox(frame_hardware_type, values=["-    typ zařízení  -", "Ostatní", "Router", "Tiskárna",
                                                                              "Server", "PC Stanice", "Switch"], width=200, justify="center")
        combobox_hardware_type.configure(state="readonly")
        combobox_hardware_type.grid(row=1, column=2, pady=(0,0), padx=(87,0), sticky="w")


        # Settings for hardware mark
        frame_hardware_mark = ctk.CTkFrame(globals.hardware_event, fg_color="#242222")
        frame_hardware_mark.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_hardware_mark = ctk.CTkLabel(frame_hardware_mark, text="Označení hardwaru")
        label_hardware_mark.configure(font=("Arial", 13, "bold"))
        label_hardware_mark.grid(row=2, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_hardware_mark = ctk.CTkEntry(frame_hardware_mark, width=200)
        textbox_hardware_mark.grid(row=2, column=1, pady=(0, 0), padx=(40, 0), sticky="w")


        # Settings for place of hardware
        frame_hardware_place = ctk.CTkFrame(globals.hardware_event, fg_color="#242222")
        frame_hardware_place.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_hardware_place = ctk.CTkLabel(frame_hardware_place, text="Umístění hardwaru")
        label_hardware_place.configure(font=("Arial", 13, "bold"))
        label_hardware_place.grid(row=3, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_hardware_place = ctk.CTkEntry(frame_hardware_place, width=200)
        textbox_hardware_place.grid(row=3, column=1, pady=(0, 0), padx=(45, 0), sticky="w")


        # Settings for name of hardware
        frame_hardware_name = ctk.CTkFrame(globals.hardware_event, fg_color="#242222")
        frame_hardware_name.pack(pady=(30, 0), padx=(35, 0), anchor="w")

        label_hardware_name = ctk.CTkLabel(frame_hardware_name, text="Název zařízení")
        label_hardware_name.configure(font=("Arial", 13, "bold"))
        label_hardware_name.grid(row=4, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_hardware_name = ctk.CTkEntry(frame_hardware_name, width=200)
        textbox_hardware_name.grid(row=4, column=1, pady=(0, 0), padx=(70, 0), sticky="w")


        # Settings for link of hardware
        frame_hardware_link = ctk.CTkFrame(globals.hardware_event, fg_color="#242222")
        frame_hardware_link.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_hardware_link = ctk.CTkLabel(frame_hardware_link, text="Odkaz na zařízení")
        label_hardware_link.configure(font=("Arial", 13, "bold"))
        label_hardware_link.grid(row=5, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_hardware_link = ctk.CTkEntry(frame_hardware_link, width=200)
        textbox_hardware_link.grid(row=5, column=1, pady=(0, 0), padx=(50, 0), sticky="w")


        # Settings for information of hardware
        frame_hardware_info = ctk.CTkFrame(globals.hardware_event, fg_color="#242222")
        frame_hardware_info.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_hardware_info = ctk.CTkLabel(frame_hardware_info, text="Poznámka k zařízení")
        label_hardware_info.configure(font=("Arial", 13, "bold"))
        label_hardware_info.grid(row=6, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_hardware_info = ctk.CTkEntry(frame_hardware_info, width=200)
        textbox_hardware_info.grid(row=6, column=1, pady=(0, 0), padx=(32, 0), sticky="w")


        # Setting for buttons
        frame_hardware_buttons = ctk.CTkFrame(globals.hardware_event, fg_color="#242222")
        frame_hardware_buttons.pack(pady=(15, 0), padx=(35, 0), anchor="w")

        button_hardware_cancel = ctk.CTkButton(frame_hardware_buttons, text="Storno", width=10, command=cancel_form)
        button_hardware_cancel.configure(font=("Arial", 14, "bold"))
        button_hardware_cancel.grid(row=7, column=0, pady=(15, 0), padx=(242, 0))

        button_hardware_add = ctk.CTkButton(frame_hardware_buttons, text="Uložit", width=10, command=hardware_add)
        button_hardware_add.configure(font=("Arial", 14, "bold"))
        button_hardware_add.grid(row=7, column=1, pady=(15, 0), padx=(10, 0))


    def hardware_edit_event(self, index):

        if globals.hardware_event_open:
            globals.hardware_event.destroy()

        globals.hardware_event = ctk.CTkToplevel(fg_color="#242222")
        globals.hardware_event.title("Změna údajů HARDWARU")
        globals.hardware_event.resizable(width=False, height=False)
        globals.hardware_event_open = True

        globals.hardware_event.protocol("WM_DELETE_WINDOW", lambda: self.on_detail_window_close(globals.hardware_event))

        window_width = 440
        windows_height = 550
        screen_width = globals.hardware_event.winfo_screenwidth()
        screen_heigth = globals.hardware_event.winfo_screenheight()

        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_heigth / 2 - windows_height / 2)

        globals.hardware_event.geometry(f"{window_width}x{windows_height}+{center_x}+{center_y}")

        connection = connection_db()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM ITmanager_hardware WHERE hardware_id=?", (index,))
        hardware_info = cursor.fetchone()


        def hardware_message_success(title, message):
            response = messagebox.showinfo(title, message)

        def hardware_message_error(title, message):
            response = messagebox.showerror(title, message)
            globals.hardware_event.lift()

        def cancel_form():
            textbox_hardware_ip.delete(0, "end")
            textbox_hardware_ip.insert(0, hardware_info[1])
            combobox_hardware_type.set(value="-    typ zařízení  -")
            combobox_hardware_type.set(hardware_info[2])
            textbox_hardware_mark.delete(0, "end")
            textbox_hardware_mark.insert(0, hardware_info[3])
            textbox_hardware_place.delete(0, "end")
            textbox_hardware_place.insert(0, hardware_info[4])
            textbox_hardware_name.delete(0, "end")
            textbox_hardware_name.insert(0, hardware_info[5])
            textbox_hardware_link.delete(0, "end")
            textbox_hardware_link.insert(0, hardware_info[6])
            textbox_hardware_info.delete(0, "end")
            textbox_hardware_info.insert(0, hardware_info[7])
            button_hardware_cancel.focus_set()


        def hardware_edit():
            connection = connection_db()
            cursor = connection.cursor()
            id = index
            ip = textbox_hardware_ip.get().strip()

            if ip != "-":
                try:
                    ipaddress.ip_address(
                        ip)  # Pokusíme se vytvořit instanci ip_address, kontrola platnosti IP adresy
                except ValueError:
                    hardware_message_error("Špatná IP adresa", f"Zadaná IP adresa '{ip}' není platná.")
                    return

                cursor.execute("SELECT * FROM ITmanager_hardware WHERE hardware_ip=?", (ip,))
                check_hardware = cursor.fetchone()

                if check_hardware is not None and check_hardware[0] != id:
                    hardware_message_error("Upravit záznam","Bohužel nově zadaná adresa z formuláře již v seznamu existuje.")
                else:
                    if (textbox_hardware_ip.get().strip() != "" and textbox_hardware_mark.get().strip() != "" and textbox_hardware_place.get().strip() != "" and
                        textbox_hardware_name.get().strip() != "" and textbox_hardware_link.get().strip() != "" and textbox_hardware_info.get().strip() and
                        combobox_hardware_type.get().strip() != "-    typ zařízení  -"):

                        id = index
                        ip = textbox_hardware_ip.get().strip()
                        mark = textbox_hardware_mark.get().strip()
                        place = textbox_hardware_place.get().strip()
                        name = textbox_hardware_name.get().strip()
                        link = textbox_hardware_link.get()
                        info = textbox_hardware_info.get()
                        type = combobox_hardware_type.get().strip()

                        cursor.execute("""
                                            UPDATE ITmanager_hardware
                                            SET hardware_ip = ?, hardware_type = ?, hardware_mark = ?, hardware_place = ?, hardware_name = ?, hardware_link = ?, hardware_info = ?
                                            WHERE hardware_id = ?""", (ip, type, mark, place, name, link, info, id))
                        connection.commit()
                        cursor.close()
                        connection.close()
                        globals.hardware_event.destroy()
                        self.load_data()
                        self.show_page()
                        self.sort_column("hardware_ip", False)
                        hardware_message_success("Upravit záznam", "Informace o zařízení byly upraveny.")
                    else:
                        hardware_message_error("Upravit záznam","Nejsou vyplněna správně všechna pole. \nProsím zkontrolujte formulář.")
            else:
                if (textbox_hardware_ip.get().strip() != "" and textbox_hardware_mark.get().strip() != "" and textbox_hardware_place.get().strip() != "" and
                    textbox_hardware_name.get().strip() != "" and textbox_hardware_link.get().strip() != "" and textbox_hardware_info.get().strip() and
                    combobox_hardware_type.get().strip() != "-    typ zařízení  -"):

                    id = index
                    ip = textbox_hardware_ip.get().strip()
                    mark = textbox_hardware_mark.get().strip()
                    place = textbox_hardware_place.get().strip()
                    name = textbox_hardware_name.get().strip()
                    link = textbox_hardware_link.get()
                    info = textbox_hardware_info.get()
                    type = combobox_hardware_type.get().strip()

                    cursor.execute("""
                                        UPDATE ITmanager_hardware
                                        SET hardware_ip = ?, hardware_type = ?, hardware_mark = ?, hardware_place = ?, hardware_name = ?, hardware_link = ?, hardware_info = ?
                                        WHERE hardware_id = ?""", (ip, type, mark, place, name, link, info, id))
                    connection.commit()
                    cursor.close()
                    connection.close()
                    globals.hardware_event.destroy()
                    self.load_data()
                    self.show_page()
                    self.sort_column("hardware_ip", False)
                    hardware_message_success("Upravit záznam", "Informace o zařízení byly upraveny.")
                else:
                    hardware_message_error("Upravit záznam","Nejsou vyplněna správně všechna pole. \nProsím zkontrolujte formulář.")


        def hardware_delete():
            connection = connection_db()
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM ITmanager_hardware WHERE hardware_id=?", (index,))
            row = cursor.fetchone()

            ip = row[1]
            type = row[2]
            mark = row[3]
            place = row[4]
            name = row[5]
            link = row[6]
            info = row[7]


            response = messagebox.askyesno("Odstranit záznam", f"Opravdu chcete odstranit hardware ze seznamu?\n\nIP adresa: {ip} \nTyp: {type} \nOznačení: {mark} \nUmístění: {place} \nNázev: {name} \nOdkaz: {link} \nPoznámka: {info}")

            if response:
                cursor.execute("DELETE FROM ITmanager_hardware WHERE hardware_id=?", (index,))
                connection.commit()
                cursor.close()
                connection.close()
                self.load_data()
                self.show_page()
                messagebox.showinfo("Odstranit záznam", "Záznam byl smazán.")
            else:
                globals.hardware_event.destroy()
                self.reset_row_colors()

        def close_form():
            self.reset_row_colors()
            globals.hardware_event.destroy()


        # Main header
        label_header = ctk.CTkLabel(globals.hardware_event, text="Změna údajů HARDWARU")
        label_header.configure(font=("Arial", 14, "bold"))
        label_header.pack(pady=(25, 0), padx=(0, 0))


        # Settings for IP adrress
        frame_hardware_ip = ctk.CTkFrame(globals.hardware_event,  fg_color="#242222")
        frame_hardware_ip.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_hardware_ip = ctk.CTkLabel(frame_hardware_ip, text="IP adresa (nebo '-')")
        label_hardware_ip.configure(font=("Arial", 13, "bold"))
        label_hardware_ip.grid(row=0, column=0, pady=(0, 0), padx=(0, 0), sticky="w")


        textbox_hardware_ip = ctk.CTkEntry(frame_hardware_ip, width=200)
        textbox_hardware_ip.insert(0, hardware_info[1])
        textbox_hardware_ip.grid(row=0, column=1, pady=(0,0), padx=(47,0), sticky="w")


        # Setting for type of hardware
        frame_hardware_type = ctk.CTkFrame(globals.hardware_event, fg_color="#242222")
        frame_hardware_type.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_hardware_type = ctk.CTkLabel(frame_hardware_type, text="Typ zařízení")
        label_hardware_type.configure(font=("Arial", 13, "bold"))
        label_hardware_type.grid(row=1, column=0, pady=(0,0), padx=(0,0), sticky="w")

        combobox_hardware_type = ctk.CTkComboBox(frame_hardware_type, values=["-    typ zařízení  -", "Ostatní", "Router", "Tiskárna",
                                                                              "Server", "PC Stanice", "Switch"], width=200, justify="center")
        combobox_hardware_type.configure(state="readonly")
        combobox_hardware_type.set(hardware_info[2])
        combobox_hardware_type.grid(row=1, column=2, pady=(0,0), padx=(87,0), sticky="w")


        # Settings for hardware mark
        frame_hardware_mark = ctk.CTkFrame(globals.hardware_event, fg_color="#242222")
        frame_hardware_mark.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_hardware_mark = ctk.CTkLabel(frame_hardware_mark, text="Označení hardwaru")
        label_hardware_mark.configure(font=("Arial", 13, "bold"))
        label_hardware_mark.grid(row=2, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_hardware_mark = ctk.CTkEntry(frame_hardware_mark, width=200)
        textbox_hardware_mark.insert(0, hardware_info[3])
        textbox_hardware_mark.grid(row=2, column=1, pady=(0, 0), padx=(40, 0), sticky="w")


        # Settings for place of hardware
        frame_hardware_place = ctk.CTkFrame(globals.hardware_event, fg_color="#242222")
        frame_hardware_place.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_hardware_place = ctk.CTkLabel(frame_hardware_place, text="Umístění hardwaru")
        label_hardware_place.configure(font=("Arial", 13, "bold"))
        label_hardware_place.grid(row=3, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_hardware_place = ctk.CTkEntry(frame_hardware_place, width=200)
        textbox_hardware_place.insert(0, hardware_info[4])
        textbox_hardware_place.grid(row=3, column=1, pady=(0, 0), padx=(45, 0), sticky="w")


        # Settings for name of hardware
        frame_hardware_name = ctk.CTkFrame(globals.hardware_event, fg_color="#242222")
        frame_hardware_name.pack(pady=(30, 0), padx=(35, 0), anchor="w")

        label_hardware_name = ctk.CTkLabel(frame_hardware_name, text="Název zařízení")
        label_hardware_name.configure(font=("Arial", 13, "bold"))
        label_hardware_name.grid(row=4, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_hardware_name = ctk.CTkEntry(frame_hardware_name, width=200)
        textbox_hardware_name.insert(0, hardware_info[5])
        textbox_hardware_name.grid(row=4, column=1, pady=(0, 0), padx=(70, 0), sticky="w")


        # Settings for link of hardware
        frame_hardware_link = ctk.CTkFrame(globals.hardware_event, fg_color="#242222")
        frame_hardware_link.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_hardware_link = ctk.CTkLabel(frame_hardware_link, text="Odkaz na zařízení")
        label_hardware_link.configure(font=("Arial", 13, "bold"))
        label_hardware_link.grid(row=5, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_hardware_link = ctk.CTkEntry(frame_hardware_link, width=200)
        textbox_hardware_link.insert(0, hardware_info[6])
        textbox_hardware_link.grid(row=5, column=1, pady=(0, 0), padx=(50, 0), sticky="w")


        # Settings for information of hardware
        frame_hardware_info = ctk.CTkFrame(globals.hardware_event, fg_color="#242222")
        frame_hardware_info.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_hardware_info = ctk.CTkLabel(frame_hardware_info, text="Poznámka k zařízení")
        label_hardware_info.configure(font=("Arial", 13, "bold"))
        label_hardware_info.grid(row=6, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_hardware_info = ctk.CTkEntry(frame_hardware_info, width=200)
        textbox_hardware_info.insert(0, hardware_info[7])
        textbox_hardware_info.grid(row=6, column=1, pady=(0, 0), padx=(32, 0), sticky="w")


        # Setting for buttons
        frame_hardware_buttons = ctk.CTkFrame(globals.hardware_event, fg_color="#242222")
        frame_hardware_buttons.pack(pady=(15, 0), padx=(57, 0), anchor="w")

        button_hardware_cancel = ctk.CTkButton(frame_hardware_buttons, text="Vrátit zpět", width=10, command=cancel_form)
        button_hardware_cancel.configure(font=("Arial", 14, "bold"))
        button_hardware_cancel.grid(row=7, column=0, pady=(15, 0), padx=(30, 0))

        button_hardware_add = ctk.CTkButton(frame_hardware_buttons, text="Upravit", width=10, command=hardware_edit)
        button_hardware_add.configure(font=("Arial", 14, "bold"))
        button_hardware_add.grid(row=7, column=1, pady=(15, 0), padx=(10, 0))

        button_hardware_delete = ctk.CTkButton(frame_hardware_buttons, text="Odstranit", width=10, command=hardware_delete)
        button_hardware_delete.configure(font=("Arial", 14, "bold"))
        button_hardware_delete.grid(row=7, column=2, pady=(15, 0), padx=(10, 0))

        button_hardware_close = ctk.CTkButton(frame_hardware_buttons, text="Zavřít", width=10, command=close_form)
        button_hardware_close.configure(font=("Arial", 14, "bold"))
        button_hardware_close.grid(row=7, column=3, pady=(15, 0), padx=(10, 0))







