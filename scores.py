import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import Calendar
import mysql.connector  # Import MySQL connector

DB_CONFIG = {
    'user': 'root', 
    'password': '',  
    'host': 'localhost', 
    'database': 'nea',   
    'buffered': 'True'
}


class ScoreManager(ctk.CTkFrame):  # inheritance 
    def __init__(self, parent,user_id, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)  

        self.user_id=user_id
        self.subj = self.get_subj(user_id)  
        self.ui()

    def get_subj(self, user_id):
        
        subjects = []
        try:
            
            # Connect to the MySQL database
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()

            # Execute the query to fetch subjects for user_id = 1
            cursor.execute("SELECT subject_name FROM subjects WHERE user_id = %s", (user_id,))
            rows = cursor.fetchall()

            # Extract subject names from the query results
            subjects = [row[0] for row in rows]
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while fetching subjects: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        return subjects

    def cstm_date(self):
        top = ctk.CTkToplevel(self)
        top.title("Select Date")

        # Get screen dimensions
        screen_width = top.winfo_screenwidth()
        screen_height = top.winfo_screenheight()

        # Set the size of the calendar window
        calendar_width = 300
        calendar_height = 300

        # Calculate x and y coordinates for center position
        x = (screen_width // 2) - (calendar_width // 2)
        y = (screen_height // 2) - (calendar_height // 2)

        # Set the geometry of the calendar window
        top.geometry(f"{calendar_width}x{calendar_height}+{x}+{y}")
        top.attributes('-topmost', True)  # Ensure the window stays on top

        cal = Calendar(top, selectmode='day', year=2024, month=1, day=1)
        cal.pack(pady=20)
        
        def grab_date():
            selected_date = cal.get_date()
            month, day, year = map(int, selected_date.split("/"))
            self.yr_var.set(year)  # Year will be full 4-digit format
            self.month_var.set(month)
            self.date_disp_var.set(f"Selected Date: {day}/{month}/{year}")
            top.destroy()
        
        ctk.CTkButton(top, text="Select", command=grab_date).pack()

    def add_score(self):
        subject = self.subj_var.get()
        year_str = self.yr_var.get()  # Get the year as a string
        month = int(self.month_var.get())
        score = float(self.score_var.get())  # Score can be a float as per your table definition

        # Ensure the year is a full four-digit number
        try:
            year = int(year_str)
            if year < 100:  # If the year is less than 100, assume it's in the 2000s
                year += 2000
        except ValueError:
            messagebox.showerror("Input Error", "Year must be a valid integer.")
            return

        print(f"Adding score: Subject={subject}, Year={year}, Month={month}, Score={score}")  
        
        
        try:
            # Connect to the DB
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            
            
            cursor.execute("SELECT subject_id FROM subjects WHERE subject_name = %s AND user_id = %s", (subject,self.user_id))
            subject_id_row = cursor.fetchone()

            if not subject_id_row:
                messagebox.showerror("Database Error", "Subject not found in the database.")
                return

            subject_id = subject_id_row[0]

            #NOTE Close the first cursor and create a new one for the INSERT
            cursor.close()
            cursor = connection.cursor()

            # Insert the score into the scores table
            cursor.execute("INSERT INTO scores (subject_id, month, year, score) VALUES (%s, %s, %s, %s)",
                        (subject_id, month, year, score))
            connection.commit()
            messagebox.showinfo("Success", "Score added successfully!")
           
            
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while adding the score: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


    def ui(self):
        frame = ctk.CTkFrame(self)  # Ensure it's created in the context of ScoreManager
        frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        self.subj_var = ctk.StringVar()
        self.yr_var = ctk.StringVar()
        self.month_var = ctk.StringVar()
        self.score_var = ctk.StringVar()
        self.date_disp_var = ctk.StringVar(value="No date selected")
        
        ctk.CTkLabel(frame, text="Subject:").grid(row=0, column=0, pady=5)
        ctk.CTkComboBox(frame, variable=self.subj_var, values=self.subj).grid(row=0, column=1, pady=5)
        
        ctk.CTkLabel(frame, text="Date:").grid(row=1, column=0, pady=5)
        date_btn = ctk.CTkButton(frame, text="Select Date", command=self.cstm_date)
        date_btn.grid(row=1, column=1, pady=5)
        
        ctk.CTkLabel(frame, textvariable=self.date_disp_var, text_color="white").grid(row=2, column=1, pady=5)
        
        ctk.CTkLabel(frame, text="Score:").grid(row=3, column=0, pady=5)
        ctk.CTkEntry(frame, textvariable=self.score_var).grid(row=3, column=1, pady=5)
        
        ctk.CTkButton(frame, text="Add Score", command=self.add_score).grid(row=4, columnspan=2, pady=10)
