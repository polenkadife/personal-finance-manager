import customtkinter as ctk
from gui import FinanceApp
from finance_manager import FinanceManager
from database import Database

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # "light" veya "dark" tema
    ctk.set_default_color_theme("blue")  # Tema rengi
    root = ctk.CTk()
    db = Database("finance.db")
    finance_manager = FinanceManager(db)
    app = FinanceApp(root, finance_manager)
    root.mainloop()