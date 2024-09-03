import tkinter
import customtkinter as ctk
from connection import connection_db
from tkinter import messagebox, ttk
import pandas as pd
import os
import ipaddress
from reportlab.pdfgen import canvas
from fpdf import FPDF
from datetime import datetime
import globals

class Printers_material_frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="#333232")
        self.sort_reverse = False
        self.df = None
        self.selected_record_id = None
        self.selected_edit_id = None
        self.configure_treeview_style()
        self.material_table_show()
        self.tree.tag_configure('selected', background='#4e6b47')
        self.load_data()
        self.show_page()

    def find_material(self):
        messagebox.showinfo("Vyhledat materiál tiskárny", "Bohoužel tato funkce není dostupná.")

    def create_pdf(self):
        # Připojení k databázi a načtení názvů sloupců
        connection = connection_db()
        cursor = connection.cursor()
        cursor.execute("PRAGMA table_info(ITmanager_printer_materials)")
        columns = cursor.fetchall()

        # Nastavení PDF
        pdf = FPDF(orientation="L", unit="pt", format="A4")
        font_path = "Data/arial.ttf"
        if not os.path.exists(font_path):
            raise RuntimeError(f"Font file '{font_path}' not found")

        pdf.add_font("Arial", "", font_path, uni=True)
        pdf.set_font("Arial", size=12)
        pdf.set_font("Arial", style="B", size=12)
        pdf.add_page()

        # Definování názvů sloupců a jejich šířek
        column_widths = [180, 300, 60, 250]
        columns_names = ["Název tiskárny", "Název materiálu", "Cena", "Poznámka"]

        # Generování záhlaví sloupců
        for idx, column_name in enumerate(columns_names):
            pdf.cell(w=column_widths[idx], h=15, txt=column_name, border=1, align='C')

        pdf.ln()

        # Vybereme sloupce, které chceme zahrnout do PDF, a vytvoříme seznam řádků
        rows = self.df[["hardware_name", "printer_material_name", "printer_material_price",
                        "printer_material_info"]].values.tolist()

        # Zápis dat
        pdf.set_font("Arial", size=10)
        for row in rows:
            for idx, element in enumerate(row):
                pdf.cell(w=column_widths[idx], h=15, txt=str(element), border=1, align='C')
            pdf.ln()  # Přidání nového řádku po každém řádku dat

        # Uložení PDF
        date = datetime.now()
        date_now = date.strftime("%Y_%m_%d-%H_%M")
        pdf.output(f"./Reporty/Tiskarny_ceny_materialu_{date_now}.pdf")
        messagebox.showinfo("PDF soubor", f"Soubor: \n\nTiskarny_ceny_materialu_{date_now}.pdf\n\nbyl vygenerován. \n\nReport naleznete ve složce 'reporty'.")
        connection.close()


    def configure_treeview_style(self):
        style = ttk.Style()
        style.theme_use("classic")
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), anchor="center", background="#92ff75")
        style.configure("Treeview", rowheight=30, font=("Arial", 10))
        style.configure("Treeview", background="#333232", fieldbackground="#333232", foreground="white")
        style.map("Treeview", background=[("selected", "#347083")], foreground=[("selected", "white")])
        style.map("Treeview.Heading", background=[("active", "#63cc47")], foreground=[("active", "black")])
        style.configure("Vertical.TScrollbar", background="#4A4A4A", troughcolor="#333333", bordercolor="#333333", arrowcolor="#FFFFFF", relief="flat")

    def material_table_show(self):
        # FRAME
        frame_buttons = ctk.CTkFrame(self, fg_color="#333232")
        frame_buttons.grid(row=0, column=0, columnspan=5, pady=(20, 0), padx=(20, 20), sticky="ew")

        # BUTTON
        button_material_add = ctk.CTkButton(frame_buttons, text="Vložit nový materiál tiskárny", width=10, command=self.material_add_event)
        button_material_add.configure(font=("Arial", 12, "bold"))
        button_material_add.grid(row=0, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        button_hardware_find = ctk.CTkButton(frame_buttons, text="Vyhledat materiál tiskárny", width=10, command=self.find_material)
        button_hardware_find.configure(font=("Arial", 12, "bold"))
        button_hardware_find.grid(row=0, column=1, pady=(0, 0), padx=(10, 0), sticky="w")

        button_hardware_print = ctk.CTkButton(frame_buttons, text="Tisk materiálů tiskáren", width=10, command=self.create_pdf)
        button_hardware_print.configure(font=("Arial", 12, "bold"))
        button_hardware_print.grid(row=0, column=2, pady=(0, 0), padx=(10, 0), sticky="w")

        # SPACE COLUMNS
        frame_buttons.grid_columnconfigure(3, weight=1)
        frame_buttons.grid_columnconfigure(4, weight=1)
        frame_buttons.grid_columnconfigure(5, weight=1)

        label_description = ctk.CTkLabel(frame_buttons, text="Přehled spotřebního materiálu")
        label_description.configure(font=("Arial", 24, "bold"))
        label_description.grid(row=1, column=0, columnspan=6, pady=(40, 25), padx=(0, 0), sticky="ew")

        self.tree = ttk.Treeview(self, columns=("hardware_name", "printer_material_name", "printer_material_price", "pracovnici", "printer_material_info"), show='headings', height=25)
        self.tree.heading("hardware_name", text="Název tiskárny", command=lambda: self.sort_column("hardware_name", False))
        self.tree.heading("printer_material_name", text="Název materiálu", command=lambda: self.sort_column("printer_material_name", False))
        self.tree.heading("printer_material_price", text="Cena Kč", command=lambda: self.sort_column("printer_material_price", False))
        self.tree.heading("pracovnici", text="Pracovníci", command=lambda: self.sort_column("pracovnici", False))
        self.tree.heading("printer_material_info", text="Poznámka", command=lambda: self.sort_column("printer_material_info", False))

        self.tree.column("hardware_name", width=300, anchor="center")
        self.tree.column("printer_material_name", width=450, anchor="center")
        self.tree.column("printer_material_price", width=100, anchor="center")
        self.tree.column("pracovnici", width=250, anchor="center")
        self.tree.column("printer_material_info", width=400, anchor="center")

        for column in self.tree["columns"]:
            self.tree.column(column, anchor="center")

        self.tree.grid(row=1, column=0, columnspan=5, pady=(0, 0), padx=(20, 0), sticky="nsew")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=5, sticky="ns")

        # DYNAMIC RESIZING
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(5, weight=0)  # For the scrollbar

        self.tree.bind("<Configure>", lambda e: self.adjust_column_widths())

        self.lock_columns()

    def adjust_column_widths(self):
        total_width = self.tree.winfo_width()
        num_columns = len(self.tree["columns"])
        column_width = total_width // num_columns
        for column in self.tree["columns"]:
            self.tree.column(column, width=column_width)

    def load_data(self):
        connection = connection_db()  # Implementace připojení k databázi
        cursor = connection.cursor()

        sql_query = """
        SELECT pm.printer_material_id, 
               h.hardware_name, 
               h.hardware_place, 
               pm.printer_material_name, 
               pm.printer_material_price,
               h.hardware_info AS pracovnici,
               pm.printer_material_info,
               pm.printer_material_printer_id
        FROM ITmanager_printer_materials pm
        JOIN ITmanager_hardware h ON pm.printer_material_printer_id = h.hardware_id
        """
        df = pd.read_sql_query(sql_query, connection)
        self.df = df
        connection.close()

        # Vymazání existujících dat v Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Vložení nových dat do Treeview s tagy obsahujícími ID záznamů
        for index, row in df.iterrows():
            self.tree.insert("", "end", values=(
                row["hardware_name"], row["printer_material_name"], row["printer_material_price"], row["pracovnici"],
                row["printer_material_info"], row["printer_material_printer_id"]), tags=(str(row["printer_material_id"]),))


    def show_page(self):
        # Vymazání existujících dat v Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Vložení dat z DataFrame do Treeview
        for index, row in self.df.iterrows():
            printer_material_printer_id = str(row.get("printer_material_printer_id", ""))
            self.tree.insert("", "end", text=row["printer_material_id"], values=(
                row["hardware_name"],
                row["printer_material_name"],
                row["printer_material_price"],
                row["pracovnici"],
                row["printer_material_info"],
                row["printer_material_printer_id"]
            ))

    def reset_row_colors(self):
        for row in self.tree.get_children():
            self.tree.item(row, tags=())
        self.tree.tag_configure('selected', background='#4e6b47')

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

            current_tags = self.tree.item(item_id, "tags")
            self.tree.item(item_id, tags=('selected',))
            record_id = self.tree.item(item_id, "text")
            item_data = self.tree.item(item_id, "values")

            printer_name = item_data[0]
            material_name = item_data[1]
            price = item_data[2]

            # Získání pracovníka spojeného s daným materiálem
            pracovnici = item_data[3]

            info = item_data[4]  # Zde je vhodné zvolit, kterou informaci použít (může být kombinovaná nebo původní)
            printer_material_printer_id = item_data[5]

            self.material_edit_event(record_id, printer_name, material_name, price, pracovnici, info, printer_material_printer_id)

    def sort_column(self, col, reverse):
        if col not in self.df.columns:
            print(f"Sloupec {col} není v datovém rámci.")
            return

        if col == "hardware_name":
            self.df = self.df.sort_values(by="hardware_name", ascending=not reverse)
        else:
            self.df = self.df.sort_values(by=col, ascending=not reverse)

        self.show_page()
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def on_detail_window_close(self, window):
        self.reset_row_colors()  # Reset the row colors when the detail window is closed
        window.destroy()

    def material_add_event(self):
        
        if globals.material_event_open:
            globals.material_event.destroy()

        globals.material_event = ctk.CTkToplevel(fg_color="#242222")
        globals.material_event.title("Informace o novém materiálu")
        globals.material_event.resizable(width=False, height=False)
        globals.material_event_open = True

        window_width = 500
        windows_height = 370
        screen_width = globals.material_event.winfo_screenwidth()
        screen_heigth = globals.material_event.winfo_screenheight()

        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_heigth / 2 - windows_height / 2)

        globals.material_event.geometry(f"{window_width}x{windows_height}+{center_x}+{center_y}")


        def material_message_success(title, message):
            response = messagebox.showinfo(title, message)

        def material_message_error(title, message):
            response = messagebox.showerror(title, message)
            globals.material_event.lift()

        def cancel_form():
            combobox_material_printer_id.set(value="-    název tiskárny  -")
            textbox_material_name.delete(0, "end")
            textbox_material_price.delete(0, "end")
            textbox_material_info.delete(0, "end")
            button_material_cancel.focus_set()

        def material_refresh_table():
            frame_labels_db = ctk.CTkFrame(self, fg_color="#242222")
            frame_labels_db.pack(pady=(0, 0), padx=(100, 0), anchor="w")

            connection = connection_db()
            df = pd.read_sql_query("SELECT * FROM ITmanager_printer_materials", connection)
            self.maerial_show_data(df)

        def get_printer_names():
            connection = connection_db()
            cursor = connection.cursor()
            cursor.execute(
                "SELECT hardware_id, hardware_name, hardware_info FROM ITmanager_hardware WHERE hardware_type='Tiskárna'")
            printers = cursor.fetchall()
            connection.close()

            printer_names = {}

            for hardware_id, name, info in printers:
                formatted_name = f"{name} - ({info})"
                printer_names[formatted_name] = {"id": hardware_id, "name": name, "info": info}

            return printer_names

        def material_add():
            connection = connection_db()
            cursor = connection.cursor()

            if (combobox_material_printer_id.get().strip() != "-    název tiskárny  -" and
                    textbox_material_name.get().strip() != "" and
                    textbox_material_price.get().strip() != ""):

                printer_name_with_info = combobox_material_printer_id.get().strip()
                printer_data = get_printer_names().get(printer_name_with_info)
                material_info = textbox_material_info.get().strip()

                if printer_data:
                    material_name = textbox_material_name.get().strip()
                    price = textbox_material_price.get().strip()

                    # Vložení materiálu pouze pro jedno ID tiskárny
                    printer_id = printer_data["id"]  # Použití klíče 'id' místo 'ids'
                    cursor.execute("""
                        INSERT INTO ITmanager_printer_materials (printer_material_printer_id, printer_material_name, printer_material_price, printer_material_info)
                        VALUES (?, ?, ?, ?)
                    """, (printer_id, material_name, price, material_info))

                    connection.commit()
                    cursor.close()
                    connection.close()

                    self.reset_row_colors()
                    self.load_data()
                    self.material_table_show()
                    self.sort_column("hardware_name", False)
                    globals.material_event.destroy()
                    material_message_success("Info", "Nový materiál byl přidán.")
                else:
                    material_message_error("Chyba!", "Nebyla nalezena žádná tiskárna s vybraným názvem.")
            else:
                material_message_error("Chyba!","Nejsou vyplněna správně všechna pole. \nProsím zkontrolujte formulář.")

        # Main header
        label_header = ctk.CTkLabel(globals.material_event, text="Informace o novém materiálu")
        label_header.configure(font=("Arial", 14, "bold"))
        label_header.pack(pady=(25, 0), padx=(0, 0))


        # Settings for printer ID for material
        frame_material_printer_id = ctk.CTkFrame(globals.material_event,  fg_color="#242222")
        frame_material_printer_id.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_material_printer_id = ctk.CTkLabel(frame_material_printer_id, text="Název tiskárny")
        label_material_printer_id.configure(font=("Arial", 13, "bold"))
        label_material_printer_id.grid(row=0, column=0, pady=(0,0), padx=(0,0), sticky="w")

        printer_names = get_printer_names()
        combobox_material_printer_id = ctk.CTkComboBox(frame_material_printer_id, values=["-    název tiskárny  -"] + list(printer_names.keys()), width=300, justify="center")
        combobox_material_printer_id.configure(state="readonly")
        combobox_material_printer_id.grid(row=0, column=1, pady=(0, 0), padx=(33, 0), sticky="w")

        # Setting for name of meterial
        frame_material_name = ctk.CTkFrame(globals.material_event, fg_color="#242222")
        frame_material_name.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_material_name = ctk.CTkLabel(frame_material_name, text="Název materiálu")
        label_material_name.configure(font=("Arial", 13, "bold"))
        label_material_name.grid(row=1, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_material_name = ctk.CTkEntry(frame_material_name, width=300)
        textbox_material_name.grid(row=1, column=1, pady=(0, 0), padx=(20, 0), sticky="w")


        # Settings for price of material
        frame_material_price = ctk.CTkFrame(globals.material_event, fg_color="#242222")
        frame_material_price.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_material_price = ctk.CTkLabel(frame_material_price, text="Cena materiálu")
        label_material_price.configure(font=("Arial", 13, "bold"))
        label_material_price.grid(row=2, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_material_price = ctk.CTkEntry(frame_material_price, width=100)
        textbox_material_price.grid(row=2, column=1, pady=(0, 0), padx=(25, 0), sticky="w")


        # Settings for info of material
        frame_material_info = ctk.CTkFrame(globals.material_event, fg_color="#242222")
        frame_material_info.pack(pady=(30, 0), padx=(35, 0), anchor="w")

        label_material_info = ctk.CTkLabel(frame_material_info, text="Poznámka")
        label_material_info.configure(font=("Arial", 13, "bold"))
        label_material_info.grid(row=3, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_material_info = ctk.CTkEntry(frame_material_info, width=300)
        textbox_material_info.grid(row=3, column=1, pady=(0, 0), padx=(55, 0), sticky="w")


        # Setting for buttons
        frame_material_buttons = ctk.CTkFrame(globals.material_event, fg_color="#242222")
        frame_material_buttons.pack(pady=(15, 0), padx=(35, 0), anchor="w")

        button_material_cancel = ctk.CTkButton(frame_material_buttons, text="Storno", width=10, command=cancel_form)
        button_material_cancel.configure(font=("Arial", 14, "bold"))
        button_material_cancel.grid(row=4, column=0, pady=(15, 0), padx=(300, 0))

        button_material_add = ctk.CTkButton(frame_material_buttons, text="Uložit", width=10, command=material_add)
        button_material_add.configure(font=("Arial", 14, "bold"))
        button_material_add.grid(row=4, column=1, pady=(15, 0), padx=(10, 0))


    def material_edit_event(self, record_id, printer_name, material_name, price, worker, info, printer_material_printer_id):

        if globals.material_event_open:
            globals.material_event.destroy()

        globals.material_event = ctk.CTkToplevel(fg_color="#242222")
        globals.material_event.title("Změna údajů materiálu tiskárny")
        globals.material_event.resizable(width=False, height=False)
        globals.material_event_open = True

        globals.material_event.protocol("WM_DELETE_WINDOW", lambda: self.on_detail_window_close(globals.material_event))

        window_width = 500
        windows_height = 430
        screen_width = globals.material_event.winfo_screenwidth()
        screen_heigth = globals.material_event.winfo_screenheight()

        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_heigth / 2 - windows_height / 2)

        globals.material_event.geometry(f"{window_width}x{windows_height}+{center_x}+{center_y}")


        def material_message_success(title, message):
            response = messagebox.showinfo(title, message)

        def material_message_error(title, message):
            response = messagebox.showerror(title, message)
            globals.material_event.lift()

        def cancel_form():
            combobox_material_printer_id.set(printer_name)
            textbox_material_name.delete(0, "end")
            textbox_material_name.insert(0, material_name)
            textbox_material_price.delete(0, "end")
            textbox_material_price.insert(0, price)
            textbox_material_info.delete(0, "end")
            textbox_material_info.insert(0, info)
            button_material_cancel.focus_set()

        def material_edit():
            connection = connection_db()
            cursor = connection.cursor()

        def get_printer_names():
            connection = connection_db()
            cursor = connection.cursor()
            cursor.execute(
                "SELECT hardware_id, hardware_name, hardware_info FROM ITmanager_hardware WHERE hardware_type='Tiskárna'")
            printers = cursor.fetchall()
            connection.close()

            printer_names = {}

            for hardware_id, name, info in printers:
                formatted_name = f"{name} - ({info})"
                printer_names[formatted_name] = hardware_id

            return printer_names

        def handle_selection(event):
            self.selected_edit_id = None
            selected_name = combobox_material_printer_id.get().strip()
            if selected_name != "-    název tiskárny  -":
                print(printer_names[selected_name])
                self.selected_edit_id = printer_names[selected_name]  # Získání skrytého ID pro vybraný název

        def material_edit():
            connection = connection_db()
            cursor = connection.cursor()

            if self.selected_edit_id is None:
                selected_name = f"{combobox_material_printer_id.get().strip()} - ({textbox_worker_names.get().strip()})"

                if selected_name != "-    název tiskárny  -":
                    self.selected_edit_id = printer_names[selected_name]

            if (combobox_material_printer_id.get().strip() != "-    název tiskárny  -" and
                    self.selected_edit_id != None and
                    textbox_material_name.get().strip() != "" and
                    textbox_material_price.get().strip() != "" and
                    textbox_material_info.get().strip() != ""):

                material_name = textbox_material_name.get().strip()
                material_price = textbox_material_price.get().strip()
                material_info = textbox_material_info.get().strip()

                cursor.execute("""
                    UPDATE ITmanager_printer_materials
                    SET printer_material_printer_id = ?, printer_material_name = ?, 
                        printer_material_price = ?, printer_material_info = ?
                    WHERE printer_material_id = ?
                    """, (self.selected_edit_id, material_name, material_price, material_info, record_id))

                connection.commit()
                cursor.close()
                connection.close()

                globals.material_event.destroy()
                self.load_data()
                self.show_page()
                self.sort_column("hardware_name", False)
                self.selected_edit_id = None
                material_message_success("Upravit záznam", "Informace o zařízení byly upraveny.")
            else:
                material_message_error("Chyba!","Nejsou vyplněna správně všechna pole. \nProsím zkontrolujte formulář.")

        def material_delete():
            connection = connection_db()
            cursor = connection.cursor()
            cursor.execute("""
                    SELECT pm.printer_material_id, h.hardware_name, h.hardware_place, pm.printer_material_name, pm.printer_material_price, pm.printer_material_info
                    FROM ITmanager_printer_materials pm
                    JOIN ITmanager_hardware h ON pm.printer_material_printer_id = h.hardware_id
                    WHERE pm.printer_material_id=?
                    """, (record_id,))
            row = cursor.fetchone()

            printer_id = row[1]
            name = row[3]
            price = row[4]
            info = row[5]

            response = messagebox.askyesno("Odstranit záznam", f"Opravdu chcete odstranit material ze seznamu?\n\nNázev tiskárny: {printer_id} \nMateriál: {name} \nCena {price} Kč \nPoznámka: {info}")

            if response:
                cursor.execute("DELETE FROM ITmanager_printer_materials WHERE printer_material_id=?", (record_id,))
                connection.commit()
                cursor.close()
                connection.close()
                self.load_data()
                self.show_page()
                messagebox.showinfo("Odstranit záznam", "Záznam byl smazán.")
            else:
                globals.material_event.destroy()
                self.reset_row_colors()

        def close_form():
            self.reset_row_colors()
            globals.material_event.destroy()

        # Main header
        label_header = ctk.CTkLabel(globals.material_event, text="Informace o novém materiálu")
        label_header.configure(font=("Arial", 14, "bold"))
        label_header.pack(pady=(25, 0), padx=(0, 0))


        # Settings for printer ID for material
        frame_material_printer_id = ctk.CTkFrame(globals.material_event,  fg_color="#242222")
        frame_material_printer_id.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_material_printer_id = ctk.CTkLabel(frame_material_printer_id, text="ID tiskárny")
        label_material_printer_id.configure(font=("Arial", 13, "bold"))
        label_material_printer_id.grid(row=0, column=0, pady=(0,0), padx=(0,0), sticky="w")


        printer_names = get_printer_names()
        combobox_material_printer_id = ctk.CTkComboBox(frame_material_printer_id, values=["-    název tiskárny  -"] + list(printer_names.keys()), width=300, justify="center", command=handle_selection)
        combobox_material_printer_id.set(printer_name)
        combobox_material_printer_id.configure(state="readonly")
        combobox_material_printer_id.grid(row=0, column=1, pady=(0, 0), padx=(57, 0), sticky="w")



        # Setting for name of meterial
        frame_material_name = ctk.CTkFrame(globals.material_event, fg_color="#242222")
        frame_material_name.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_material_name = ctk.CTkLabel(frame_material_name, text="Název materiálu")
        label_material_name.configure(font=("Arial", 13, "bold"))
        label_material_name.grid(row=1, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_material_name = ctk.CTkEntry(frame_material_name, width=300)
        textbox_material_name.insert(0, material_name)
        textbox_material_name.grid(row=1, column=1, pady=(0, 0), padx=(20, 0), sticky="w")


        # Settings for price of material
        frame_material_price = ctk.CTkFrame(globals.material_event, fg_color="#242222")
        frame_material_price.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_material_price = ctk.CTkLabel(frame_material_price, text="Cena materiálu")
        label_material_price.configure(font=("Arial", 13, "bold"))
        label_material_price.grid(row=2, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_material_price = ctk.CTkEntry(frame_material_price, width=100)
        textbox_material_price.insert(0, price)
        textbox_material_price.grid(row=2, column=1, pady=(0, 0), padx=(25, 0), sticky="w")


        # Setting for name of worker
        frame_worker_names = ctk.CTkFrame(globals.material_event, fg_color="#242222")
        frame_worker_names.pack(pady=(30, 0), padx=(35, 0), anchor="w")

        label_worker_names = ctk.CTkLabel(frame_worker_names, text="Pracovníci")
        label_worker_names.configure(font=("Arial", 13, "bold"))
        label_worker_names.grid(row=3, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_worker_names = ctk.CTkEntry(frame_worker_names, width=300)
        textbox_worker_names.insert(0, worker)
        textbox_worker_names.configure(state="readonly")
        textbox_worker_names.grid(row=3, column=1, pady=(0, 0), padx=(55, 0), sticky="w")


        # Settings for info of material
        frame_material_info = ctk.CTkFrame(globals.material_event, fg_color="#242222")
        frame_material_info.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_material_info = ctk.CTkLabel(frame_material_info, text="Poznámka")
        label_material_info.configure(font=("Arial", 13, "bold"))
        label_material_info.grid(row=4, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        textbox_material_info = ctk.CTkEntry(frame_material_info, width=300)
        textbox_material_info.insert(0, info)
        textbox_material_info.grid(row=4, column=1, pady=(0, 0), padx=(55, 0), sticky="w")


        # Setting for buttons
        frame_material_buttons = ctk.CTkFrame(globals.material_event, fg_color="#242222")
        frame_material_buttons.pack(pady=(15, 0), padx=(35, 0), anchor="w")

        button_material_cancel = ctk.CTkButton(frame_material_buttons, text="Storno", width=10, command=cancel_form)
        button_material_cancel.configure(font=("Arial", 14, "bold"))
        button_material_cancel.grid(row=5, column=0, pady=(15, 0), padx=(145, 0))

        button_material_delete = ctk.CTkButton(frame_material_buttons, text="Odstranit", width=10, command=material_delete)
        button_material_delete.configure(font=("Arial", 14, "bold"))
        button_material_delete.grid(row=5, column=1, pady=(15, 0), padx=(10, 0))

        button_material_add = ctk.CTkButton(frame_material_buttons, text="Uložit", width=10, command=material_edit)
        button_material_add.configure(font=("Arial", 14, "bold"))
        button_material_add.grid(row=5, column=2, pady=(15, 0), padx=(10, 0))

        button_material_close = ctk.CTkButton(frame_material_buttons, text="Zavřít", width=10, command=close_form)
        button_material_close.configure(font=("Arial", 14, "bold"))
        button_material_close.grid(row=5, column=3, pady=(15, 0), padx=(10, 0))


