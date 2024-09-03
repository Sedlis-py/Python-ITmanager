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
from tkcalendar import Calendar
import locale
from datetime import datetime
import globals

class Printers_event_frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="#333232")
        locale.setlocale(locale.LC_TIME, "cs_CZ")
        self.name_of_printer = None
        self.sort_reverse = False
        self.selected_year = None
        self.selected_hardware = None
        self.configure_treeview_style()
        self.event_table_show()
        self.df = None
        self.load_data()

    def find_printer_event(self):
        messagebox.showinfo("Vyhledat náklady tiskárny", "Bohoužel tato funkce není dostupná.")

    def create_pdf(self):
        original_df = self.df.copy()  # Uložíme původní data

        # Inicializace dotazu a parametrů
        if self.selected_year is None:
            self.selected_year = "Zobrazit vše"

        if self.selected_hardware is None:
            self.selected_hardware = "Zobrazit vše"

        if self.selected_year == "Zobrazit vše":
            year_condition = "1=1"  # Neprovádí žádné filtrování podle roku
            parameters = []  # Bez parametrů
        else:
            year_condition = "SUBSTR(pe.printer_event_date, -4) = ?"
            parameters = [self.selected_year]

        if self.selected_hardware == "Zobrazit vše":
            hardware_condition = "1=1"  # Neprovádí žádné filtrování podle zařízení
        else:
            hardware_condition = "(h.hardware_name || ' / ' || h.hardware_place || ' / ' || h.hardware_info) = ?"
            parameters.append(self.selected_hardware)

        if self.selected_year == "Zobrazit vše" and self.selected_hardware == "Zobrazit vše":
            query = """
                        SELECT 
                            pe.printer_event_printer_id,
                            pe.printer_event_id, 
                            h.hardware_name, 
                            h.hardware_place,
                            h.hardware_info,
                            pe.printer_event_type, 
                            pe.printer_event_material_name,
                            pe.printer_event_other,
                            pe.printer_event_price,
                            pe.printer_event_date
                        FROM 
                            ITmanager_printer_events pe
                        JOIN 
                            ITmanager_hardware h ON pe.printer_event_printer_id = h.hardware_id
                    """
            connection = connection_db()
            cursor = connection.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
        else:
            query = f"""
                SELECT 
                    pe.printer_event_printer_id,
                    pe.printer_event_id, 
                    h.hardware_name, 
                    h.hardware_place,
                    h.hardware_info,
                    pe.printer_event_type, 
                    pe.printer_event_material_name,
                    pe.printer_event_other,
                    pe.printer_event_price,
                    pe.printer_event_date
                FROM 
                    ITmanager_printer_events pe
                JOIN 
                    ITmanager_hardware h ON pe.printer_event_printer_id = h.hardware_id
                WHERE
                    {year_condition} AND
                    {hardware_condition}
                """

            connection = connection_db()
            cursor = connection.cursor()
            cursor.execute(query, parameters)
            data = cursor.fetchall()

        # Připojení k databázi a načtení dat
        connection = connection_db()
        cursor = connection.cursor()
        cursor.execute(query, parameters)
        data = cursor.fetchall()

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
        column_widths = [360, 85, 180, 60, 120]
        columns_names = ["Název tiskárny", "Typ události", "Jiná událost", "Cena", "Datum události"]

        # Generování záhlaví sloupců
        for idx, column_name in enumerate(columns_names):
            pdf.cell(w=column_widths[idx], h=15, txt=column_name, border=1, align='C')

        pdf.ln()

        # Vytvoření DataFrame z vrácených dat
        self.df = pd.DataFrame(data, columns=["printer_event_printer_id", "printer_event_id", "hardware_name",
                                              "hardware_place", "hardware_info", "printer_event_type",
                                              "printer_event_material_name", "printer_event_other",
                                              "printer_event_price", "printer_event_date"])

        self.df["printer_event_date"] = pd.to_datetime(self.df["printer_event_date"], dayfirst=True)

        # Formátování datumu do požadovaného formátu
        self.df["formatted_event_date"] = self.df["printer_event_date"].dt.strftime("%d.%m.%Y")

        self.df["printer_info"] = self.df["hardware_name"] + " / " + self.df["hardware_place"] + " / " + self.df[
            "hardware_info"]

        # Vybereme sloupce, které chceme zahrnout do PDF, a vytvoříme seznam řádků
        rows = self.df[["printer_info", "printer_event_type", "printer_event_other",
                        "printer_event_price", "formatted_event_date"]].values.tolist()

        # Zápis dat
        pdf.set_font("Arial", size=10)
        for row in rows:
            for idx, element in enumerate(row):
                pdf.cell(w=column_widths[idx], h=15, txt=str(element), border=1, align='C')
            pdf.ln()  # Přidání nového řádku po každém řádku dat

        # Uložení PDF
        date = datetime.now()
        date_now = date.strftime("%Y_%m_%d-%H_%M_%S")
        pdf.output(f"./Reporty/Udalosti_tiskaren_{date_now}.pdf")
        messagebox.showinfo("PDF soubor",
                            f"Soubor: \n\nUdalosti_tiskaren_{date_now}.pdf\n\nbyl vygenerován. \n\nReport naleznete ve složce 'reporty'.")

        # Obnovíme původní df
        self.df = original_df.copy()
        self.filter_by_hardware_year("")  # Obnoví data podle uložených filtrů

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
        style.configure("Treeview.default", background='#333232', foreground='white')

    def event_table_show(self):
        # FRAME
        frame_buttons = ctk.CTkFrame(self, fg_color="#333232")
        frame_buttons.grid(row=0, column=0, columnspan=10, pady=(20, 0), padx=(20, 20), sticky="ew")

        # BUTTON
        button_printer_event_add = ctk.CTkButton(frame_buttons, text="Vložit novou událost", width=10, command=self.printer_add_event)
        button_printer_event_add.configure(font=("Arial", 12, "bold"))
        button_printer_event_add.grid(row=0, column=0, pady=(0, 0), padx=(0, 0), sticky="w")

        button_printer_event_find = ctk.CTkButton(frame_buttons, text="Vyhledat náklady na tiskárnu", width=10, command=self.find_printer_event)
        button_printer_event_find.configure(font=("Arial", 12, "bold"))
        button_printer_event_find.grid(row=0, column=1, pady=(0, 0), padx=(10, 0), sticky="w")

        button_printer_event_print = ctk.CTkButton(frame_buttons, text="Tisk nákladů na tiskárnu", width=10, command=self.create_pdf)
        button_printer_event_print.configure(font=("Arial", 12, "bold"))
        button_printer_event_print.grid(row=0, column=2, pady=(0, 0), padx=(10, 0), sticky="w")

        # SPACE COLUMNS
        frame_buttons.grid_columnconfigure(3, weight=1)
        frame_buttons.grid_columnconfigure(4, weight=1)
        frame_buttons.grid_columnconfigure(5, weight=1)

        label_description = ctk.CTkLabel(frame_buttons, text="Přehled nákladů tiskáren")
        label_description.configure(font=("Arial", 24, "bold"))
        label_description.grid(row=1, column=0, columnspan=10, pady=(30,25), padx=(0,0), sticky="ew")

        # FRAME
        frame_options = ctk.CTkFrame(self, fg_color="#333232")
        frame_options.grid(row=2, column=0, pady=(0, 0), padx=(20, 20), sticky="ew")

        frame_options.grid_columnconfigure(0, weight=1)

        label_printer_device = ctk.CTkLabel(frame_options, text="Vyberte zařízení")
        label_printer_device.configure(font=("Arial", 13, "bold"))
        label_printer_device.grid(row=0, column=1, pady=(30, 10), padx=(0, 0), sticky="e")

        hardware = self.combobox_data_hardware()
        self.combobox_printer_device = ctk.CTkComboBox(frame_options, values=hardware, width=500, justify="center", command=self.filter_by_hardware_year)
        self.combobox_printer_device.configure(state="readonly")
        self.combobox_printer_device.grid(row=0, column=2, pady=(30, 10), padx=(10, 0), sticky="e")

        label_printer_event_date = ctk.CTkLabel(frame_options, text="Vyber rok")
        label_printer_event_date.configure(font=("Arial", 13, "bold"))
        label_printer_event_date.grid(row=0, column=3, pady=(30, 10), padx=(25, 0), sticky="e")

        years = self.combobox_data_date()
        self.combobox_printer_event_date = ctk.CTkComboBox(frame_options, values=years, width=150, justify="center", command=self.filter_by_hardware_year)
        self.combobox_printer_event_date.configure(state="readonly")
        self.combobox_printer_event_date.grid(row=0, column=4, pady=(30, 10), padx=(10, 0), sticky="e")

        self.tree = ttk.Treeview(self, columns=("hardware_name", "printer_event_type", "printer_event_material_name", "printer_event_other", "printer_event_price", "printer_event_date"), show='headings', height=25)
        self.tree.heading("hardware_name", text="Název tiskárny", command=lambda: self.sort_column("hardware_name", False))
        self.tree.heading("printer_event_type", text="Typ události", command=lambda: self.sort_column("printer_event_type", False))
        self.tree.heading("printer_event_material_name", text="Název materiálu", command=lambda: self.sort_column("printer_event_material_name", False))
        self.tree.heading("printer_event_other", text="Jiná událost", command=lambda: self.sort_column("printer_event_material_name", False))
        self.tree.heading("printer_event_price", text="Cena Kč", command=lambda: self.sort_column("printer_event_price", False))
        self.tree.heading("printer_event_date", text="Datum události", command=lambda: self.sort_column("printer_event_date", False))

        self.tree.column("hardware_name", width=525, anchor="center")
        self.tree.column("printer_event_type", width=100, anchor="center")
        self.tree.column("printer_event_material_name", width=400, anchor="center")
        self.tree.column("printer_event_other", width=250, anchor="center")
        self.tree.column("printer_event_price", width=100, anchor="center")
        self.tree.column("printer_event_date", width=100, anchor="center")


        for column in self.tree["columns"]:
            self.tree.column(column, anchor="center")

        self.tree.grid(row=3, column=0, columnspan=10, pady=(0, 0), padx=(20, 0), sticky="nsew")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=3, column=10, sticky="ns")

        # DYNAMIC RESIZING
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(5, weight=0)  # For the scrollbar

        self.tree.bind("<Configure>", lambda e: self.adjust_column_widths())
        self.bind("<Configure>", self.adjust_combobox_widths)

        self.lock_columns()

    def adjust_column_widths(self):
        # Získání celkové šířky Treeview
        total_width = self.tree.winfo_width()

        # Nastavení minimální šířky pro konkrétní sloupec (např. "hardware_name")
        min_width_hardware_name = 500

        # Počet sloupců (kromě toho s pevně nastavenou šířkou)
        num_dynamic_columns = len(self.tree["columns"]) - 1

        # Výpočet zbývající šířky pro dynamické sloupce
        remaining_width = total_width - min_width_hardware_name

        # Výpočet šířky pro dynamické sloupce
        if num_dynamic_columns > 0:
            dynamic_column_width = remaining_width // num_dynamic_columns
        else:
            dynamic_column_width = remaining_width

        # Nastavení šířky sloupců
        for column in self.tree["columns"]:
            if column == "hardware_name":
                self.tree.column(column, width=min_width_hardware_name)
            else:
                self.tree.column(column, width=dynamic_column_width)

    def adjust_combobox_widths(self, event):
        # Get the current width of the window
        current_width = self.winfo_width()

        # Calculate the width for the comboboxes based on the window width
        combobox_width = int(current_width * 0.25)  # Adjust this multiplier as needed

        # Set the new width for both comboboxes
        self.combobox_printer_device.configure(width=combobox_width)
        max_date_combobox_width = 150  # Set this to your preferred maximum width
        self.combobox_printer_event_date.configure(width=min(combobox_width, max_date_combobox_width))

    def combobox_data_hardware(self):
        connection = connection_db()  # Implementace připojení k databázi
        cursor = connection.cursor()

        sql_query = """
            SELECT 
                pe.printer_event_id,
                h.hardware_name, 
                h.hardware_place,
                h.hardware_info
            FROM ITmanager_printer_events pe
            JOIN ITmanager_hardware h ON pe.printer_event_printer_id = h.hardware_id
        """
        df = pd.read_sql_query(sql_query, connection)

        # Spojení hodnot do jednoho sloupce a odstranění duplicit
        df["hardware_combined"] = df["hardware_name"] + " / " + df["hardware_place"] + " / " + df["hardware_info"]
        unique_hardware = df["hardware_combined"].unique().tolist()

        self.hardware_dict = dict(zip(df["hardware_combined"], df["printer_event_id"]))

        # Uzavření připojení k databázi
        connection.close()

        # Přidání možnosti "Zobrazit vše"
        hardware_list = ["Zobrazit vše"] + unique_hardware

        return hardware_list

    def combobox_data_date(self):
        connection = connection_db()  # Implementace připojení k databázi
        cursor = connection.cursor()

        sql_query = """
                                SELECT printer_event_id, printer_event_date
                                FROM ITmanager_printer_events
                                """
        df = pd.read_sql_query(sql_query, connection)

        df["printer_event_date"] = pd.to_datetime(df["printer_event_date"], format='%d.%m.%Y', dayfirst=True)
        df = df.sort_values(by='printer_event_date', ascending=False)
        #self.df = df

        self.year_dict = {}
        for _, row in df.iterrows():
            year = row["printer_event_date"].year
            if year not in self.year_dict:
                self.year_dict[year] = []
            self.year_dict[year].append(row["printer_event_id"])

        connection.close()

        years = ["Zobrazit vše"] + sorted(df["printer_event_date"].dt.year.unique().astype(str).tolist(), reverse=True)

        return years

    def update_comboboxes(self):
        hardware = self.combobox_data_hardware()
        self.combobox_printer_device.configure(values=hardware)
        self.combobox_printer_device.set("Zobrazit vše")
        years = self.combobox_data_date()
        self.combobox_printer_event_date.configure(values=years)
        self.combobox_printer_event_date.set("Zobrazit vše")

    def filter_by_hardware_year(self, info):

        self.selected_hardware = self.combobox_printer_device.get()
        self.selected_year = self.combobox_printer_event_date.get()

        filtered_df = self.df

        # Filtrování podle roku
        if self.selected_year != "Zobrazit vše":
            filtered_df = filtered_df[filtered_df["printer_event_date"].dt.year == int(self.selected_year)]

        # Filtrování podle zařízení
        if self.selected_hardware != "Zobrazit vše":
            filtered_df = filtered_df[
                (filtered_df["hardware_name"] + " / " + filtered_df["hardware_place"] + " / " + filtered_df[
                    "hardware_info"]) == self.selected_hardware
                ]

        # Vymazání existujících dat v Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Vložení nových dat do Treeview
        for index, row in filtered_df.iterrows():
            self.tree.insert("", "end", iid=row["printer_event_id"], values=(
                row["hardware_name"] + " / " + row["hardware_place"] + " / " + row["hardware_info"],
                row["printer_event_type"], row["printer_event_material_name"], row["printer_event_other"],
                row["printer_event_price"], row["printer_event_date"].strftime("%d.%m.%Y")))


    def load_data(self):
        connection = connection_db()  # Implementace připojení k databázi
        cursor = connection.cursor()

        sql_query = """
        SELECT pe.printer_event_printer_id,
               pe.printer_event_id, 
               h.hardware_name, 
               h.hardware_place,
               h.hardware_info,
               pe.printer_event_type, 
               pe.printer_event_material_name,
               pe.printer_event_other,
               pe.printer_event_price,
               pe.printer_event_date
        FROM ITmanager_printer_events pe
        JOIN ITmanager_hardware h ON pe.printer_event_printer_id = h.hardware_id
        """
        df = pd.read_sql_query(sql_query, connection)

        df["printer_event_date"] = pd.to_datetime(df["printer_event_date"], format='%d.%m.%Y', dayfirst=True)
        df = df.sort_values(by='printer_event_date', ascending=False)
        self.df = df
        connection.close()

        self.years = ["Zobrazit vše"] + sorted(self.df["printer_event_date"].dt.year.unique().astype(str).tolist())


        # Vymazání existujících dat v Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Vložení nových dat do Treeview s tagy obsahujícími ID záznamů
        for index, row in df.iterrows():
            self.tree.insert("", "end", iid=row["printer_event_id"], values=(
                row["hardware_name"] + " / " + row["hardware_place"] + " / " + row["hardware_info"], row["printer_event_type"], row["printer_event_material_name"], row["printer_event_other"],
                row["printer_event_price"], row["printer_event_date"].strftime("%d.%m.%Y")))

    def show_page(self):
        # Vymazání existujících dat v Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Vložení dat z DataFrame do Treeview
        for index, row in self.df.iterrows():
            self.tree.insert("", "end", text=row["printer_event_id"], values=(
                row["hardware_name"] + " / " + row["hardware_place"] + " / " + row["hardware_info"],
                row["printer_event_type"],
                row["printer_event_material_name"],
                row["printer_event_other"],
                row["printer_event_price"],
                row["printer_event_date"].strftime("%d.%m.%Y")
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
        self.tree.bind('<ButtonRelease-1>', self.handle_click)
        self.tree.bind('<Button-1>', self.ignore_column_resize)

    def ignore_column_resize(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "separator":
            return "break"
        return None  # Allow other events to proceed

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
        selected_item = self.tree.selection()

        if not selected_item:
            return

        selected_item = selected_item[0]  # Get the selected item
        record_values = self.tree.item(selected_item, 'values')
        record_id = selected_item


        if self.combobox_printer_device.get() == "Zobrazit vše" or self.combobox_printer_event_date.get() == "Zobrazit vše":
            pass
        else:
            selected_value = self.combobox_printer_device.get()

            if selected_value in self.hardware_dict:
                record_id = self.hardware_dict[selected_value]
                messagebox.showinfo("info", record_id)

        # Construct record info string
        record_info = (
            f"ID: {record_id}\n"
            f"Název tiskárny: {record_values[0]}\n"
            f"Typ události: {record_values[1]}\n"
            f"Název materiálu: {record_values[2]}\n"
            f"Jiná událost: {record_values[3]}\n"
            f"Cena Kč: {record_values[4]}\n"
            f"Datum události: {record_values[5]}"
        )


        # Debug print statement
        if messagebox.askyesno("Smazat záznam", f"Chcete smazat tento záznam?\n\n{record_info}"):
                if messagebox.askyesno("Záznam bude smazán", f"Záznam u tiskárny \n\n{record_values[0]}\n\n bude smazán."):
                    self.delete_record(record_id)
                else:
                    self.tree.selection_remove(selected_item)
                    pass
        else:
            self.tree.selection_remove(selected_item)
            pass

    def delete_record(self, record_id):
        selected_value = self.combobox_printer_device.get()

        if selected_value in self.hardware_dict:
            record_id = self.hardware_dict[selected_value]

        if record_id:
            connection = connection_db()
            cursor = connection.cursor()

            # SQL dotaz na odstranění záznamu podle ID
            cursor.execute("DELETE FROM ITmanager_printer_events WHERE printer_event_id = ?", (record_id,))
            connection.commit()

            cursor.close()
            connection.close()
            self.load_data()
            self.update_comboboxes()
            messagebox.showinfo("Odstranit záznam", "Záznam byl smazán.")

    def sort_column(self, col, reverse):
        if col not in self.df.columns:
            print(f"Sloupec {col} není v datovém rámci.")
            return

        # Příprava sloupce pro třídění
        self.df = self.df.sort_values(by=col, ascending=not reverse)

        self.show_page()
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))


    def printer_add_event(self):
        if globals.printer_event_open:
            globals.printer_event.destroy()

        globals.printer_event = ctk.CTkToplevel(fg_color="#242222")
        globals.printer_event.title("Nová událost tiskárny")
        globals.printer_event.resizable(width=False, height=False)
        globals.printer_event_open = True

        window_width = 550
        windows_height = 680
        screen_width = globals.printer_event.winfo_screenwidth()
        screen_heigth = globals.printer_event.winfo_screenheight()

        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_heigth / 2 - windows_height / 2)

        globals.printer_event.geometry(f"{window_width}x{windows_height}+{center_x}+{center_y}")
        current_date = datetime.now().strftime("%d.%m.%Y")
        selected_option = tkinter.IntVar()

        def event_message_success(title, message):
            response = messagebox.showinfo(title, message)

        def event_message_error(title, message):
            response = messagebox.showerror(title, message)
            globals.printer_event.lift()

        def printer_event_radio1():
            label_printer_name.configure(text_color="white")
            on_printer_select(self.name_of_printer)
            combobox_printer_name.configure(state="readonly")
            label_printer_cartridge.configure(text_color="white")
            combobox_printer_cartridge.configure(state="readonly")
            label_printer_another_event.configure(text_color="grey")
            textbox_printer_another_event.delete(0, "end")
            textbox_printer_another_event.configure(state="disable")
            self.textbox_printer_price.delete(0, "end")
            radio1_printer_type.focus_set()


        def printer_event_radio2():
            label_printer_name.configure(text_color="white")
            combobox_printer_name.configure(state="readonly")
            label_printer_cartridge.configure(text_color="grey")
            combobox_printer_cartridge.configure(values=["-    seznam tonerů   -"])
            combobox_printer_cartridge.set(value="-    seznam tonerů   -")
            combobox_printer_cartridge.configure(state="disable")
            label_printer_another_event.configure(text_color="white")
            textbox_printer_another_event.configure(state="normal")
            self.textbox_printer_price.delete(0, "end")
            radio2_printer_type.focus_set()

        def select_date(event):
            date = cal.get_date()
            textbox_printer_event_date.configure(state="normal")
            textbox_printer_event_date.delete(0, "end")
            textbox_printer_event_date.insert(0, date)
            textbox_printer_event_date.configure(state="disable")

        def cancel_form():
            label_printer_name.configure(text_color="grey")
            combobox_printer_name.configure(state="normal")
            combobox_printer_name.set(value="-    název tiskárny  -")
            combobox_printer_name.configure(state="disable")
            selected_option.set(0)
            label_printer_cartridge.configure(text_color="grey")
            combobox_printer_cartridge.configure(state="disable")
            label_printer_another_event.configure(text_color="grey")
            combobox_printer_cartridge.configure(state="normal")
            combobox_printer_cartridge.set(value="-    seznam tonerů   -")
            combobox_printer_cartridge.configure(state="disable")
            textbox_printer_another_event.delete(0, "end")
            textbox_printer_another_event.configure(state="disable")
            self.textbox_printer_price.delete(0, "end")
            textbox_printer_event_date.configure(state="normal")
            textbox_printer_event_date.delete(0, "end")
            textbox_printer_event_date.insert(0, current_date)
            cal.selection_set(current_date)
            textbox_printer_event_date.configure(state="disable")
            button_printer_event_cancel.focus_set()

        def get_printer_names():
            connection = connection_db()
            cursor = connection.cursor()
            cursor.execute("""
                SELECT hardware_id, hardware_name, hardware_info
                FROM ITmanager_hardware
                WHERE hardware_type = 'Tiskárna'
            """)
            printers = cursor.fetchall()
            connection.close()

            formatted_printer_names = [
                {"id": hardware_id, "name": name, "info": info}
                for hardware_id, name, info in printers
            ]

            return formatted_printer_names

        def get_materials_for_printer(hardware_id):
            connection = connection_db()
            cursor = connection.cursor()
            cursor.execute("""
                SELECT printer_material_name, printer_material_price
                FROM ITmanager_printer_materials
                WHERE printer_material_printer_id = ?
            """, (hardware_id,))
            materials = cursor.fetchall()
            connection.close()

            return [(material[0], material[1]) for material in materials]  # Předpokládáme, že printer_material_name je prvním a jediným polem

        def on_printer_select(selected_printer):
            self.name_of_printer = selected_printer

            if selected_option.get() == 1:
                combobox_printer_cartridge.configure(state="normal")
                combobox_printer_cartridge.set(value="-    seznam tonerů   -")
                combobox_printer_cartridge.configure(state="readonly")

                selected_printer = combobox_printer_name.get()
                if selected_printer != "-    název tiskárny  -":
                    # Získání hardware_id z vybraného textu (předpokládáme, že hardware_id je součástí textu)
                    for printer in printer_names:
                        if f"{printer['name']} - ({printer['info']})" == selected_printer:
                            hardware_id = printer['id']
                            break

                    materials = get_materials_for_printer(hardware_id)
                    material_names = [material[0] for material in materials]
                    combobox_printer_cartridge.configure(values=material_names)
                    self.materials = dict(materials)  # Uložíme ceny tonerů do slovníku
                else:
                    combobox_printer_cartridge.configure(values=["-    seznam tonerů   -"])
                    self.materials = {}  # Nastavíme prázdný slovník pro materiály

            if selected_option.get() == 2:
                combobox_printer_cartridge.configure(state="normal")
                combobox_printer_cartridge.set(value="-    seznam tonerů   -")
                combobox_printer_cartridge.configure(state="disable")
                self.materials = {}  # Nastavíme prázdný slovník pro materiály

        def on_material_select(selected_material):
            price = self.materials.get(selected_material)  # Získání ceny z uloženého slovníku

            self.textbox_printer_price.delete(0, "end")
            if price is not None:
                self.textbox_printer_price.insert(0, str(price))
            else:
                self.textbox_printer_price.insert(0, "")

        def event_add():
            connection = connection_db()
            cursor = connection.cursor()

            if (selected_option.get() != 0 and combobox_printer_name.get().strip() != "-    název tiskárny  -"
                    and (combobox_printer_cartridge.get().strip() != "-    seznam tonerů   -" or textbox_printer_another_event.get().strip() != "")
                    and self.textbox_printer_price.get().strip() != ""):

                selected_printer = combobox_printer_name.get().strip()
                printer_id = None
                for printer in printer_names:
                    if f"{printer['name']} - ({printer['info']})" == selected_printer:
                        printer_id = printer['id']
                        break

                if selected_option.get() == 1:
                    printer_event_type = "Toner"
                elif selected_option.get() == 2:
                    printer_event_type = "Ostatní"

                if combobox_printer_cartridge.get().strip() == "-    seznam tonerů   -":
                    printer_event_material_name = "-"
                else:
                    printer_event_material_name = combobox_printer_cartridge.get().strip()

                if textbox_printer_another_event.get().strip() == "":
                    printer_event_other = "-"
                else:
                    printer_event_other = textbox_printer_another_event.get().strip()

                printer_event_price = self.textbox_printer_price.get().strip()
                printer_event_date = textbox_printer_event_date.get().strip()

                cursor.execute("""
                                INSERT INTO ITmanager_printer_events (printer_event_printer_id, printer_event_type, printer_event_material_name,
                                 printer_event_other, printer_event_price, printer_event_date)
                                VALUES (?, ?, ?, ?, ?, ?)
                                """, (printer_id, printer_event_type, printer_event_material_name, printer_event_other, printer_event_price, printer_event_date))
                connection.commit()
                cursor.close()
                connection.close()

                self.reset_row_colors()
                self.load_data()
                globals.printer_event.destroy()
                self.update_comboboxes()

                event_message_success("Info", "Nová událost tiskárny byla vytvořena.")
            else:
                event_message_error("Chyba!", "Nejsou vyplněna správně všechna pole. \nProsím zkontrolujte formulář.")


        # Main header
        label_header = ctk.CTkLabel(globals.printer_event, text="Přídání nové události tiskárny")
        label_header.configure(font=("Arial", 14, "bold"))
        label_header.pack(pady=(25,0), padx=(0,0))

        # Setting for type of printer event
        frame_printer_type = ctk.CTkFrame(globals.printer_event, fg_color="#242222")
        frame_printer_type.pack(pady=(25, 0), padx=(35, 0), anchor="w")

        label_printer_type = ctk.CTkLabel(frame_printer_type, text="Vyberte typ události")
        label_printer_type.configure(font=("Arial", 13, "bold"))
        label_printer_type.grid(row=1, column=0, pady=(0, 0), padx=(0, 0), sticky="w")



        radio1_printer_type = ctk.CTkRadioButton(frame_printer_type, text="výměna náplně do tiskárny",
                                                 command=printer_event_radio1,
                                                 variable=selected_option, radiobutton_width=17, radiobutton_height=17,
                                                 border_width_checked=5, value=1)
        radio1_printer_type.grid(row=2, column=0, pady=(15, 0), padx=(25, 0), sticky="w")

        radio2_printer_type = ctk.CTkRadioButton(frame_printer_type, text="jiná událost", command=printer_event_radio2,
                                                 variable=selected_option, radiobutton_width=17, radiobutton_height=17,
                                                 border_width_checked=5, value=2)
        radio2_printer_type.grid(row=2, column=1, pady=(15, 0), padx=(50, 0), sticky="w")


        # Settings for printer name
        frame_printer_name = ctk.CTkFrame(globals.printer_event, fg_color="#242222")
        frame_printer_name.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_printer_name = ctk.CTkLabel(frame_printer_name, text="Vyberte tiskárnu")
        label_printer_name.configure(font=("Arial", 13, "bold"), text_color="grey")
        label_printer_name.grid(row=0, column=0, pady=(0,0), padx=(0,0), sticky="w")

        printer_names = get_printer_names()
        combobox_values = ["-    název tiskárny  -"] + [f"{printer['name']} - ({printer['info']})"for printer in printer_names]
        combobox_printer_name = ctk.CTkComboBox(frame_printer_name, values=combobox_values, width=320, justify="center", command=on_printer_select)
        combobox_printer_name.configure(state="disable")
        combobox_printer_name.grid(row=0, column=1, pady=(0,0), padx=(65,0), sticky="w")


        # Settings for printer cartridge
        frame_printer_cartridge = ctk.CTkFrame(globals.printer_event, fg_color="#242222")
        frame_printer_cartridge.pack(pady=(30,0), padx=(35,0), anchor="w")

        label_printer_cartridge = ctk.CTkLabel(frame_printer_cartridge, text="Vyberte náplň tiskárny")
        label_printer_cartridge.configure(font=("Arial", 13, "bold"), text_color="grey")
        label_printer_cartridge.grid(row=3, column=0, pady=(0,0), padx=(0,0), sticky="w")

        combobox_printer_cartridge = ctk.CTkComboBox(frame_printer_cartridge, values=["-    seznam tonerů   -"], width=320, justify="center", command=on_material_select)
        combobox_printer_cartridge.configure(state="disable")
        combobox_printer_cartridge.grid(row=3, column=1, pady=(0,0), padx=(27,0), sticky="w")


        # Setting for another event
        frame_printer_another_event = ctk.CTkFrame(globals.printer_event, fg_color="#242222")
        frame_printer_another_event.pack(pady=(30,0), padx=(20,0), anchor="w")

        label_printer_another_event = ctk.CTkLabel(frame_printer_another_event, text="Zadej popis jiné události")
        label_printer_another_event.configure(font=("Arial", 13, "bold"), text_color="grey")
        label_printer_another_event.grid(row=4, column=0, pady=(0,0), padx=(15,0), sticky="w")

        textbox_printer_another_event = ctk.CTkEntry(frame_printer_another_event, width=200)
        textbox_printer_another_event.configure(state="disable")
        textbox_printer_another_event.grid(row=4, column=1, pady=(0,0), padx=(15,0), sticky="w")


        # Settings for price of event
        frame_printer_price = ctk.CTkFrame(globals.printer_event, fg_color="#242222")
        frame_printer_price.pack(pady=(15,0), padx=(35,0), anchor="w")

        label_printer_price = ctk.CTkLabel(frame_printer_price, text="Zadejte cenu události")
        label_printer_price.configure(font=("Arial", 13, "bold"))
        label_printer_price.grid(row=5, column="0", pady=(15,0), padx=(0,0), sticky="w")

        self.textbox_printer_price = ctk.CTkEntry(frame_printer_price, width=100)
        self.textbox_printer_price.grid(row=5, column="2", pady=(15,0), padx=(35,0), sticky="w")


        # Setting for date of event
        frame_printer_event_date = ctk.CTkFrame(globals.printer_event, fg_color="#242222")
        frame_printer_event_date.pack(pady=(15,0), padx=(35,0), anchor="w")

        label_printer_event_date = ctk.CTkLabel(frame_printer_event_date, text="Vyberte datum události")
        label_printer_event_date.configure(font=("Arial", 13, "bold"))
        label_printer_event_date.grid(row=6, column="0", pady=(0,0), padx=(0,0), sticky="w")

        cal = Calendar(frame_printer_event_date, selectmode="day", date_pattern="dd.mm.y", locale="cs_CZ", firstweekday="monday" )
        cal.grid(row=6, column=1, pady=(15,0), padx=(25,0))
        cal.bind("<<CalendarSelected>>", select_date)

        textbox_printer_event_date = ctk.CTkEntry(frame_printer_event_date, justify="center")
        textbox_printer_event_date.insert(0, current_date)
        textbox_printer_event_date.configure(state="disable")
        textbox_printer_event_date.grid(row=6, column=0, pady=(70,0))


        # Setting for buttons
        frame_printer_event_buttons = ctk.CTkFrame(globals.printer_event, fg_color="#242222")
        frame_printer_event_buttons.pack(pady=(15,0), padx=(35,0), anchor="w")

        button_printer_event_cancel = ctk.CTkButton(frame_printer_event_buttons, text="Storno", width=10, command=cancel_form)
        button_printer_event_cancel.configure(font=("Arial", 14, "bold"))
        button_printer_event_cancel.grid(row=7, column=0, pady=(15,0), padx=(369,0))

        button_printer_event_add = ctk.CTkButton(frame_printer_event_buttons, text="Uložit", width=10, command=event_add)
        button_printer_event_add.configure(font=("Arial", 14, "bold"))
        button_printer_event_add.grid(row=7, column=1, pady=(15,0), padx=(10,0))

















