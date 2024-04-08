import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime
from tkcalendar import DateEntry

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
        completed INTEGER
    )
''')

#store user info
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        full_name TEXT,
        location TEXT,
        phone_number TEXT,
        email TEXT,
        notification_preference TEXT
    )
''')
conn.commit()

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

# Create the login window
login_window = tk.Tk()
login_window.title("Taskify - Login")
login_window.geometry("400x600")
login_window.configure(bg="#2c3e50")

# Load the logo image
logo_image = tk.PhotoImage(file="logo.png")
logo_label = tk.Label(login_window, image=logo_image, bg="#2c3e50")
logo_label.pack(pady=50)

# Create the username entry
username_entry = ttk.Entry(login_window, font=("Arial", 16))
username_entry.pack(pady=10)

# Create the password entry
password_entry = ttk.Entry(login_window, show="*", font=("Arial", 16))
password_entry.pack(pady=10)

## Create the login button
def login():
    username = username_entry.get()
    password = password_entry.get()
    if username == "admin" and password == "calvert":
        login_window.destroy()
        open_main_window()
    else:
        error_label.config(text="Invalid username or password")

login_button = ttk.Button(login_window, text="Login", command=login, style="Blue.TButton")
login_button.pack(pady=20)

# Create the "Sign in with Google" button
def sign_in_with_google():
    # Add your Google sign-in logic here
    pass

google_button = ttk.Button(login_window, text="Sign in with Google", command=sign_in_with_google, style="Red.TButton")
google_button.pack(pady=10)

# Create the error label
error_label = ttk.Label(login_window, text="", foreground="red", background="#2c3e50", font=("Arial", 12))
error_label.pack(pady=10)

# Configure button styles
style = ttk.Style()
style.configure("Blue.TButton", background="#3498db", foreground="white", font=("Arial", 14), padding=10)
style.configure("Red.TButton", background="#e74c3c", foreground="white", font=("Arial", 14), padding=10)

def open_main_window():
    # Create the main window
    window = tk.Tk()
    window.title("Taskify")
    window.geometry("800x600")
    window.configure(bg="#2c3e50")

    # Create the task list frame
    task_list_frame = ttk.Frame(window, style="Blue.TFrame")
    task_list_frame.pack(pady=20)

    # Create the task list
    task_list = ttk.Treeview(task_list_frame, columns=("Title", "Description", "Deadline", "Completed"), show="headings", style="Blue.Treeview")
    task_list.heading("Title", text="Title")
    task_list.heading("Description", text="Description")
    task_list.heading("Deadline", text="Deadline")
    task_list.heading("Completed", text="Completed")
    task_list.pack()

    # Create the task entry frame
    task_entry_frame = ttk.Frame(window, style="Blue.TFrame")
    task_entry_frame.pack(pady=10)

    # Create the task entry fields
    title_label = ttk.Label(task_entry_frame, text="Title:", style="Blue.TLabel")
    title_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    title_entry = ttk.Entry(task_entry_frame, style="Blue.TEntry")
    title_entry.grid(row=0, column=1, padx=5, pady=5)

    description_label = ttk.Label(task_entry_frame, text="Description:", style="Blue.TLabel")
    description_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    description_entry = ttk.Entry(task_entry_frame, style="Blue.TEntry")
    description_entry.grid(row=1, column=1, padx=5, pady=5)

    deadline_label = ttk.Label(task_entry_frame, text="Deadline:", style="Blue.TLabel")
    deadline_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
    deadline_entry = DateEntry(task_entry_frame, style="Blue.TEntry", date_pattern="yyyy-mm-dd", format="%Y-%m-%d")
    deadline_entry.grid(row=2, column=1, padx=5, pady=5)

    time_label = ttk.Label(task_entry_frame, text="Time:", style="Blue.TLabel")
    time_label.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
    time_entry = ttk.Entry(task_entry_frame, style="Blue.TEntry")
    time_entry.insert(0, datetime.now().strftime("%H:%M"))
    time_entry.grid(row=3, column=1, padx=5, pady=5)

    # Create the add task button
    def add_task():
        title = title_entry.get()
        description = description_entry.get()
        deadline_date = deadline_entry.get_date()
        deadline_time_str = time_entry.get()
        deadline_time = datetime.strptime(deadline_time_str, "%H:%M").time()
        deadline = datetime.combine(deadline_date, deadline_time)
        cursor.execute("INSERT INTO tasks (title, description, deadline, completed) VALUES (?, ?, ?, ?)", (title, description, deadline, 0))
        conn.commit()
        load_tasks()
        title_entry.delete(0, tk.END)
        description_entry.delete(0, tk.END)
        deadline_entry.set_date(datetime.now().date())
        time_entry.delete(0, tk.END)
        time_entry.insert(0, datetime.now().strftime("%H:%M"))

    add_task_button = ttk.Button(task_entry_frame, text="Add Task", command=add_task, style="Green.TButton")
    add_task_button.grid(row=4, column=0, columnspan=2, pady=10)

    # Create the complete task button
    def complete_task():
        try:
            selected_task = task_list.focus()
            if selected_task:
                task_id = task_list.item(selected_task, 'text')
                cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
                conn.commit()
                load_tasks()
                update_badges()
                update_progress()
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    complete_task_button = ttk.Button(window, text="Complete Task", command=complete_task, style="Green.TButton")
    complete_task_button.pack()

    # Create the points label
    points_label = ttk.Label(window, text="Points: 0", style="Blue.TLabel")
    points_label.pack()

    # Create the progress frame
    progress_frame = ttk.Frame(window, style="Blue.TFrame")
    progress_frame.pack(pady=10)

    # Create the progress label
    progress_label = ttk.Label(progress_frame, text="Progress:", style="Blue.TLabel")
    progress_label.pack(side=tk.LEFT)

    # Create the progress bar
    progress_bar = ttk.Progressbar(progress_frame, length=200, style="Blue.Horizontal.TProgressbar")
    progress_bar.pack(side=tk.LEFT, padx=10)

    # Create the badges frame
    badges_frame = ttk.Frame(window, style="Blue.TFrame")
    badges_frame.pack(pady=20)

    # Load tasks from the database
    def load_tasks():
        task_list.delete(*task_list.get_children())
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
        for task in tasks:
            deadline = datetime.strptime(task[3], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
            task_list.insert("", tk.END, text=task[0], values=(task[1], task[2], deadline, "Yes" if task[4] else "No"))

        # Update the points label
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1")
        total_points = cursor.fetchone()[0]
        points_label.config(text=f"Points: {total_points}")


    # Load badges from the database
    def load_badges():
        for widget in badges_frame.winfo_children():
            widget.destroy()

        cursor.execute("SELECT * FROM badges")
        badges = cursor.fetchall()
        for badge in badges:
            badge_label = ttk.Label(badges_frame, text=f"{badge[1]} - {badge[2]}", style="Blue.TLabel")
            badge_label.pack()

    # Update badges based on points
    def update_badges():
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1")
        total_points = cursor.fetchone()[0]

        cursor.execute("SELECT * FROM badges")
        badges = cursor.fetchall()
        for badge in badges:
            if total_points >= badge[3]:
                cursor.execute("INSERT OR IGNORE INTO earned_badges (badge_id) VALUES (?)", (badge[0],))
        conn.commit()
        load_badges()

    # Update progress bar
    def update_progress():
        cursor.execute("SELECT COUNT(*) FROM tasks")
        total_tasks = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1")
        completed_tasks = cursor.fetchone()[0]
        progress = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        progress_bar['value'] = progress

    def check_deadlines():
        cursor.execute("SELECT * FROM tasks WHERE completed = 0")
        tasks = cursor.fetchall()
        for task in tasks:
            deadline = datetime.strptime(task[3], "%Y-%m-%d %H:%M")
            if deadline < datetime.now():
                send_reminder(task)

    window.after(60000, check_deadlines)  # Check deadlines every minute

    # Start checking deadlines
    check_deadlines()

    # Load initial data
    load_tasks()
    load_badges()
    update_progress()

    # Start the main event loop
    window.mainloop()

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
style.configure("Blue.TFrame", background="#2980b9")
style.configure("Blue.TLabel", background="#2980b9", foreground="white", font=("Arial", 12))
style.configure("Blue.TButton", background="#3498db", foreground="white", font=("Arial", 12), padding=5)
style.configure("Blue.Treeview", background="#ecf0f1", fieldbackground="#ecf0f1", foreground="#34495e", font=("Arial", 12))
style.configure("Blue.Treeview.Heading", background="#3498db", foreground="white", font=("Arial", 12))
style.configure("Blue.TEntry", fieldbackground="#ecf0f1", foreground="#34495e", font=("Arial", 12))
style.configure("Blue.Horizontal.TProgressbar", background="#3498db", troughcolor="#2980b9", bordercolor="#2980b9", lightcolor="#3498db", darkcolor="#2980b9")
style.configure("Green.TButton", background="#2ecc71", foreground="white", font=("Arial", 12), padding=5)


def open_registration_window():
    registration_window = tk.Toplevel(login_window)
    registration_window.title("Taskify - Registration")
    registration_window.geometry("400x400")
    registration_window.configure(bg="#2c3e50")

    # Registration form code ...

    def register():
        full_name = full_name_entry.get()
        location = location_entry.get()
        phone_number = phone_number_entry.get()
        email = email_entry.get()
        notification_preference = notification_var.get()
        cursor.execute("INSERT INTO users (full_name, location, phone_number, email, notification_preference) VALUES (?, ?, ?, ?, ?)",
                       (full_name, location, phone_number, email, notification_preference))
        conn.commit()
        registration_window.destroy()
        open_main_window()

    register_button = ttk.Button(registration_window, text="Register", command=register, style="Blue.TButton")
    register_button.pack(pady=20)

# Add a sign up button in the login window
signup_button = ttk.Button(login_window, text="Sign Up", command=open_registration_window, style="Blue.TButton")
signup_button.pack(pady=10)

def send_reminder(task):
    user_id = 1  # Assuming a single user for simplicity
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if user:
        if user[5] == "email":
            # Send email reminder
            # Code to send email using SMTP or email library
            pass
        elif user[5] == "sms":
            # Send SMS reminder
            # Code to send SMS using Twilio or SMS gateway
            pass

cursor.execute("PRAGMA table_info(tasks)")
table_info = cursor.fetchall()
for column in table_info:
    print(column)


#Start the login window
login_window.mainloop()

# Close the database connection
conn.close()