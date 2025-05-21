import pandas as pd
import json
import os
from datetime import datetime

class FinanceManager:
    def __init__(self, db):
        self.db = db
        categories = [
            "Maaş", "Kira", "Yiyecek", "Eğlence", "Ev Bakımı",
            "Faturalar", "Ulaşım", "Sağlık", "Eğitim", "Alışveriş",
            "Yatırım", "Borç", "Kredi Kartı", "Kişisel Bakım", "Diğer"
        ]
        for cat in categories:
            self.db.add_category(cat)

    def add_transaction(self, type, amount, category, date, description):
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            date = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("Tarih formatı YYYY-MM-DD olmalı!")
        self.db.add_transaction(type, amount, category, date, description)

    def delete_transaction(self, id):
        self.db.delete_transaction(id)

    def get_transactions(self, category=None, type=None, year=None, month=None):
        transactions = self.db.get_transactions(category=category, type=type)
        if year or month:
            filtered = []
            for t in transactions:
                try:
                    date_str = t[4]
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                    if year and str(date.year) != year:
                        continue
                    if month and date.month != int(month):
                        continue
                    filtered.append(t)
                except ValueError:
                    continue
            return filtered
        return transactions

    def get_categories(self):
        return self.db.get_categories()

    def set_budget(self, year, month, amount):
        self.db.set_budget(year, month, amount)

    def get_budget(self, year, month):
        return self.db.get_budget(year, month)

    def get_budget_report(self, year=None, month=None):
        """Bütçe ve gider raporunu döndürür."""
        transactions = self.get_transactions(type="Gider", year=year, month=month)
        df = pd.DataFrame(transactions, columns=["id", "type", "amount", "category", "date", "description"])
        if df.empty:
            return []

        def parse_date(date_str):
            try:
                return pd.to_datetime(date_str, format="%Y-%m-%d")
            except ValueError:
                return pd.NaT

        df["date"] = df["date"].apply(parse_date)
        df = df.dropna(subset=["date"])
        df["month"] = df["date"].dt.to_period("M")
        expense_summary = df.groupby("month")["amount"].sum().reset_index()
        report = []
        for _, row in expense_summary.iterrows():
            period = str(row["month"])
            y, m = period.split("-")
            budget = self.get_budget(y, m.zfill(2)) or 0.0
            expense = float(row["amount"])
            remaining = budget - expense
            report.append((period, budget, expense, remaining))
        return sorted(report, key=lambda x: x[0])

    def generate_summary(self, year=None, month=None):
        transactions = self.get_transactions(year=year, month=month)
        df = pd.DataFrame(transactions, columns=["id", "type", "amount", "category", "date", "description"])
        if df.empty:
            return pd.DataFrame(columns=["Gelir", "Gider"])

        def parse_date(date_str):
            try:
                return pd.to_datetime(date_str, format="%Y-%m-%d")
            except ValueError:
                return pd.NaT

        df["date"] = df["date"].apply(parse_date)
        df = df.dropna(subset=["date"])
        df["month"] = df["date"].dt.to_period("M")
        summary = df.groupby(["month", "type"])["amount"].sum().unstack().fillna(0)
        return summary

    def generate_chart_data(self, chart_type, year=None, month=None):
        if chart_type == "Both":
            transactions = self.get_transactions(year=year, month=month)
        else:
            transactions = self.get_transactions(type=chart_type, year=year, month=month)

        df = pd.DataFrame(transactions, columns=["id", "type", "amount", "category", "date", "description"])
        if df.empty:
            return {
                "type": "pie",
                "data": {
                    "labels": ["Veri Yok"],
                    "datasets": [{
                        "label": "Dağılım",
                        "data": [1],
                        "backgroundColor": ["#CCCCCC"],
                        "borderColor": ["#FFFFFF"],
                        "borderWidth": 1
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "legend": {"position": "top"},
                        "tooltip": {"enabled": False},
                        "centerText": {"display": False}
                    }
                }
            }

        category_totals = df.groupby("category")["amount"].sum().reset_index()
        labels = category_totals["category"].tolist()
        data = category_totals["amount"].tolist()
        total = sum(data)
        colors = [
            "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF",
            "#FF9F40", "#E57373", "#81C784", "#64B5F6", "#FFD54F",
            "#4DD0E1", "#9575CD", "#F06292", "#AED581", "#4FC3F7"
        ]

        return {
            "type": "pie",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": f"{chart_type} Dağılımı",
                    "data": data,
                    "backgroundColor": colors[:len(labels)],
                    "borderColor": ["#FFFFFF"] * len(labels),
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"position": "top"},
                    "tooltip": {
                        "enabled": True,
                        "callbacks": {
                            "label": """function(context) {
                                let label = context.label || '';
                                let value = context.parsed || 0;
                                let total = context.dataset.data.reduce((a, b) => a + b, 0);
                                let percentage = total ? ((value / total) * 100).toFixed(2) : 0;
                                return `${label}: ${value.toFixed(2)} TL (${percentage}%)`;
                            }"""
                        }
                    },
                    "centerText": {
                        "display": True,
                        "text": f"Toplam: {total:.2f} TL"
                    }
                }
            },
            "plugins": [{
                "id": "centerText",
                "beforeDraw": """function(chart) {
                    if (chart.options.plugins.centerText.display) {
                        let ctx = chart.ctx;
                        let width = chart.width;
                        let height = chart.height;
                        ctx.save();
                        ctx.font = 'bold 16px Arial';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillStyle = '#FFFFFF';
                        ctx.fillText(chart.options.plugins.centerText.text, width / 2, height / 2);
                        ctx.restore();
                    }
                }"""
            }]
        }