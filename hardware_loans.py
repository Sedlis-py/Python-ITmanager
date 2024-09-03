import customtkinter as ctk

class Hardware_loans_frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.label = ctk.CTkLabel(self, text="Hardware zápůjčky")
        self.label.pack(pady=20)