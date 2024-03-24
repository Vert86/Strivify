import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime

# Create a connection to the SQLite database
conn = sqlite3.connect('productivity_app.db')
cursor = conn.cursor()

# Drop the tasks table if it exists
cursor.execute("DROP TABLE IF EXISTS tasks")

# Create the tasks table
cursor.execute('''
    CREATE TABLE tasks (
        id INTEGER PRIMARY KEY,
        title TEXT,
        description TEXT,
        deadline TEXT,
        completed INTEGER,
        points INTEGER
    )
''')

# Create the badges table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS badges (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        points_required INTEGER
    )
''')

# Insert default badges if they don't exist
cursor.execute("SELECT COUNT(*) FROM badges")
badge_count = cursor.fetchone()[0]
if badge_count == 0:
    default_badges = [
        ('Novice', 'Complete 5 tasks', 5),
        ('Intermediate', 'Complete 10 tasks', 10),
        ('Expert', 'Complete 20 tasks', 20),
        ('Master', 'Complete 50 tasks', 50)
    ]
    cursor.executemany("INSERT INTO badges (name, description, points_required) VALUES (?, ?, ?)", default_badges)

conn.commit()

# Create the main window
window = tk.Tk()
window.title("Productivity Quest")
window.geometry("800x600")
window.configure(bg="#222")

# Create the task list frame
task_list_frame = ttk.Frame(window, style="Dark.TFrame")
task_list_frame.pack(pady=20)

# Create the task list
task_list = ttk.Treeview(task_list_frame, columns=("Title", "Description", "Deadline", "Completed", "Points"), show="headings", style="Dark.Treeview")
task_list.heading("Title", text="Title")
task_list.heading("Description", text="Description")
task_list.heading("Deadline", text="Deadline")
task_list.heading("Completed", text="Completed")
task_list.heading("Points", text="Points")
task_list.pack()

# Create the task entry frame
task_entry_frame = ttk.Frame(window, style="Dark.TFrame")
task_entry_frame.pack(pady=10)

# Create the task entry fields
title_label = ttk.Label(task_entry_frame, text="Title:", style="Dark.TLabel")
title_label.grid(row=0, column=0)
title_entry = ttk.Entry(task_entry_frame, style="Dark.TEntry")
title_entry.grid(row=0, column=1)

description_label = ttk.Label(task_entry_frame, text="Description:", style="Dark.TLabel")
description_label.grid(row=1, column=0)
description_entry = ttk.Entry(task_entry_frame, style="Dark.TEntry")
description_entry.grid(row=1, column=1)

deadline_label = ttk.Label(task_entry_frame, text="Deadline:", style="Dark.TLabel")
deadline_label.grid(row=2, column=0)
deadline_entry = ttk.Entry(task_entry_frame, style="Dark.TEntry")
deadline_entry.grid(row=2, column=1)

points_label = ttk.Label(task_entry_frame, text="Points:", style="Dark.TLabel")
points_label.grid(row=3, column=0)
points_entry = ttk.Entry(task_entry_frame, style="Dark.TEntry")
points_entry.grid(row=3, column=1)

# Create the add task button
def add_task():
    title = title_entry.get()
    description = description_entry.get()
    deadline = deadline_entry.get()
    points = int(points_entry.get())
    cursor.execute("INSERT INTO tasks (title, description, deadline, completed, points) VALUES (?, ?, ?, ?, ?)", (title, description, deadline, 0, points))
    conn.commit()
    load_tasks()
    title_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    deadline_entry.delete(0, tk.END)
    points_entry.delete(0, tk.END)

add_task_button = ttk.Button(task_entry_frame, text="Add Task", command=add_task, style="Dark.TButton")
add_task_button.grid(row=4, column=0, columnspan=2, pady=10)

# Create the complete task button
def complete_task():
    selected_task = task_list.focus()
    if selected_task:
        task_id = task_list.item(selected_task, 'text')
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        conn.commit()
        load_tasks()
        update_badges()

complete_task_button = ttk.Button(window, text="Complete Task", command=complete_task, style="Dark.TButton")
complete_task_button.pack()

# Create the points label
points_label = ttk.Label(window, text="Points: 0", style="Dark.TLabel")
points_label.pack()

# Create the badges frame
badges_frame = ttk.Frame(window, style="Dark.TFrame")
badges_frame.pack(pady=20)

# Load tasks from the database
def load_tasks():
    task_list.delete(*task_list.get_children())
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    for task in tasks:
        task_list.insert("", tk.END, text=task[0], values=(task[1], task[2], task[3], "Yes" if task[4] else "No", task[5]))

    # Update the points label
    cursor.execute("SELECT SUM(points) FROM tasks WHERE completed = 1")
    total_points = cursor.fetchone()[0]
    if total_points is None:
        total_points = 0
    points_label.config(text=f"Points: {total_points}")

# Load badges from the database
def load_badges():
    for widget in badges_frame.winfo_children():
        widget.destroy()

    cursor.execute("SELECT * FROM badges")
    badges = cursor.fetchall()
    for badge in badges:
        badge_label = ttk.Label(badges_frame, text=f"{badge[1]} - {badge[2]}", style="Dark.TLabel")
        badge_label.pack()

# Update badges based on points
def update_badges():
    cursor.execute("SELECT SUM(points) FROM tasks WHERE completed = 1")
    total_points = cursor.fetchone()[0]
    if total_points is None:
        total_points = 0

    cursor.execute("SELECT * FROM badges")
    badges = cursor.fetchall()
    for badge in badges:
        if total_points >= badge[3]:
            cursor.execute("INSERT OR IGNORE INTO earned_badges (badge_id) VALUES (?)", (badge[0],))
    conn.commit()
    load_badges()

# Load initial data
load_tasks()
load_badges()

# Create the earned badges table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS earned_badges (
        id INTEGER PRIMARY KEY,
        badge_id INTEGER,
        FOREIGN KEY (badge_id) REFERENCES badges (id)
    )
''')
conn.commit()

# Configure styles
style = ttk.Style()
style.theme_use("clam")
style.configure("Dark.TFrame", background="#333")
style.configure("Dark.TLabel", background="#333", foreground="white")
style.configure("Dark.TButton", background="#555", foreground="white")
style.configure("Dark.Treeview", background="#444", fieldbackground="#444", foreground="white")
style.configure("Dark.Treeview.Heading", background="#555", foreground="white")
style.configure("Dark.TEntry", fieldbackground="#666", foreground="white")

cursor.execute("PRAGMA table_info(tasks)")
table_info = cursor.fetchall()
for column in table_info:
    print(column)

# Start the main event loop
window.mainloop()

# Close the database connection
conn.close()