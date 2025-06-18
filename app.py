import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import json
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, date
import os

class PersonalExpenseTracker:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker - Abdul Hadi (F2022266615)")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize database
        self.init_database()
        
        # Create GUI
        self.create_widgets()
        
        # Load and display expenses
        self.refresh_expense_list()
        
    def init_database(self):
        """Initialize SQLite database and create tables if they don't exist"""
        self.conn = sqlite3.connect('expenses.db')
        self.cursor = self.conn.cursor()
        
        # Create expenses table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create categories table for suggestions
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Insert default categories
        default_categories = ['Food', 'Transportation', 'Entertainment', 'Shopping', 
                            'Bills', 'Healthcare', 'Education', 'Others']
        for category in default_categories:
            self.cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
        
        self.conn.commit()
    
    def create_widgets(self):
        """Create and arrange all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Personal Expense Tracker", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Left Panel - Input Form
        self.create_input_panel(main_frame)
        
        # Right Panel - Filters and Actions
        self.create_filter_panel(main_frame)
        
        # Bottom Panel - Expense List
        self.create_expense_list_panel(main_frame)
        
        # Chart Panel
        self.create_chart_panel(main_frame)
    
    def create_input_panel(self, parent):
        """Create expense input form"""
        input_frame = ttk.LabelFrame(parent, text="Add New Expense", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
        # Amount
        ttk.Label(input_frame, text="Amount:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.amount_var = tk.StringVar()
        amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var, width=15)
        amount_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Category
        ttk.Label(input_frame, text="Category:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.category_var = tk.StringVar()
        self.categories = self.get_categories()
        category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, 
                                     values=self.categories, width=13)
        category_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Description
        ttk.Label(input_frame, text="Description:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.description_var = tk.StringVar()
        desc_entry = ttk.Entry(input_frame, textvariable=self.description_var, width=15)
        desc_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Date
        ttk.Label(input_frame, text="Date:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        date_entry = ttk.Entry(input_frame, textvariable=self.date_var, width=15)
        date_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Add Button
        add_btn = ttk.Button(input_frame, text="Add Expense", command=self.add_expense)
        add_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        input_frame.columnconfigure(1, weight=1)
    
    def create_filter_panel(self, parent):
        """Create filter and action panel"""
        filter_frame = ttk.LabelFrame(parent, text="Filters & Actions", padding="10")
        filter_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N), padx=(10, 0))
        
        # Month/Year filter
        ttk.Label(filter_frame, text="Filter by Month:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.month_var = tk.StringVar()
        month_entry = ttk.Entry(filter_frame, textvariable=self.month_var, width=10)
        month_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Format hint
        ttk.Label(filter_frame, text="(YYYY-MM)", font=('Arial', 8), 
                 foreground='gray').grid(row=0, column=2, sticky=tk.W, padx=(5, 0))
        
        # Filter buttons
        filter_btn = ttk.Button(filter_frame, text="Apply Filter", command=self.apply_filter)
        filter_btn.grid(row=1, column=0, pady=5)
        
        clear_filter_btn = ttk.Button(filter_frame, text="Clear Filter", command=self.clear_filter)
        clear_filter_btn.grid(row=1, column=1, pady=5)
        
        # Monthly total
        self.total_label = ttk.Label(filter_frame, text="Total: Rs:0.00", 
                                    font=('Arial', 12, 'bold'))
        self.total_label.grid(row=2, column=0, columnspan=3, pady=10)
        
        # Action buttons
        ttk.Separator(filter_frame, orient='horizontal').grid(row=3, column=0, columnspan=3, 
                                                             sticky=(tk.W, tk.E), pady=10)
        
        export_btn = ttk.Button(filter_frame, text="Export to CSV", command=self.export_to_csv)
        export_btn.grid(row=4, column=0, pady=2)
        
        chart_btn = ttk.Button(filter_frame, text="Show Charts", command=self.show_chart)
        chart_btn.grid(row=4, column=1, pady=2)
        
        backup_btn = ttk.Button(filter_frame, text="Backup Data", command=self.backup_data)
        backup_btn.grid(row=5, column=0, pady=2)
        
        restore_btn = ttk.Button(filter_frame, text="Restore Data", command=self.restore_data)
        restore_btn.grid(row=5, column=1, pady=2)
        
        filter_frame.columnconfigure(1, weight=1)
    
    def create_expense_list_panel(self, parent):
        """Create expense list with treeview"""
        list_frame = ttk.LabelFrame(parent, text="Expense History", padding="10")
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Create Treeview
        columns = ('ID', 'Date', 'Category', 'Description', 'Amount')
        self.expense_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.expense_tree.heading(col, text=col)
            if col == 'ID':
                self.expense_tree.column(col, width=50)
            elif col == 'Amount':
                self.expense_tree.column(col, width=100)
            else:
                self.expense_tree.column(col, width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.expense_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.expense_tree.xview)
        self.expense_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.expense_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Delete button
        delete_btn = ttk.Button(list_frame, text="Delete Selected", command=self.delete_expense)
        delete_btn.grid(row=2, column=0, pady=10)
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
    
    def create_chart_panel(self, parent):
        """Create chart display panel (no longer needed as charts open in separate window)"""
        pass  # Charts now open in separate windows
    
    def get_categories(self):
        """Fetch categories from database"""
        self.cursor.execute('SELECT name FROM categories ORDER BY name')
        return [row[0] for row in self.cursor.fetchall()]
    
    def add_expense(self):
        """Add new expense to database"""
        try:
            amount = float(self.amount_var.get())
            category = self.category_var.get().strip()
            description = self.description_var.get().strip()
            expense_date = self.date_var.get().strip()
            
            if not category:
                messagebox.showerror("Error", "Please select a category")
                return
            
            # Validate date format
            try:
                datetime.strptime(expense_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Please enter date in YYYY-MM-DD format")
                return
            
            # Insert into database
            self.cursor.execute('''
                INSERT INTO expenses (amount, category, description, date)
                VALUES (?, ?, ?, ?)
            ''', (amount, category, description, expense_date))
            
            # Add category if new
            self.cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
            
            self.conn.commit()
            
            # Clear form
            self.amount_var.set("")
            self.category_var.set("")
            self.description_var.set("")
            self.date_var.set(date.today().strftime("%Y-%m-%d"))
            
            # Refresh display
            self.refresh_expense_list()
            self.categories = self.get_categories()
            
            messagebox.showinfo("Success", "Expense added successfully!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def refresh_expense_list(self, filter_month=None):
        """Refresh the expense list display"""
        # Clear existing items
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)
        
        # Fetch expenses
        if filter_month:
            self.cursor.execute('''
                SELECT id, date, category, description, amount 
                FROM expenses 
                WHERE date LIKE ?
                ORDER BY date DESC, id DESC
            ''', (f"{filter_month}%",))
        else:
            self.cursor.execute('''
                SELECT id, date, category, description, amount 
                FROM expenses 
                ORDER BY date DESC, id DESC
            ''')
        
        expenses = self.cursor.fetchall()
        total = 0
        
        # Insert into treeview
        for expense in expenses:
            self.expense_tree.insert('', 'end', values=(
                expense[0], expense[1], expense[2], 
                expense[3] or '', f"Rs:{expense[4]:.2f}"
            ))
            total += expense[4]
        
        # Update total label
        if filter_month:
            self.total_label.config(text=f"Total for {filter_month}: Rs:{total:.2f}")
        else:
            self.total_label.config(text=f"Total: Rs:{total:.2f}")
    
    def apply_filter(self):
        """Apply month filter"""
        month_filter = self.month_var.get().strip()
        if month_filter:
            try:
                # Validate format
                datetime.strptime(month_filter + "-01", "%Y-%m-%d")
                self.refresh_expense_list(month_filter)
            except ValueError:
                messagebox.showerror("Error", "Please enter month in YYYY-MM format")
        else:
            messagebox.showwarning("Warning", "Please enter a month to filter")
    
    def clear_filter(self):
        """Clear all filters"""
        self.month_var.set("")
        self.refresh_expense_list()
    
    def delete_expense(self):
        """Delete selected expense"""
        selected_item = self.expense_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an expense to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?"):
            expense_id = self.expense_tree.item(selected_item[0])['values'][0]
            
            self.cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
            self.conn.commit()
            
            self.refresh_expense_list()
            messagebox.showinfo("Success", "Expense deleted successfully!")
    
    def export_to_csv(self):
        """Export expenses to CSV file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save expenses as CSV"
            )
            
            if filename:
                # Get current filter
                month_filter = self.month_var.get().strip()
                
                if month_filter:
                    self.cursor.execute('''
                        SELECT date, category, description, amount 
                        FROM expenses 
                        WHERE date LIKE ?
                        ORDER BY date DESC
                    ''', (f"{month_filter}%",))
                else:
                    self.cursor.execute('''
                        SELECT date, category, description, amount 
                        FROM expenses 
                        ORDER BY date DESC
                    ''')
                
                expenses = self.cursor.fetchall()
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Date', 'Category', 'Description', 'Amount'])
                    
                    for expense in expenses:
                        writer.writerow([
                            expense[0], expense[1], 
                            expense[2] or '', expense[3]
                        ])
                
                messagebox.showinfo("Success", f"Data exported to {filename}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def show_chart(self):
        """Display pie chart of expenses by category in a separate window"""
        try:
            # Get current filter
            month_filter = self.month_var.get().strip()
            
            if month_filter:
                self.cursor.execute('''
                    SELECT category, SUM(amount) 
                    FROM expenses 
                    WHERE date LIKE ?
                    GROUP BY category
                    ORDER BY SUM(amount) DESC
                ''', (f"{month_filter}%",))
                title_suffix = f" for {month_filter}"
            else:
                self.cursor.execute('''
                    SELECT category, SUM(amount) 
                    FROM expenses 
                    GROUP BY category
                    ORDER BY SUM(amount) DESC
                ''')
                title_suffix = ""
            
            data = self.cursor.fetchall()
            
            if not data:
                messagebox.showinfo("Info", "No data available for chart")
                return
            
            # Create separate window for chart
            chart_window = tk.Toplevel(self.root)
            chart_window.title(f"Expense Chart{title_suffix}")
            chart_window.geometry("900x700")
            chart_window.configure(bg='white')
            
            # Make window modal (optional)
            chart_window.transient(self.root)
            chart_window.grab_set()
            
            # Create frame for chart
            chart_frame = ttk.Frame(chart_window, padding="10")
            chart_frame.pack(fill=tk.BOTH, expand=True)
            
            # Get categories and amounts
            categories = [row[0] for row in data]
            amounts = [row[1] for row in data]
            
            # Create figure with subplots for both pie and bar chart
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # Pie chart
            wedges, texts, autotexts = ax1.pie(amounts, labels=categories, autopct='%1.1f%%', 
                                              startangle=90)
            ax1.set_title(f'Expense Distribution{title_suffix}', fontsize=12, fontweight='bold')
            
            # Bar chart
            bars = ax2.bar(categories, amounts, color=plt.cm.Set3(range(len(categories))))
            ax2.set_title(f'Expense Amounts by Category{title_suffix}', fontsize=12, fontweight='bold')
            ax2.set_xlabel('Category')
            ax2.set_ylabel('Amount (Rs)')
            ax2.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, amount in zip(bars, amounts):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + max(amounts)*0.01,
                        f'Rs:{amount:.2f}', ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            
            # Create canvas
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Button frame
            button_frame = ttk.Frame(chart_frame)
            button_frame.pack(fill=tk.X, pady=10)
            
            # Close button
            close_btn = ttk.Button(button_frame, text="Close Chart", 
                                  command=chart_window.destroy)
            close_btn.pack(side=tk.RIGHT, padx=5)
            
            # Export chart button
            export_chart_btn = ttk.Button(button_frame, text="Save Chart as PNG", 
                                         command=lambda: self.save_chart(fig))
            export_chart_btn.pack(side=tk.RIGHT, padx=5)
            
            # Center the window
            chart_window.update_idletasks()
            x = (chart_window.winfo_screenwidth() // 2) - (chart_window.winfo_width() // 2)
            y = (chart_window.winfo_screenheight() // 2) - (chart_window.winfo_height() // 2)
            chart_window.geometry(f"+{x}+{y}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Chart generation failed: {str(e)}")
    
    def save_chart(self, fig):
        """Save chart as PNG file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                title="Save chart as PNG"
            )
            
            if filename:
                fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Chart saved as {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save chart: {str(e)}")
    
    def backup_data(self):
        """Backup database to JSON file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save backup as JSON"
            )
            
            if filename:
                # Get all expenses
                self.cursor.execute('SELECT * FROM expenses ORDER BY id')
                expenses = self.cursor.fetchall()
                
                # Convert to dict format
                backup_data = {
                    'expenses': [
                        {
                            'id': exp[0],
                            'amount': exp[1],
                            'category': exp[2],
                            'description': exp[3],
                            'date': exp[4],
                            'created_at': exp[5]
                        } for exp in expenses
                    ],
                    'backup_date': datetime.now().isoformat(),
                    'total_records': len(expenses)
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Backup saved to {filename}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")
    
    def restore_data(self):
        """Restore database from JSON backup"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Select backup file to restore"
            )
            
            if filename:
                if messagebox.askyesno("Confirm", 
                    "This will replace all current data. Are you sure?"):
                    
                    with open(filename, 'r', encoding='utf-8') as f:
                        backup_data = json.load(f)
                    
                    # Clear existing data
                    self.cursor.execute('DELETE FROM expenses')
                    
                    # Restore expenses
                    for exp in backup_data['expenses']:
                        self.cursor.execute('''
                            INSERT INTO expenses (amount, category, description, date)
                            VALUES (?, ?, ?, ?)
                        ''', (exp['amount'], exp['category'], 
                             exp['description'], exp['date']))
                    
                    self.conn.commit()
                    self.refresh_expense_list()
                    
                    messagebox.showinfo("Success", 
                        f"Restored {len(backup_data['expenses'])} records")
        
        except Exception as e:
            messagebox.showerror("Error", f"Restore failed: {str(e)}")
    
    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    root = tk.Tk()
    app = PersonalExpenseTracker(root)
    
    # Handle window closing
    def on_closing():
        app.conn.close()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()