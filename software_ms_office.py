import customtkinter as ctk

class Software_ms_office_frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.label = ctk.CTkLabel(self, text="Microsoft Office licence")
        self.label.pack(pady=20)