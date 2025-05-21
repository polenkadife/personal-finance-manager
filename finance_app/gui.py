import customtkinter as ctk
import webbrowser
import json
import os
from datetime import datetime
from tkcalendar import Calendar
import logging

# Hata günlüğünü yapılandır
logging.basicConfig(
    level=logging.INFO,
    filename="finance_app.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

class FinanceApp:
    def __init__(self, root, finance_manager):
        """Uygulamanın ana GUI sınıfı."""
        self.root = root
        self.finance_manager = finance_manager
        self.selected_transactions = []
        self.warning_window = None

        # Pencere ayarları
        self.root.title("Kişisel Finans Takip")
        self.root.geometry("1000x750")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.root.configure(bg="#212121")

        # Ana çerçeve
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=12, fg_color="#2B2B2B")
        self.main_frame.pack(pady=15, padx=15, fill="both", expand=True)

        # Roboto yazı tipi
        try:
            self.font = ctk.CTkFont(family="Roboto", size=14)
        except:
            logging.warning("Roboto yazı tipi bulunamadı, varsayılan kullanılacak.")
            self.font = ctk.CTkFont(size=14)

        # UI bileşenleri
        self._create_header()
        self._create_budget_form()
        self._create_input_form()
        self._create_transaction_list()
        self._create_filter_and_summary()

        # Başlangıç güncellemeleri
        self.update_transaction_list()
        self._check_budget_exceedance()

    def _create_header(self):
        """Başlık oluşturur."""
        ctk.CTkLabel(
            self.main_frame,
            text="💰 Kişisel Finans Yönetimi",
            font=ctk.CTkFont(family="Roboto", size=26, weight="bold"),
            text_color="#FFFFFF"
        ).pack(pady=15)

    def _create_budget_form(self):
        """Bütçe formunu oluşturur."""
        frame = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color="#333333")
        frame.pack(pady=10, padx=10, fill="x")

        # Yıl
        ctk.CTkLabel(frame, text="📅 Yıl:", font=self.font).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.budget_year_var = ctk.StringVar(value=str(datetime.now().year))
        ctk.CTkEntry(
            frame,
            textvariable=self.budget_year_var,
            width=100,
            corner_radius=8,
            placeholder_text="YYYY",
            font=self.font
        ).grid(row=0, column=1, padx=15, pady=10)

        # Ay
        ctk.CTkLabel(frame, text="🗓️ Ay:", font=self.font).grid(row=0, column=2, padx=15, pady=10, sticky="w")
        self.budget_month_var = ctk.StringVar(value=datetime.now().strftime("%m"))
        ctk.CTkOptionMenu(
            frame,
            values=[f"{i:02d}" for i in range(1, 13)],
            variable=self.budget_month_var,
            corner_radius=8,
            button_color="#0288D1",
            button_hover_color="#01579B",
            font=self.font
        ).grid(row=0, column=3, padx=15, pady=10)

        # Bütçe miktarı
        ctk.CTkLabel(frame, text="💸 Bütçe (TL):", font=self.font).grid(row=0, column=4, padx=15, pady=10, sticky="w")
        self.budget_amount_entry = ctk.CTkEntry(
            frame,
            corner_radius=8,
            width=140,
            placeholder_text="Miktar girin",
            font=self.font
        )
        self.budget_amount_entry.grid(row=0, column=5, padx=15, pady=10)

        # Mevcut bütçe
        self.budget_display = ctk.CTkLabel(
            frame,
            text="ℹ️ Mevcut Bütçe: -",
            font=ctk.CTkFont(size=12),
            text_color="#B0BEC5"
        )
        self.budget_display.grid(row=1, column=0, columnspan=6, padx=15, pady=10)

        # Butonlar
        ctk.CTkButton(
            frame,
            text="🔍 Bütçeyi Kontrol Et",
            command=self._check_budget,
            corner_radius=8,
            fg_color="#0288D1",
            hover_color="#01579B",
            font=self.font,
            width=160
        ).grid(row=0, column=6, padx=15, pady=10)
        ctk.CTkButton(
            frame,
            text="💾 Bütçeyi Kaydet",
            command=self._save_budget,
            corner_radius=8,
            fg_color="#43A047",
            hover_color="#2E7D32",
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            width=160
        ).grid(row=0, column=7, padx=15, pady=10)

    def _check_budget(self):
        """Bütçeyi kontrol eder."""
        try:
            year = self.budget_year_var.get()
            month = self.budget_month_var.get()
            budget = self.finance_manager.get_budget(year, month)
            self.budget_display.configure(
                text=f"ℹ️ Mevcut Bütçe: {budget:.2f} TL" if budget else "ℹ️ Mevcut Bütçe: Tanımlı değil"
            )
            self.budget_amount_entry.delete(0, "end")
            if budget:
                self.budget_amount_entry.insert(0, f"{budget:.2f}")
        except ValueError:
            self._show_error("Geçerli bir yıl girin!")

    def _save_budget(self):
        """Bütçeyi kaydeder."""
        try:
            year = int(self.budget_year_var.get())
            month = self.budget_month_var.get()
            amount = float(self.budget_amount_entry.get())
            if amount <= 0:
                raise ValueError("Bütçe pozitif olmalı!")
            self.finance_manager.set_budget(year, month, amount)
            self.budget_amount_entry.delete(0, "end")
            self._check_budget()
            self._check_budget_exceedance()
            self._show_info("Bütçe başarıyla kaydedildi.")
        except ValueError as e:
            self._show_error(str(e))

    def _create_input_form(self):
        """İşlem ekleme formunu oluşturur."""
        frame = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color="#333333")
        frame.pack(pady=10, padx=10, fill="x")

        # Tür
        ctk.CTkLabel(frame, text="📋 Tür:", font=self.font).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.type_var = ctk.StringVar(value="Gelir")
        ctk.CTkOptionMenu(
            frame,
            values=["Gelir", "Gider"],
            variable=self.type_var,
            corner_radius=8,
            button_color="#0288D1",
            button_hover_color="#01579B",
            font=self.font
        ).grid(row=0, column=1, padx=15, pady=10)

        # Miktar
        ctk.CTkLabel(frame, text="💰 Miktar:", font=self.font).grid(row=0, column=2, padx=15, pady=10, sticky="w")
        self.amount_entry = ctk.CTkEntry(
            frame,
            corner_radius=8,
            width=140,
            placeholder_text="Miktar girin",
            font=self.font
        )
        self.amount_entry.grid(row=0, column=3, padx=15, pady=10)

        # Kategori
        ctk.CTkLabel(frame, text="🏷️ Kategori:", font=self.font).grid(row=0, column=4, padx=15, pady=10, sticky="w")
        self.category_var = ctk.StringVar(value=self.finance_manager.get_categories()[0])
        self.category_menu = ctk.CTkOptionMenu(
            frame,
            values=self.finance_manager.get_categories(),
            variable=self.category_var,
            corner_radius=8,
            button_color="#0288D1",
            button_hover_color="#01579B",
            font=self.font
        )
        self.category_menu.grid(row=0, column=5, padx=15, pady=10)

        # Tarih
        ctk.CTkLabel(frame, text="📅 Tarih:", font=self.font).grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.date_entry = ctk.CTkEntry(
            frame,
            corner_radius=8,
            width=140,
            placeholder_text="YYYY-MM-DD",
            font=self.font
        )
        self.date_entry.grid(row=1, column=1, padx=15, pady=10)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Takvim butonu
        ctk.CTkButton(
            frame,
            text="📅",
            width=40,
            command=self._open_calendar,
            corner_radius=8,
            fg_color="#0288D1",
            hover_color="#01579B",
            font=self.font
        ).grid(row=1, column=2, padx=(0, 15), pady=10, sticky="w")

        # Açıklama
        ctk.CTkLabel(frame, text="📝 Açıklama:", font=self.font).grid(row=1, column=3, padx=15, pady=10, sticky="w")
        self.desc_entry = ctk.CTkEntry(
            frame,
            corner_radius=8,
            width=350,
            placeholder_text="Açıklama girin",
            font=self.font
        )
        self.desc_entry.grid(row=1, column=4, columnspan=2, padx=15, pady=10, sticky="ew")

        # Ekle butonu
        ctk.CTkButton(
            frame,
            text="➕ Ekle",
            command=self.add_transaction,
            corner_radius=8,
            fg_color="#43A047",
            hover_color="#2E7D32",
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            width=160
        ).grid(row=2, column=4, columnspan=2, padx=15, pady=10)

    def _open_calendar(self):
        """Takvim açar."""
        top = ctk.CTkToplevel(self.root)
        top.title("Tarih Seç")
        top.geometry("300x300")
        top.transient(self.root)
        top.grab_set()

        cal = Calendar(
            top,
            selectmode="day",
            date_pattern="yyyy-mm-dd",
            font=("Roboto", 12),
            background="#0288D1",
            foreground="white"
        )
        cal.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkButton(
            top,
            text="✔️ Seç",
            command=lambda: self._set_date(cal.get_date(), top),
            corner_radius=8,
            fg_color="#43A047",
            hover_color="#2E7D32",
            font=self.font
        ).pack(pady=10)

    def _set_date(self, date, window):
        """Tarihi günceller."""
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, date)
        window.destroy()

    def _create_transaction_list(self):
        """İşlem listesi oluşturur."""
        self.list_frame = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color="#333333")
        self.list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.scrollable_frame = ctk.CTkScrollableFrame(self.list_frame, corner_radius=10, fg_color="#2B2B2B")
        self.scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.transaction_frames = []

        ctk.CTkButton(
            self.list_frame,
            text="🗑️ Seçilenleri Sil",
            command=self.delete_selected,
            corner_radius=8,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            width=160
        ).pack(pady=10)

    def _create_filter_and_summary(self):
        """Filtre ve özet alanı oluşturur."""
        frame = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color="#333333")
        frame.pack(pady=10, padx=10, fill="x")

        # Kategori filtresi
        ctk.CTkLabel(frame, text="🏷️ Kategori:", font=self.font).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.filter_category_var = ctk.StringVar(value="Tümü")
        ctk.CTkOptionMenu(
            frame,
            values=["Tümü"] + self.finance_manager.get_categories(),
            variable=self.filter_category_var,
            command=self.update_transaction_list,
            corner_radius=8,
            button_color="#0288D1",
            button_hover_color="#01579B",
            font=self.font
        ).grid(row=0, column=1, padx=15, pady=10)

        # Yıl filtresi
        ctk.CTkLabel(frame, text="📅 Yıl:", font=self.font).grid(row=0, column=2, padx=15, pady=10, sticky="w")
        self.filter_year_var = ctk.StringVar(value="Tümü")
        self.filter_year_menu = ctk.CTkOptionMenu(
            frame,
            values=["Tümü"] + self.get_available_years(),
            variable=self.filter_year_var,
            command=self.update_transaction_list,
            corner_radius=8,
            button_color="#0288D1",
            button_hover_color="#01579B",
            font=self.font
        )
        self.filter_year_menu.grid(row=0, column=3, padx=15, pady=10)

        # Ay filtresi
        ctk.CTkLabel(frame, text="🗓️ Ay:", font=self.font).grid(row=0, column=4, padx=15, pady=10, sticky="w")
        self.filter_month_var = ctk.StringVar(value="Tümü")
        self.filter_month_menu = ctk.CTkOptionMenu(
            frame,
            values=["Tümü"] + [f"{i:02d}" for i in range(1, 13)],
            variable=self.filter_month_var,
            command=self.update_transaction_list,
            corner_radius=8,
            button_color="#0288D1",
            button_hover_color="#01579B",
            font=self.font
        )
        self.filter_month_menu.grid(row=0, column=5, padx=15, pady=10)

        # Butonlar
        ctk.CTkButton(
            frame,
            text="📊 Özeti Görüntüle",
            command=self.show_summary,
            corner_radius=8,
            fg_color="#43A047",
            hover_color="#2E7D32",
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            width=160
        ).grid(row=0, column=6, padx=15, pady=10)
        ctk.CTkButton(
            frame,
            text="📈 Grafik Görüntüle",
            command=self.show_chart_dialog,
            corner_radius=8,
            fg_color="#43A047",
            hover_color="#2E7D32",
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            width=160
        ).grid(row=0, column=7, padx=15, pady=10)
        ctk.CTkButton(
            frame,
            text="📋 Bütçe Raporu",
            command=self.show_budget_report,
            corner_radius=8,
            fg_color="#43A047",
            hover_color="#2E7D32",
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            width=160
        ).grid(row=0, column=8, padx=15, pady=10)

    def get_available_years(self):
        """Mevcut yılları alır."""
        transactions = self.finance_manager.get_transactions()
        years = set()
        for t in transactions:
            try:
                date = datetime.strptime(t[4].split(" ")[0], "%Y-%m-%d")
                years.add(date.year)
            except ValueError:
                continue
        current_year = datetime.now().year
        return sorted([str(y) for y in set(years).union(set(range(current_year, current_year + 5)))])

    def add_transaction(self):
        """İşlem ekler."""
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError("Miktar pozitif olmalı!")
            type_ = self.type_var.get()
            category = self.category_var.get()
            description = self.desc_entry.get()
            date = self.date_entry.get()
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Geçerli bir tarih girin (YYYY-MM-DD)!")

            self.finance_manager.add_transaction(type_, amount, category, date, description)
            self.update_transaction_list()
            self._update_category_menu()
            self._update_year_menu()
            self.amount_entry.delete(0, "end")
            self.desc_entry.delete(0, "end")
            self._check_budget_exceedance()
            self._show_info("İşlem başarıyla eklendi.")
        except ValueError as e:
            self._show_error(str(e))

    def update_transaction_list(self, *args):
        """İşlem listesini günceller."""
        for frame in self.transaction_frames:
            frame.destroy()
        self.transaction_frames.clear()
        self.selected_transactions.clear()

        category = self.filter_category_var.get() if self.filter_category_var.get() != "Tümü" else None
        year = self.filter_year_var.get() if self.filter_year_var.get() != "Tümü" else None
        month = self.filter_month_var.get() if self.filter_month_var.get() != "Tümü" else None
        transactions = self.finance_manager.get_transactions(category=category, year=year, month=month)

        category_colors = {
            "Maaş": "#4CAF50", "Kira": "#0288D1", "Yiyecek": "#FF9800",
            "Eğlence": "#E91E63", "Diğer": "#757575", "Faturalar": "#2196F3",
            "Ulaşım": "#FF5722", "Sağlık": "#009688", "Eğitim": "#673AB7",
            "Alışveriş": "#F44336", "Yatırım": "#4DB6AC", "Borç": "#D81B60",
            "Kredi Kartı": "#AB47BC", "Kişisel Bakım": "#26A69A", "Ev Bakımı": "#FFCA28"
        }

        for t in transactions:
            frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=8, fg_color="#424242")
            frame.pack(pady=5, padx=10, fill="x")

            checkbox_var = ctk.BooleanVar(value=False)
            ctk.CTkCheckBox(
                frame,
                text="",
                variable=checkbox_var,
                command=lambda id=t[0], var=checkbox_var: self._toggle_selection(id, var)
            ).pack(side="left", padx=10)

            # Kategori etiketi
            ctk.CTkLabel(
                frame,
                text=t[3],
                font=ctk.CTkFont(size=12),
                text_color=category_colors.get(t[3], "#FFFFFF"),
                width=80,
                anchor="w"
            ).pack(side="left", padx=5)

            # İşlem satırı: 💵 Gelir ⬆️ veya 💸 Gider ⬇️
            type_icon = "💵" if t[1] == "Gelir" else "💸"
            type_arrow = "⬆️" if t[1] == "Gelir" else "⬇️"
            text = f"{type_icon} {t[1]} {type_arrow} {t[2]:.2f} TL | {t[4]} | {t[5] or ''}"
            ctk.CTkLabel(
                frame,
                text=text,
                font=ctk.CTkFont(size=12),
                anchor="w"
            ).pack(pady=5, padx=10, fill="x")

            self.transaction_frames.append(frame)

        self._check_budget_exceedance()

    def _toggle_selection(self, id_, var):
        """İşlem seçimini günceller."""
        if var.get():
            if id_ not in self.selected_transactions:
                self.selected_transactions.append(id_)
        else:
            if id_ in self.selected_transactions:
                self.selected_transactions.remove(id_)

    def _update_category_menu(self):
        """Kategori menüsünü günceller."""
        categories = ["Tümü"] + self.finance_manager.get_categories()
        self.category_menu.configure(values=self.finance_manager.get_categories())
        self.filter_category_var.set("Tümü")
        self.category_menu.configure(values=categories)

    def _update_year_menu(self):
        """Yıl menüsünü günceller."""
        years = ["Tümü"] + self.get_available_years()
        self.filter_year_var.set("Tümü")
        self.filter_year_menu.configure(values=years)

    def delete_selected(self):
        """Seçili işlemleri siler."""
        if not self.selected_transactions:
            self._show_warning("Silmek için işlem seçin!")
            return
        for id_ in self.selected_transactions:
            self.finance_manager.delete_transaction(id_)
        self.update_transaction_list()
        self._check_budget_exceedance()

    def show_summary(self):
        """Özet tablosu gösterir."""
        year = self.filter_year_var.get() if self.filter_year_var.get() != "Tümü" else None
        month = self.filter_month_var.get() if self.filter_month_var.get() != "Tümü" else None
        summary = self.finance_manager.generate_summary(year, month)

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Finansal Özet")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(fg_color="#212121")

        frame = ctk.CTkFrame(dialog, corner_radius=12, fg_color="#333333")
        frame.pack(pady=10, padx=10, fill="both", expand=True)

        headers = ["Dönem", "Gelir", "Gider"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(
                frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#FFFFFF"
            ).grid(row=0, column=col, padx=10, pady=5)

        if not summary.empty:
            for row, (index, data) in enumerate(summary.iterrows(), 1):
                ctk.CTkLabel(
                    frame,
                    text=str(index),
                    font=ctk.CTkFont(size=12)
                ).grid(row=row, column=0, padx=10, pady=2)
                ctk.CTkLabel(
                    frame,
                    text=f"{float(data.get('Gelir', 0)):.2f} TL",
                    font=ctk.CTkFont(size=12)
                ).grid(row=row, column=1, padx=10, pady=2)
                ctk.CTkLabel(
                    frame,
                    text=f"{float(data.get('Gider', 0)):.2f} TL",
                    font=ctk.CTkFont(size=12)
                ).grid(row=row, column=2, padx=10, pady=2)
        else:
            ctk.CTkLabel(
                frame,
                text="Veri bulunamadı.",
                font=ctk.CTkFont(size=12),
                text_color="#B0BEC5"
            ).grid(row=1, column=0, columnspan=3, pady=10)

        ctk.CTkButton(
            dialog,
            text="❌ Kapat",
            command=dialog.destroy,
            corner_radius=8,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            font=self.font
        ).pack(pady=10)

    def show_budget_report(self):
        """Bütçe raporunu gösterir."""
        year = self.filter_year_var.get() if self.filter_year_var.get() != "Tümü" else None
        month = self.filter_month_var.get() if self.filter_month_var.get() != "Tümü" else None
        report_data = self.finance_manager.get_budget_report(year, month)

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Bütçe Raporu")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(fg_color="#212121")

        frame = ctk.CTkFrame(dialog, corner_radius=12, fg_color="#333333")
        frame.pack(pady=10, padx=10, fill="both", expand=True)

        headers = ["Dönem", "Bütçe (TL)", "Gider (TL)", "Kalan (TL)"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(
                frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#FFFFFF"
            ).grid(row=0, column=col, padx=10, pady=5)

        if report_data:
            for row, (period, budget, expense, remaining) in enumerate(report_data, 1):
                ctk.CTkLabel(
                    frame,
                    text=period,
                    font=ctk.CTkFont(size=12)
                ).grid(row=row, column=0, padx=10, pady=2)
                ctk.CTkLabel(
                    frame,
                    text=f"{budget:.2f}",
                    font=ctk.CTkFont(size=12)
                ).grid(row=row, column=1, padx=10, pady=2)
                ctk.CTkLabel(
                    frame,
                    text=f"{expense:.2f}",
                    font=ctk.CTkFont(size=12)
                ).grid(row=row, column=2, padx=10, pady=2)
                ctk.CTkLabel(
                    frame,
                    text=f"{remaining:.2f}",
                    font=ctk.CTkFont(size=12)
                ).grid(row=row, column=3, padx=10, pady=2)
        else:
            ctk.CTkLabel(
                frame,
                text="Veri bulunamadı.",
                font=ctk.CTkFont(size=12),
                text_color="#B0BEC5"
            ).grid(row=1, column=0, columnspan=4, pady=10)

        ctk.CTkButton(
            dialog,
            text="❌ Kapat",
            command=dialog.destroy,
            corner_radius=8,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            font=self.font
        ).pack(pady=10)

    def show_chart_dialog(self):
        """Grafik seçimi penceresi açar."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Grafik Türü Seç")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(fg_color="#212121")

        ctk.CTkLabel(
            dialog,
            text="📊 Görmek istediğiniz grafiği seçin:",
            font=self.font,
            text_color="#FFFFFF"
        ).pack(pady=20)

        ctk.CTkButton(
            dialog,
            text="📈 Gelir Dağılımı",
            command=lambda: self._show_chart("Gelir"),
            corner_radius=8,
            fg_color="#43A047",
            hover_color="#2E7D32",
            font=self.font
        ).pack(pady=10)
        ctk.CTkButton(
            dialog,
            text="📉 Gider Dağılımı",
            command=lambda: self._show_chart("Gider"),
            corner_radius=8,
            fg_color="#43A047",
            hover_color="#2E7D32",
            font=self.font
        ).pack(pady=10)
        ctk.CTkButton(
            dialog,
            text="📊 Gelir ve Gider",
            command=lambda: self._show_chart("Both"),
            corner_radius=8,
            fg_color="#43A047",
            hover_color="#2E7D32",
            font=self.font
        ).pack(pady=10)

    def _show_chart(self, chart_type):
        """Grafiği tarayıcıda açar."""
        try:
            chart_file = "chart.html"
            if os.path.exists(chart_file):
                os.remove(chart_file)

            year = self.filter_year_var.get() if self.filter_year_var.get() != "Tümü" else None
            month = self.filter_month_var.get() if self.filter_month_var.get() != "Tümü" else None
            chart_data = self.finance_manager.generate_chart_data(chart_type, year, month)
            with open(chart_file, "w", encoding="utf-8") as f:
                f.write(f"""
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>{chart_type} Dağılımı</title>
                    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
                    <style>
                        #myChart {{ max-width: 600px; max-height: 400px; margin: 20px auto; }}
                        #error {{ color: red; text-align: center; margin-top: 20px; }}
                    </style>
                </head>
                <body>
                    <canvas id="myChart"></canvas>
                    <div id="error" style="display: none;">Grafik yüklenemedi.</div>
                    <script>
                        try {{
                            const ctx = document.getElementById('myChart').getContext('2d');
                            new Chart(ctx, {json.dumps(chart_data, ensure_ascii=False)});
                        }} catch (e) {{
                            document.getElementById('error').style.display = 'block';
                            console.error('Grafik hatası:', e);
                        }}
                    </script>
                </body>
                </html>
                """)
            webbrowser.open(f"file://{os.path.abspath(chart_file)}")
        except Exception as e:
            self._show_error(f"Grafik oluşturulamadı: {str(e)}")

    def _check_budget_exceedance(self):
        """Bütçe aşımını kontrol eder."""
        if self.warning_window:
            self.warning_window.destroy()
            self.warning_window = None

        year = self.filter_year_var.get() if self.filter_year_var.get() != "Tümü" else str(datetime.now().year)
        month = self.filter_month_var.get() if self.filter_month_var.get() != "Tümü" else datetime.now().strftime("%m")
        budget = self.finance_manager.get_budget(year, month)
        if not budget:
            return

        transactions = self.finance_manager.get_transactions(type="Gider", year=year, month=month)
        total_expense = sum(t[2] for t in transactions)
        if total_expense > budget:
            self.warning_window = ctk.CTkToplevel(self.root)
            self.warning_window.title("Dikkat")
            self.warning_window.geometry("400x150")
            self.warning_window.transient(self.root)
            self.warning_window.grab_set()
            self.warning_window.configure(fg_color="#212121")

            ctk.CTkLabel(
                self.warning_window,
                text=f"⚠️ UYARI: {year}-{month} bütçesi aşıldı! ({total_expense:.2f} TL / {budget:.2f} TL)",
                text_color="#EF5350",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(pady=20)

            ctk.CTkButton(
                self.warning_window,
                text="✔️ Tamam",
                command=self.warning_window.destroy,
                corner_radius=8,
                fg_color="#43A047",
                hover_color="#2E7D32",
                font=self.font
            ).pack(pady=10)

    def _show_error(self, message):
        """Hata mesajı gösterir."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Hata")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(fg_color="#212121")
        ctk.CTkLabel(
            dialog,
            text=f"❌ {message}",
            text_color="#EF5350",
            font=self.font
        ).pack(pady=20)
        ctk.CTkButton(
            dialog,
            text="✔️ Tamam",
            command=dialog.destroy,
            corner_radius=8,
            fg_color="#43A047",
            hover_color="#2E7D32",
            font=self.font
        ).pack(pady=10)

    def _show_warning(self, message):
        """Uyarı mesajı gösterir."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Uyarı")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(fg_color="#212121")
        ctk.CTkLabel(
            dialog,
            text=f"⚠️ {message}",
            text_color="#FFCA28",
            font=self.font
        ).pack(pady=20)
        ctk.CTkButton(
            dialog,
            text="✔️ Tamam",
            command=dialog.destroy,
            corner_radius=8,
            fg_color="#43A047",
            hover_color="#2E7D32",
            font=self.font
        ).pack(pady=10)

    def _show_info(self, message):
        """Bilgi mesajı gösterir."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Bilgi")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(fg_color="#212121")
        ctk.CTkLabel(
            dialog,
            text=f"✅ {message}",
            text_color="#4CAF50",
            font=self.font
        ).pack(pady=20)
        ctk.CTkButton(
            dialog,
            text="✔️ Tamam",
            command=dialog.destroy,
            corner_radius=8,
            fg_color="#43A047",
            hover_color="#2E7D32",
            font=self.font
        ).pack(pady=10)