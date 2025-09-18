import customtkinter as ctk
import mysql.connector
from datetime import datetime, timedelta
from tkcalendar import Calendar
import functools


DB_CONFIG = {
    'user': 'root',  #  MySQL username
    'password': '',  #  MySQL password
    'host': 'localhost',  #host
    'database': 'nea',   # database name 
}

class TaskView(ctk.CTkFrame):
    def __init__(self, parent, user_id, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.tasks = self.get_tasks()
        self.deleted_tasks = []  # Stack to store deleted tasks
        self.filtered_tasks = {"Today": [], "Tomorrow": [], "Upcoming": []}
        self.filter_tsk()
        
        self.ui()

        # Make the TaskView frame fill the entire width of the parent
        self.pack(fill="both", expand=True)

    def get_tasks(self):
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        today = datetime.today().date()

        cursor.execute("""
            SELECT title, date, time 
            FROM events 
            WHERE user_id = %s AND date >= %s
            ORDER BY date ASC
        """, (self.user_id, today.strftime('%Y-%m-%d')))

        tasks = cursor.fetchall()
        connection.close()
        return tasks

    def filter_tsk(self):
        today = datetime.today().date()
        tomorrow = today + timedelta(days=1)
        self.filtered_tasks = {"Today": [], "Tomorrow": [], "Upcoming": []}

        for task in self.tasks:
            task_date = datetime.strptime(task["date"], "%Y-%m-%d").date()
            if task_date == today:
                self.filtered_tasks["Today"].append(task)
            elif task_date == tomorrow:
                self.filtered_tasks["Tomorrow"].append(task)
            else:
                self.filtered_tasks["Upcoming"].append(task)

    def Mark_deletion(self, task, checkbox):
        # Marks a task for deletion 
        if task in self.deleted_tasks:
            self.deleted_tasks.remove(task)
            checkbox.configure(fg_color=("#3B8ED0", "#1F6AA5"))
        else:
            self.deleted_tasks.append(task)
            checkbox.configure(fg_color="red")

    def save_deletions(self):
         # Delete all marked tasks  
        if self.deleted_tasks:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            for task in self.deleted_tasks:
                cursor.execute("DELETE FROM events WHERE user_id = %s AND title = %s AND date = %s AND time = %s", 
                               (self.user_id, task['title'], task['date'], task['time']))
            connection.commit()
            connection.close()

            self.tasks = self.get_tasks()
            self.filter_tsk()
            self.clear_ui()
            self.ui()

    def add_task(self):
       
        frame = ctk.CTkFrame(self)
        frame.pack(pady=5, fill="both", side="right")

        ctk.CTkLabel(frame, text="Task Title:").pack(pady=5)
        title_entry = ctk.CTkEntry(frame)
        title_entry.pack(pady=5, fill="x")

        ctk.CTkLabel(frame, text="Select Time:").pack(pady=5)

        time_slots = [datetime.strptime(f"{hour}:00", "%H:%M").strftime("%I:%M %p") for hour in range(7, 24)]
        time_opt = ctk.CTkComboBox(frame, values=time_slots)
        time_opt.pack(pady=5, fill="x")
        time_opt.set(time_slots[0])

        # Radio Buttons for Date Selection
        date_selection = ctk.CTkFrame(frame)
        date_selection.pack(pady=10, fill="x")

        selected_date_option = ctk.StringVar(value="Today")
        custom_date = ctk.StringVar(value=datetime.today().date().strftime('%Y-%m-%d'))

        today = ctk.CTkRadioButton(date_selection, text="Today", variable=selected_date_option, value="Today",fg_color="#7f5af0")
        tomorrow = ctk.CTkRadioButton(date_selection, text="Tomorrow", variable=selected_date_option, value="Tomorrow",fg_color="#7f5af0")
        custom = ctk.CTkRadioButton(date_selection, text="Custom", variable=selected_date_option, value="Custom",fg_color="#7f5af0")

        today.pack(anchor="w")
        tomorrow.pack(anchor="w")
        custom.pack(anchor="w")

        # Date display for custom date
        display_date = ctk.CTkLabel(date_selection, text=f"Selected date: {custom_date.get()}")
        display_date.pack(anchor="w", pady=(5, 0))

        def open_cstm_date():
            if selected_date_option.get() == "Custom":
                cal_window = ctk.CTkToplevel(self)
                cal_window.title("Select Date")
                cal_window.geometry("300x300")
                cal_window.attributes('-topmost', True)  # Keep window on top
                
                cal = Calendar(cal_window, selectmode="day", date_pattern="yyyy-MM-dd")
                cal.pack(pady=20)
                
                def select_date():
                    selected_date = cal.get_date()
                    custom_date.set(selected_date)
                    display_date.configure(text=f"Selected date: {selected_date}")
                    cal_window.destroy()
                
                select_button = ctk.CTkButton(cal_window, text="Select", command=select_date)
                select_button.pack(pady=10)

        def handler_date():
            if selected_date_option.get() == "Custom":
                display_date.pack(anchor="w", pady=(5, 0))
                open_cstm_date()
            else:
                display_date.pack_forget()
        
        # Configure radio buttons to call handle_radio_change
        custom.configure(command=handler_date)
        today.configure(command=handler_date)
        tomorrow.configure(command=handler_date)

        # Select custom date button
        date_button = ctk.CTkButton(
            date_selection,
            text="Select Custom Date",
            command=open_cstm_date
        )
        date_button.pack(pady=5)

        def save_task():
            title = title_entry.get().strip()
            time_inpt = time_opt.get().strip()
            date_opt = selected_date_option.get()

            if not title or not time_inpt:
                return  

            if date_opt == "Today":
                task_date = datetime.today().date().strftime('%Y-%m-%d')
            elif date_opt == "Tomorrow":
                task_date = (datetime.today().date() + timedelta(days=1)).strftime('%Y-%m-%d')
            else:
                task_date = custom_date.get()  # Get the selected custom date

            conv_24hr = datetime.strptime(time_inpt, "%I:%M %p").strftime("%H:%M:%S")

            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            cursor.execute("INSERT INTO events (user_id, title, date, time) VALUES (%s, %s, %s, %s)", 
                        (self.user_id, title, task_date, conv_24hr))
            connection.commit()
            connection.close()

            self.tasks = self.get_tasks()
            self.filter_tsk()
            self.clear_ui()
            self.ui()

        ctk.CTkButton(frame, text="Save Task", command=save_task,fg_color="#7f5af0").pack(pady=10)

    def clear_ui(self):
    # Clears UI
        try:
            if self.winfo_exists():
                for widget in self.winfo_children():
                    widget.destroy()
        except Exception as e:
            print(f"Error clearing UI: {e}")
    
    def destroy(self):
        
        try:
            # Save any pending deletions
            if hasattr(self, 'deleted_tasks') and self.deleted_tasks:
                try:
                    connection = mysql.connector.connect(**DB_CONFIG)
                    cursor = connection.cursor()
                    for task in self.deleted_tasks:
                        cursor.execute("DELETE FROM events WHERE user_id = %s AND title = %s AND date = %s AND time = %s", 
                                     (self.user_id, task['title'], task['date'], task['time']))
                    connection.commit()
                    connection.close()
                except:
                    pass 
        finally:
            
            try:
                super().destroy()
            except:
                pass  


    def ui(self):
        # Creates  UI 
        task_frame = ctk.CTkFrame(self)
        task_frame.pack(pady=10, padx=10, fill="both", expand=True, side="left")  # Main frame for tasks

        for section in ["Today", "Tomorrow", "Upcoming"]:
            frame = ctk.CTkFrame(task_frame)
            frame.pack(side="left", padx=(0, 10), fill="both", expand=True)  # Task sections fill available space

            ctk.CTkLabel(frame, text=section, font=("Arial", 16, "bold")).pack(pady=5)

            task_list = self.filtered_tasks[section]
            if task_list:
                for task in task_list:
                    task_frame_inner = ctk.CTkFrame(frame)
                    task_frame_inner.pack(fill="x", pady=2)

                    ctk.CTkLabel(task_frame_inner, text=f"{task['title']} - {task['time']}").pack(side="left", padx=5)

                    checkbox = ctk.CTkCheckBox(task_frame_inner, text="")
                    checkbox.configure(command=functools.partial(self.Mark_deletion, task, checkbox))
                    checkbox.pack(side="right", padx=5)
            else:
                ctk.CTkLabel(frame, text="No tasks", font=("Arial", 12, "italic")).pack(pady=2, fill='x')

       
        self.add_task()  