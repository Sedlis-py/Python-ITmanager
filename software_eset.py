import customtkinter as ctk

class Software_eset_frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.label = ctk.CTkLabel(self, text="Eset licence")
        self.label.pack(pady=20)