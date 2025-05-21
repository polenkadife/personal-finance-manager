import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                month TEXT NOT NULL,
                amount REAL NOT NULL,
                UNIQUE(year, month)
            )
        ''')
        self.conn.commit()

    def add_transaction(self, type, amount, category, date, description):
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            date = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("Tarih formatı YYYY-MM-DD olmalı!")
        self.cursor.execute('''
            INSERT INTO transactions (type, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (type, amount, category, date, description))
        self.conn.commit()

    def delete_transaction(self, id):
        self.cursor.execute("DELETE FROM transactions WHERE id = ?", (id,))
        self.conn.commit()

    def get_transactions(self, category=None, type=None):
        query = "SELECT * FROM transactions"
        params = []
        conditions = []
        if category:
            conditions.append("category = ?")
            params.append(category)
        if type:
            conditions.append("type = ?")
            params.append(type)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_categories(self):
        self.cursor.execute("SELECT name FROM categories")
        return [row[0] for row in self.cursor.fetchall()]

    def add_category(self, name):
        try:
            self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    def set_budget(self, year, month, amount):
        self.cursor.execute('''
            INSERT OR REPLACE INTO budgets (year, month, amount)
            VALUES (?, ?, ?)
        ''', (year, month, amount))
        self.conn.commit()

    def get_budget(self, year, month):
        self.cursor.execute("SELECT amount FROM budgets WHERE year = ? AND month = ?", (year, month))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def close(self):
        self.conn.close()