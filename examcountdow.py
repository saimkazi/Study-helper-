import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import Calendar
import json
import os
from datetime import datetime

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class ExamCountdown(ctk.CTkFrame):
    def __init__(self,parent,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        self.FILE_PATH = "exam_details.json"
        self.ui()
        self.update_countdown()

    def ui(self):
        self.main_frm = ctk.CTkFrame(self)
        self.main_frm.pack(padx=20, pady=20, fill="both", expand=True)

        self.title_labl = ctk.CTkLabel(
            self.main_frm, text="Exam Schedule", font=("Arial", 16, "bold")
        )
        self.title_labl.pack(pady=10)

        self.countdown = ctk.CTkLabel(
            self.main_frm, text="", justify="left"
        )
        self.countdown.pack(pady=10)

        self.button_frm = ctk.CTkFrame(self.main_frm, fg_color="transparent")
        self.button_frm.pack(pady=10)

        self.add_btn = ctk.CTkButton(
            self.button_frm, text="Add Exam Date", command=self.add_window,fg_color="#7f5af0"
        )
        self.add_btn.pack(side="left", padx=5)

        self.manage_btn = ctk.CTkButton(
            self.button_frm, text="Manage Exams", command=self.manage_window,fg_color="#7f5af0"
        )
        self.manage_btn.pack(side="left", padx=5)

    def save_details(self, date, subject):
        try:
            formatted_date = datetime.strptime(date, "%m/%d/%y").strftime("%d-%m-%Y")
            data = self.load_details()
            data.append({"exam_date": formatted_date, "subject": subject})
            with open(self.FILE_PATH, "w") as file:
                json.dump(data, file, indent=4)
            self.update_countdown()
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error saving exam: {str(e)}")
            return False

    def load_details(self):
        if os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, "r") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        return []

    def delete_exam(self, exam_date, subject):
        exams = [exam for exam in self.load_details()
                 if not (exam["exam_date"] == exam_date and exam["subject"] == subject)]
        with open(self.FILE_PATH, "w") as file:
            json.dump(exams, file, indent=4)
        self.update_countdown()

    def update_countdown(self):
        exams = self.load_details()
        today = datetime.today()
        countdown_text = "Upcoming Exams:\n\n"
        
        for exam in sorted(exams, key=lambda x: datetime.strptime(x["exam_date"], "%d-%m-%Y")):
            exam_day = datetime.strptime(exam["exam_date"], "%d-%m-%Y")
            days_left = (exam_day - today).days
            if days_left < 0:
                self.delete_exam(exam["exam_date"], exam["subject"])
                continue
            countdown_text += f"• {exam['subject']} - {exam['exam_date']} " \
                            f"({'Tomorrow' if days_left == 1 else f'{days_left} days left'})\n"
        
        self.countdown.configure(
            text=countdown_text if exams else "No upcoming exams!"
        )

    def add_window(self):
        AddExamWindow(self)

    def manage_window(self):
        ManageExamsWindow(self)

class AddExamWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Add Exam")
        self.geometry("350x350")
        self._setup_window()
        self._setup_ui()

    def _setup_window(self):
        self.transient(self.parent)
        self.grab_set()
        self.lift()
        self.focus_force()

    def _setup_ui(self):
        self.cal_labl = ctk.CTkLabel(self, text="Select Exam Date:")
        self.cal_labl.pack(pady=5)
        
        self.cal = Calendar(self, date_pattern='mm/dd/yy')
        self.cal.pack(pady=5)
        
        self.subject_labl = ctk.CTkLabel(self, text="Enter Subject:")
        self.subject_labl.pack(pady=5)
        
        self.subject_entry = ctk.CTkEntry(self)
        self.subject_entry.pack(pady=5)
        
        self.save_btn = ctk.CTkButton(
            self, text="Save Exam Details", command=self._save_exam
        )
        self.save_btn.pack(pady=10)

    def _save_exam(self):
        subject = self.subject_entry.get()
        if not subject:
            messagebox.showerror("Error", "Please enter a subject!")
            return
        if self.parent.save_details(self.cal.get_date(), subject):
            self.destroy()

class ManageExamsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Manage Exams")
        self.geometry("400x400")
        self._setup_window()
        self._setup_ui()
        self._refresh_list()

    def _setup_window(self):
        self.transient(self.parent)
        self.grab_set()
        self.lift()
        self.focus_force()

    def _setup_ui(self):
        self.scroll_frm = ctk.CTkScrollableFrame(self)
        self.scroll_frm.pack(fill="both", expand=True, padx=10, pady=10)

    def _refresh_list(self):
        for widget in self.scroll_frm.winfo_children():
            widget.destroy()
            
        for exam in self.parent.load_exam_details():
            item_frm = ctk.CTkFrame(self.scroll_frm)
            item_frm.pack(fill="x", pady=2)
            
            label = ctk.CTkLabel(item_frm,text=f"{exam['subject']} - {exam['exam_date']}")
            label.pack(side="left", padx=5)
            
            btn_frm = ctk.CTkFrame(item_frm, fg_color="transparent")
            btn_frm.pack(side="right")
            
            edit_btn = ctk.CTkButton(btn_frm,text="Edit",width=50,command=lambda e=exam: EditExamWindow(self.parent, e))
            edit_btn.pack(side="left", padx=2)
            
            delete_btn = ctk.CTkButton(btn_frm,text="Delete",width=50,fg_color="#d44942",hover_color="#a33732",command=lambda e=exam: self._delete_exam(e))
            delete_btn.pack(side="left", padx=2)

    def _delete_exam(self, exam):
        self.parent.delete_exam(exam["exam_date"], exam["subject"])
        self._refresh_list()

class EditExamWindow(ctk.CTkToplevel):
    def __init__(self, parent, exam):
        super().__init__(parent)
        self.parent = parent
        self.exam = exam
        self.title("Edit Exam")
        self.geometry("350x350")
        self._setup_window()
        self._setup_ui()

    def _setup_window(self):
        self.transient(self.parent)
        self.grab_set()
        self.lift()
        self.focus_force()

    def _setup_ui(self):
        self.cal_labl = ctk.CTkLabel(self, text="Select New Exam Date:")
        self.cal_labl.pack(pady=5)
        
        self.cal = Calendar(self, date_pattern='mm/dd/yy')
        self.cal.pack(pady=5)
        
        self.subj_labl = ctk.CTkLabel(self, text="Enter New Subject:")
        self.subj_labl.pack(pady=5)
        
        self.subj_entry = ctk.CTkEntry(self)
        self.subj_entry.insert(0, self.exam["subject"])
        self.subj_entry.pack(pady=5)
        
        self.save_btn = ctk.CTkButton(
            self, text="Save Changes", command=self._save_changes
        )
        self.save_btn.pack(pady=10)

    def _save_changes(self):
        new_subject = self.subj_entry.get()
        if not new_subject:
            messagebox.showerror("Error", "Please enter a subject!")
            return
        
        try:
            new_date = datetime.strptime(self.cal.get_date(), "%m/%d/%y").strftime("%d-%m-%Y")
            self.parent.delete_exam(self.exam["exam_date"], self.exam["subject"])
            if self.parent.save_exam_details(self.cal.get_date(), new_subject):
                self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid date format!")

