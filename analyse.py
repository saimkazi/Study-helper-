import mysql.connector
import json
import datetime
import webbrowser
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk,scrolledtext
import customtkinter as ctk

DB_CONFIG = {
    'user': 'root',  #  MySQL username
    'password': '',  #  MySQL password
    'host': 'localhost',  #host
    'database': 'nea',   # database name 
}

# Set appearance for CustomTkinter (dark mode by default)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def db():
    return mysql.connector.connect(**DB_CONFIG)

class StudyAdvisorApp(ctk.CTkFrame):
    def __init__(self,parent,user_id,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        
        self.user_id=user_id
        # File paths
        self.scores_file = Path("scores.json")
        self.feelings_file = Path("feelings.json")
        self.methods_file = Path("learning_methods.json")
        
        self.ui()
        self.load_subj()
        # Start recursive update of recommendation frames
        self.recom_loop()

    def ui(self):
        # Main container frame
        self.main_frm = ctk.CTkFrame(self, fg_color="#1f2a3c")
        self.main_frm.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Subject Selection 
        subj_labl = ctk.CTkLabel(self.main_frm, text="Select Subject:", font=("Arial", 14))
        subj_labl.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.subj_var = tk.StringVar()
        self.subj_combobox = ttk.Combobox(self.main_frm, textvariable=self.subj_var, state="readonly")
        self.subj_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.subj_combobox.bind("<<ComboboxSelected>>", lambda e: self.update_scores())
        
        # Scores  
        scores_title = ctk.CTkLabel(self.main_frm, text="Last 3 Scores:", font=("Arial", 14))
        scores_title.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.scores_labl = ctk.CTkLabel(self.main_frm, text="", font=("Arial", 12))
        self.scores_labl.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        #  Graph & Trend Panel
        plot_container = ctk.CTkFrame(self.main_frm, fg_color="#2e2e2e")
        plot_container.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        plot_container.columnconfigure(0, weight=1)
        plot_container.columnconfigure(1, weight=1)
        
        
        self.figure, self.ax = plt.subplots(figsize=(5, 2))
        self.figure.patch.set_facecolor('#333333')  # Figure background
        self.ax.set_facecolor('#333333')             # Plot background
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_container)
        self.canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        
        self.trend_frm = ctk.CTkFrame(plot_container, fg_color="#3e3e3e")
        self.trend_frm.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        trend_title = ctk.CTkLabel(self.trend_frm, text="Performance Trend", font=("Arial", 14, "bold"))
        trend_title.pack(anchor="w", padx=10, pady=5)
        self.crnt_improve_labl = ctk.CTkLabel(self.trend_frm, text="Current Improvement: N/A", font=("Arial", 12))
        self.crnt_improve_labl.pack(anchor="w", padx=10, pady=5)
        self.predicted_improve_labl = ctk.CTkLabel(self.trend_frm, text="Predicted Next Increase: N/A", font=("Arial", 12))
        self.predicted_improve_labl.pack(anchor="w", padx=10, pady=5)
        
        
        struggle_frm = ctk.CTkFrame(self.main_frm, fg_color="#2e2e2e")
        struggle_frm.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        struggle_labl = ctk.CTkLabel(struggle_frm, text="What are you struggling with?", font=("Arial", 14))
        struggle_labl.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        self.struggle_vars = {
            "memory": tk.BooleanVar(),
            "focus": tk.BooleanVar(),
            "understanding": tk.BooleanVar(),
            "motivation": tk.BooleanVar()
        }
        cb_memory = ctk.CTkCheckBox(struggle_frm, text="Remembering key terms", variable=self.struggle_vars["memory"])
        cb_memory.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        cb_understanding = ctk.CTkCheckBox(struggle_frm, text="Understanding concepts", variable=self.struggle_vars["understanding"])
        cb_understanding.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        cb_focus = ctk.CTkCheckBox(struggle_frm, text="Staying focused", variable=self.struggle_vars["focus"])
        cb_focus.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        cb_motivation = ctk.CTkCheckBox(struggle_frm, text="Staying motivated", variable=self.struggle_vars["motivation"])
        cb_motivation.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        #  Feeling Input 
        feeling_labl = ctk.CTkLabel(self.main_frm, text="How are you feeling?", font=("Arial", 14))
        feeling_labl.grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.feeling_entry = ctk.CTkEntry(self.main_frm, width=250)
        self.feeling_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")
        
        # Recommendation Sections Container 
        rec_container = ctk.CTkFrame(self.main_frm, fg_color="#2e2e2e")
        rec_container.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        rec_container.columnconfigure((0, 1, 2), weight=1)
        
        # Performance Analysis
        analysis_frm = ctk.CTkFrame(rec_container, fg_color="#3e3e3e")
        analysis_frm.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        analysis_labl = ctk.CTkLabel(analysis_frm, text="Performance Analysis", font=("Arial", 12, "bold"))
        analysis_labl.pack(anchor="w", padx=5, pady=5)
        self.analysis_txt = tk.scrolledtext.ScrolledText(analysis_frm, height=8, wrap=tk.WORD, bg="#333333", fg="white")
        self.analysis_txt.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Struggle-Specific Methods
        method_frm = ctk.CTkFrame(rec_container, fg_color="#3e3e3e")
        method_frm.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        method_labl = ctk.CTkLabel(method_frm, text="Struggle-Specific Methods", font=("Arial", 12, "bold"))
        method_labl.pack(anchor="w", padx=5, pady=5)
        self.method_txt = tk.scrolledtext.ScrolledText(method_frm, height=8, wrap=tk.WORD, bg="#333333", fg="white")
        self.method_txt.pack(fill="both", expand=True, padx=5, pady=5)
        # Frame to hold resource buttons
        self.resource_button_frm = ctk.CTkFrame(method_frm, fg_color="#3e3e3e")
        self.resource_button_frm.pack(fill="x", padx=5, pady=5)
        
        # Feeling-Based Suggestions
        suggestion_frm = ctk.CTkFrame(rec_container, fg_color="#3e3e3e")
        suggestion_frm.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        suggestion_labl = ctk.CTkLabel(suggestion_frm, text="Feeling-Based Suggestions", font=("Arial", 12, "bold"))
        suggestion_labl.pack(anchor="w", padx=5, pady=5)
        self.suggestion_text = tk.scrolledtext.ScrolledText(suggestion_frm, height=8, wrap=tk.WORD, bg="#333333", fg="white")
        self.suggestion_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configure grid weights for resizing
        self.main_frm.columnconfigure(1, weight=1)
        self.main_frm.rowconfigure(5, weight=1)

    def load_subj(self):
        try:
            conn = db()
            cursor = conn.cursor()
            cursor.execute("SELECT subject_id, subject_name FROM subjects WHERE user_id=%s",(self.user_id,))
            subjects = cursor.fetchall()
            conn.close()
            
            if subjects:
                self.subj_map = {str(sub[0]): sub[1] for sub in subjects}
                self.subj_combobox['values'] = list(self.subj_map.values())
                self.subj_var.set(list(self.subj_map.values())[0])
                self.update_scores()
        except Exception as e:
            print(f"Error loading subjects: {e}")

    def update_scores(self):
        
        subj_name = self.subj_var.get()
        subj_id = next((k for k, v in self.subj_map.items() if v == subj_name), None)

        if not subj_id:
            self.scores_labl.configure(text="No scores available")
            return

        try:
            conn = db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT score, month, year
                FROM scores
                WHERE subject_id = %s
                ORDER BY year DESC, month DESC
                LIMIT 3
            """, (subj_id,))
            scores = cursor.fetchall()
            conn.close()

            if scores:
                scores_txt = ", ".join(f"{entry['score']}" for entry in scores)
                self.scores_labl.configure(text=scores_txt)
                self.plot_scores(scores)
                self.update_trend(scores)
            else:
                self.scores_labl.configure(text="No scores available")
        except Exception as e:
            self.scores_labl.configure(text="Error loading scores")
            print(e)

    def plot_scores(self, scores):
        self.ax.clear()
        self.figure.patch.set_facecolor('#333333')
        self.ax.set_facecolor('#333333')
        
        if scores:
            try:
                score_values = [int(entry['score']) for entry in scores]
                attempts = list(range(1, len(score_values) + 1))
                self.ax.plot(attempts, score_values, marker='o', linestyle='-', color='b', label="Scores")
                self.ax.fill_between(attempts, score_values, min(score_values) - 5, color='blue', alpha=0.2)
                self.ax.set_title("Score Progression", fontsize=12, fontweight="bold", color='white')
                self.ax.set_xlabel("Attempts", fontsize=10, color='white')
                self.ax.set_ylabel("Scores", fontsize=10, color='white')
                self.ax.tick_params(colors='white')
                self.ax.spines['bottom'].set_color('white')
                self.ax.spines['left'].set_color('white')
                self.ax.grid(True, linestyle='--', alpha=0.6, color='white')
                self.ax.legend(facecolor='#333333', edgecolor='white')
                self.ax.set_ylim(min(score_values) - 5, max(score_values) + 5)
                if len(score_values) > 1:
                    percentage_change = ((score_values[-1] - score_values[0]) / score_values[0]) * 100 if score_values[0] != 0 else 0
                    self.ax.text(attempts[-1], score_values[-1], f"{percentage_change:.2f}% Change", fontsize=10, color='red')
            except Exception as ex:
                print(f"Error plotting scores: {ex}")
        else:
            self.ax.text(0.5, 0.5, "No scores available", fontsize=12, ha='center', transform=self.ax.transAxes, color='white')
        
        self.canvas.draw()

    def update_trend(self, scores):
        if scores and len(scores) >= 2:
            try:
                score_values = [int(entry['score']) for entry in scores]
                first, last = score_values[0], score_values[-1]
                current_improve = ((last - first) / first) * 100 if first != 0 else 0
                intervals = len(score_values) - 1
                avg_increase = ((last - first) / intervals) if intervals > 0 else 0
                predicted_improve = (avg_increase / first) * 100 if first != 0 else 0
                self.crnt_improve_labl.configure(text=f"Current Trend: {current_improve:.2f}%")
                self.predicted_improve_labl.configure(text=f"Predicted Next Increase: {predicted_improve:.2f}%")
            except Exception as ex:
                self.crnt_improve_labl.configure(text="Current Trend: N/A")
                self.predicted_improve_labl.configure(text="Predicted Next Increase: N/A")
                print(f"Error computing trend: {ex}")
        else:
            self.crnt_improve_labl.configure(text="Current Trend: N/A")
            self.predicted_improve_labl.configure(text="Predicted Next Increase: N/A")

    def get_recom(self):
        recommendations = []
        try:
            with open(self.methods_file, 'r') as f:
                methods = json.load(f)
        except Exception as e:
            methods = {}
        selected_struggles = [key for key, var in self.struggle_vars.items() if var.get()]
        for struggle in selected_struggles:
            if struggle in methods:
                method = methods[struggle]
                rec_text = (f"Recommended Method: {method['name']}\n"
                            f"Description: {method['description']}\nSteps:\n")
                rec_text += "\n".join(f"• {step}" for step in method['steps'])
                recommendations.append((rec_text, method.get('resource', '')))
        return recommendations

    def linear_search_feelings(self, user_input):
        try:
            with open(self.feelings_file, 'r') as f:
                feelings_dt = json.load(f)
                user_words = user_input.lower().split()
                recom = []
                for feeling in feelings_dt:
                    if feeling.lower() in user_words:
                        recom.extend(feelings_dt[feeling])
                return recom
        except Exception as e:
            return []

    def get_performance_recom(self, scores):
        if not scores:
            return []
        try: # basic mathematical calculation 
            score_values = [int(entry['score']) for entry in scores]
            avg = sum(score_values) / len(score_values)
        except Exception as e:
            avg = 0
        recom = []
        if avg >= 70:
            recom.append("High Performance Detected!")
            recom.append("- Use advanced practice questions")
            recom.append("- Teach concepts to peers")
        elif 50 <= avg < 70:
            recom.append("Moderate Understanding")
            recom.append("- Focus on weak areas")
            recom.append("- Use spaced repetition")
        else:
            recom.append("Needs Improvement")
            recom.append("- Daily fundamental reviews")
            recom.append("- Seek teacher assistance")
        return recom

    def generate_recom(self):
        # Clear previous recommendations
        self.analysis_txt.delete("1.0", tk.END)
        self.method_txt.delete("1.0", tk.END)
        self.suggestion_text.delete("1.0", tk.END)
        for widget in self.resource_button_frm.winfo_children():
            widget.destroy()
        
        subject = self.subj_var.get()
        try:
            with open(self.scores_file, 'r') as f:
                data = json.load(f)
                subject_data = data.get(subject, [])
                last_three = subject_data[-3:]
        except Exception as e:
            last_three = []
        
        #Performance Analysis 
        performance_recs = self.get_performance_recom(last_three)
        if performance_recs:
            for rec in performance_recs:
                self.analysis_txt.insert(tk.END, f"• {rec}\n")
        else:
            self.analysis_txt.insert(tk.END, "No performance analysis available.\n")
        
        #Struggle-Specific Methods 
        struggle_recs = self.get_recom()
        if struggle_recs:
            for rec_text, resource in struggle_recs:
                self.method_txt.insert(tk.END, rec_text + "\n")
                if resource:
                    btn = ttk.Button(self.resource_button_frm, text="Go to Resource",
                                     command=lambda url=resource: webbrowser.open(url))
                    btn.pack(pady=2, anchor="w")
                self.method_txt.insert(tk.END, "---------------------\n")
        else:
            self.method_txt.insert(tk.END, "No specific struggle selected.\n")
        
        #Feeling-Based Suggestions
        feeling_input = self.feeling_entry.get().strip()
        feeling_recs = self.linear_search_feelings(feeling_input)
        if feeling_recs:
            for rec in feeling_recs:
                self.suggestion_text.insert(tk.END, f"• {rec}\n")
        else:
            self.suggestion_text.insert(tk.END, "No feeling-based suggestions available.\n")

    def recom_loop(self):
        self.generate_recom()
        self.after(2000, self.recom_loop)

if __name__ == "__main__":
    app = StudyAdvisorApp()
    app.mainloop()
