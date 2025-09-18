import mysql.connector
import hashlib
from customtkinter import *

class UserProfile(CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.user_id = int(user_id)  # Ensure user_id is an integer
        self.username, self.password_hash = self.user_info()
        self.db()
        self.ui()

    def db(self):
        #Connect to MySQL database
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="nea"
        )
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                subject VARCHAR(255) NOT NULL
            )
        """)
        self.conn.commit()

    def user_info(self):
        #Retrieve username and password hash from MySQL database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="nea"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM users WHERE user_id = %s", (self.user_id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return user[0], user[1]
        return "Unknown", ""

    def ui(self):
        #Create UI 
        CTkLabel(self, text=f"User: {self.username}", font=("Arial", 16)).pack(pady=10)
        CTkLabel(self, text=f"Password Hash: {self.password_hash}", font=("Arial", 12)).pack(pady=5)

        self.subject_entry = CTkEntry(self, placeholder_text="Enter Subject")
        self.subject_entry.pack(pady=5)
        
        add_button = CTkButton(self, text="Add Subject", command=self.add_subject)
        add_button.pack(pady=5)
        
        self.subject_frame = CTkFrame(self)
        self.subject_frame.pack(pady=5, fill="both", expand=True)
        
        self.load_subjects()
    
    def load_subjects(self):
        #Load subjects from the DB
        for widget in self.subject_frame.winfo_children():
            widget.destroy()
        
        self.cursor.execute("SELECT subject_name FROM subjects WHERE user_id = %s", (self.user_id,))
        subjects = self.cursor.fetchall()

        # convert subject to buttons 
        for subject in subjects:
            subject_button = CTkButton(self.subject_frame, text=subject[0], command=lambda s=subject[0]: self.edit_window(s))
            subject_button.pack(pady=2, fill="x")
    
    def edit_window(self, subject):
        #Open a popup window to edit the subject
        popup = CTkToplevel(self)
        popup.title("Edit Subject")
        popup.geometry("300x150")
        popup.attributes('-topmost', True)
        
        CTkLabel(popup, text="Edit Subject:").pack(pady=5)
        subject_entry = CTkEntry(popup)
        subject_entry.insert(0, subject)
        subject_entry.pack(pady=5)
        
        def save_changes():
            new_subject = subject_entry.get().strip()
            if new_subject:
                self.cursor.execute("UPDATE subjects SET subject_name = %s WHERE user_id = %s AND subject_name = %s", (new_subject, self.user_id, subject))
                self.conn.commit()
                self.load_subjects()
                popup.destroy()
        
        save_button = CTkButton(popup, text="Save", command=save_changes)
        save_button.pack(pady=5)
        
        delete_button = CTkButton(popup, text="Delete", command=lambda: self.delete_subject(subject, popup))
        delete_button.pack(pady=5)
    
    def add_subject(self):
        #Add a new subject
        subject = self.subject_entry.get().strip()
        if subject:
            self.cursor.execute("INSERT INTO subjects (user_id, subject_name) VALUES (%s, %s)", (self.user_id, subject))
            self.conn.commit()
            self.load_subjects()
            self.subject_entry.delete(0, "end")
    
    def delete_subject(self, subject, popup=None):
        #Delete the subject
        self.cursor.execute("DELETE FROM subjects WHERE user_id = %s AND subject_name = %s", (self.user_id, subject))
        self.conn.commit()
        self.load_subjects()
        if popup:
            popup.destroy()

    def cls_con(self):
        #Close the database  when  deleted
        self.conn.close()
