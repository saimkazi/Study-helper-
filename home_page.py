import customtkinter as ctk
import time
from datetime import datetime
import mysql.connector
from task_viwer import TaskView

class Homepage(ctk.CTkFrame):
    def __init__(self, parent, user_id, main_frame, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.main_frm = main_frame
        self.user_id = user_id
        self.username = self.get_username()

        # Create main 
        self.content_frm = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frm.pack(fill="both", expand=True, padx=20, pady=20)

        
        self.header_sect()
        
        # Main content area
        self.main_cont()

        # Update time
        self.time()

    def header_sect(self):
        # Header frame
        header_frm = ctk.CTkFrame(self.content_frm, fg_color="transparent")
        header_frm.pack(fill="x", pady=(0, 20))
        
        # Left section with user greeting
        left_sect = ctk.CTkFrame(header_frm, fg_color="transparent")
        left_sect.pack(side="left", anchor="w")
        
        # Current time of day greeting
        crnt_hour = datetime.now().hour
        if crnt_hour < 12:
            greeting = "Good morning"
        elif crnt_hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
            
        greeting_labl = ctk.CTkLabel(left_sect, text=f"{greeting}, {self.username}",font=("Arial", 24, "bold"),text_color="#7F5AF0"  )
        greeting_labl.pack(anchor="w")
        
        # Current date with better formatting
        self.date_labl = ctk.CTkLabel(left_sect, text="",font=("Arial", 16),text_color="#94A1B2" )
        self.date_labl.pack(anchor="w", pady=(5, 0))
        
        # Right section with clock
        right_sect = ctk.CTkFrame(header_frm, fg_color="transparent")
        right_sect.pack(side="right", anchor="e")
        
        self.time_labl = ctk.CTkLabel(right_sect, text="",font=("Arial", 42, "bold"),text_color="#7F5AF0"  )
        self.time_labl.pack(anchor="e")

    def main_cont(self):

        # Main content frame with card design

        main_card = ctk.CTkFrame(self.content_frm, corner_radius=15,fg_color="#242629",  border_width=1,border_color="#333333")
        main_card.pack(fill="both", expand=True, padx=10, pady=10)
        
        
        card_header = ctk.CTkFrame(main_card, fg_color="transparent")
        card_header.pack(fill="x", padx=20, pady=(20, 10))
        
        welcome_labl = ctk.CTkLabel(card_header, text=f"Welcome back, {self.username}",font=("Arial", 22, "bold"),text_color="#FFFFFF")
        welcome_labl.pack(side="left")
        
        
        action_frm = ctk.CTkFrame(card_header, fg_color="transparent")
        action_frm.pack(side="right")
        
        # refresh 
        refresh_btn = ctk.CTkButton(action_frm,text="Refresh",font=("Arial", 12),fg_color="#7F5AF0",hover_color="#614AD3",corner_radius=8,height=32,width=100,command=lambda: self.task_viewr.get_tasks() )
        refresh_btn.pack(side="right", padx=5)
        
        # Task viewer section 
        tasks_cont = ctk.CTkFrame(main_card, fg_color="transparent")
        tasks_cont.pack(fill="both", expand=True, padx=15, pady=15)
        
        task_header = ctk.CTkFrame(tasks_cont, fg_color="transparent", height=40)
        task_header.pack(fill="x", pady=(0, 10))
        
        task_title = ctk.CTkLabel(task_header,text="Your Tasks",font=("Arial", 18, "bold"),text_color="#FFFFFF")
        task_title.pack(side="left")
        
        
        self.task_viewr = TaskView(tasks_cont, self.user_id)
        self.task_viewr.pack(fill="both", expand=True, padx=5, pady=5)

    def time(self):
       
        crnt_time = time.strftime("%I:%M %p")
        crnt_date = datetime.now().strftime("%A, %B %d, %Y")
        
        self.time_labl.configure(text=crnt_time)
        self.date_labl.configure(text=crnt_date)
        
        self.after(1000, self.time)  # Update every second

    def get_username(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="nea"
            )
            cursor = connection.cursor()
            cursor.execute("SELECT username FROM users WHERE user_id=%s", (self.user_id,))
            username = cursor.fetchone()
            connection.close()
            
            return username[0] if username else "Guest"
        except Exception as e:
            print(f"Error fetching username: {e}")
            return "Guest"

