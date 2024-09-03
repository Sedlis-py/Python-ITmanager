import customtkinter as ctk

class Hardware_end_devices_pc_frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.label = ctk.CTkLabel(self, text="Přehled všech PC/nb")
        self.label.pack(pady=20)