import customtkinter as ctk

class Software_user_cal_frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.label = ctk.CTkLabel(self, text="User CAL licence")
        self.label.pack(pady=20)