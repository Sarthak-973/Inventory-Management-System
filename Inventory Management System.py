import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv

# Database setup
def init_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    category TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Functions for database operations
def add_product(name, quantity, price, category):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()

    # Find the lowest unused ID
    c.execute("SELECT id FROM products ORDER BY id")
    used_ids = [row[0] for row in c.fetchall()]
    new_id = 1
    for uid in used_ids:
        if uid == new_id:
            new_id += 1
        else:
            break

    # Insert with chosen ID
    c.execute("INSERT INTO products (id, name, quantity, price, category) VALUES (?, ?, ?, ?, ?)",
              (new_id, name, quantity, price, category))
    conn.commit()
    conn.close()

def update_product(product_id, name, quantity, price, category):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("""UPDATE products SET name=?, quantity=?, price=?, category=? WHERE id=?""",
              (name, quantity, price, category, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

def fetch_products():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    rows = c.fetchall()
    conn.close()
    return rows

def search_products(keyword):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE name LIKE ? OR category LIKE ?", ('%'+keyword+'%', '%'+keyword+'%'))
    rows = c.fetchall()
    conn.close()
    return rows

def export_to_csv():
    products = fetch_products()
    if not products:
        messagebox.showinfo("Info", "No data to export")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")])
    if file_path:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Name", "Quantity", "Price", "Category"])
            writer.writerows(products)
        messagebox.showinfo("Success", "Data exported successfully")

# GUI setup
class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.configure(bg='#e0f7fa')

        self.name_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.search_var = tk.StringVar()

        frame = tk.Frame(root, bg='#b2ebf2', padx=10, pady=10, bd=2, relief='groove')
        frame.pack(pady=10)

        tk.Label(frame, text="Product Name", bg='#b2ebf2', font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(frame, textvariable=self.name_var, width=25).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Quantity", bg='#b2ebf2', font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(frame, textvariable=self.quantity_var, width=25).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Price", bg='#b2ebf2', font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(frame, textvariable=self.price_var, width=25).grid(row=2, column=1, padx=5, pady=5)

        tk.Label(frame, text="Category", bg='#b2ebf2', font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(frame, textvariable=self.category_var, width=25).grid(row=3, column=1, padx=5, pady=5)

        button_frame = tk.Frame(root, bg='#e0f7fa')
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add Product", command=self.add_product, width=15, bg="#4CAF50", fg="white").grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Update Product", command=self.update_product, width=15, bg="#2196F3", fg="white").grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Delete Product", command=self.delete_product, width=15, bg="#f44336", fg="white").grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Export to CSV", command=export_to_csv, width=15, bg="#9C27B0", fg="white").grid(row=0, column=3, padx=5)

        search_frame = tk.Frame(root, bg='#e0f7fa')
        search_frame.pack(pady=5)

        tk.Entry(search_frame, textvariable=self.search_var, width=30).grid(row=0, column=0, padx=5)
        tk.Button(search_frame, text="Search", command=self.search_product, bg="#FF9800", fg="white").grid(row=0, column=1, padx=5)
        tk.Button(search_frame, text="Show All", command=self.load_products, bg="#607D8B", fg="white").grid(row=0, column=2, padx=5)

        self.tree = ttk.Treeview(root, columns=("ID", "Name", "Quantity", "Price", "Category"), show="headings")
        for col in ("ID", "Name", "Quantity", "Price", "Category"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(pady=10)
        self.tree.bind("<ButtonRelease-1>", self.select_item)

        self.load_products()

    def load_products(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in fetch_products():
            self.tree.insert('', 'end', values=row)

    def add_product(self):
        add_product(self.name_var.get(), int(self.quantity_var.get()), float(self.price_var.get()), self.category_var.get())
        self.load_products()

    def update_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No product selected")
            return
        item = self.tree.item(selected[0])['values']
        update_product(item[0], self.name_var.get(), int(self.quantity_var.get()), float(self.price_var.get()), self.category_var.get())
        self.load_products()

    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No product selected")
            return
        item = self.tree.item(selected[0])['values']
        delete_product(item[0])
        self.load_products()

    def search_product(self):
        keyword = self.search_var.get()
        results = search_products(keyword)
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in results:
            self.tree.insert('', 'end', values=row)

    def select_item(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])['values']
            self.name_var.set(item[1])
            self.quantity_var.set(item[2])
            self.price_var.set(item[3])
            self.category_var.set(item[4])

if __name__ == '__main__':
    init_db()
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
