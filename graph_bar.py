import mysql.connector
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.interpolate import CubicSpline
from datetime import datetime

# My db settings 
DB_STUFF = {
    'user': 'root',  
    'password': '',  
    'host': 'localhost',  
    'database': 'nea',   
}

class ScoreVisualizer(tk.Frame):
    def __init__(self, parent, user_id, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)  
        
        # Make sure user_id is an int not a tuple (was getting weird errors before)
        self.user_id = int(user_id) if isinstance(user_id, (int, str)) else user_id[0]
        
        # Keep track of callbacks so they don't disappear
        self.callbacks = []

        # Dark theme setup
        self.configure(bg='#141414')
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#141414')
        self.style.configure('TLabelframe', background='#141414', foreground='white')
        self.style.configure('TLabelframe.Label', background='#141414', foreground='white')
        self.style.configure('TCheckbutton', background='#141414', foreground='black')
        self.style.configure('TCombobox', background='#141414', foreground='white')

        # Get the data from DB
        my_data = self.load_data()
        if not my_data:
            
            print("No data found! Using empty dataset instead")
            my_data = {}
            
        sorted_stuff = self.bubble_sort(my_data)  # sort using my bubble sort implementation
        
        # Main container
        self.main_frm = tk.Frame(self, bg='#141414')
        self.main_frm.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        
        self.plot_frm = tk.Frame(self.main_frm)
        self.plot_frm.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        
        self.option_frm = tk.Frame(self.main_frm, bg='#141414')
        self.option_frm.pack(side=tk.BOTTOM, fill=tk.Y, padx=10, pady=10)
        
        # Checkboxes for subject selection
        subj_vars = self.Subject_slctr(self.option_frm, sorted_stuff, 
                                        lambda: self.update_plot(sorted_stuff, self.plot_frm, subj_vars, time_range, yr))
        
        
        time_range = self.month_range_slctr(self.option_frm, 
                                            lambda: self.update_plot(sorted_stuff, self.plot_frm, subj_vars, time_range, yr))
        
    
        yr = self.year_slctr(self.option_frm, 
                                lambda: self.update_plot(sorted_stuff, self.plot_frm, subj_vars, time_range, yr))
        
        # Show latest scores in a box
        self.last_scores(self.option_frm, sorted_stuff)

        # Draw initial graph with everything selected
        self.update_plot(sorted_stuff, self.plot_frm, subj_vars, time_range, yr)
        
        # Clean up when closing
        self.bind("<Destroy>", self.cleanup)
    
    def cleanup(self, event=None):
        
        
        for cb in self.callbacks:
            try:
                self.after_cancel(cb)
            except Exception:
                pass
        
        # Close matplotlib figures
        plt.close('all')
    
    def last_scores(self, parent, data):
        # This shows the most recent scores for quick reference
        latest_frame = ttk.LabelFrame(parent, text="Latest Scores", style='TLabelframe')
        latest_frame.pack(side=tk.RIGHT, fill=tk.X, padx=10, pady=10)

    
        self.style.configure('Latest.TLabel', 
                           background='#141414', 
                           foreground='white',
                           font=('Arial', 10))

        # Find recent scores
        latest = {}
        for subj, scores in data.items():
            if scores:
                
                sorted_scores = sorted(scores, 
                                    key=lambda x: (x['year'], x['month']), 
                                    reverse=True)
                last_score = sorted_scores[0]
                latest[subj] = f"{last_score['score']} ({self.get_month_name(last_score['month'])} {last_score['year']})"

        # Show the scores in a graph
        for col, (subj, score) in enumerate(latest.items()):
            ttk.Label(latest_frame, 
                    text=f"{subj}:", 
                    style='Latest.TLabel'
                    ).grid(row=0, column=col, sticky='w', padx=5, pady=2)
            
            ttk.Label(latest_frame, text=score, style='Latest.TLabel',foreground='#1f77b4' ).grid(row=1, column=col, sticky='e', padx=5, pady=2)

        
        for kid in latest_frame.winfo_children():
            kid.grid_configure(padx=5, pady=2)
    
    @staticmethod
    def get_month_name(month_num):
        months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
        return months[month_num - 1]  # adjust for 0-indexing

    @staticmethod
    def get_current_year_and_month():
        now = datetime.now()
        return now.year, now.month

    @staticmethod
    def get_time_range_months(year, time_range, current_year, current_month):
        # This was tricky to get right!
        if year == current_year:
            # Don't show future months
            if time_range == "3 Months":
                start = max(1, current_month - 2)
                return list(range(start, current_month + 1))
            elif time_range == "6 Months":
                start = max(1, current_month - 5)
                return list(range(start, current_month + 1))
            else:  # Full Year
                return list(range(1, current_month + 1))
        else:
            # For past/future years show different parts of the year
            if time_range == "3 Months":
                return list(range(10, 13)) if year < current_year else list(range(1, 4))
            elif time_range == "6 Months":
                return list(range(7, 13)) if year < current_year else list(range(1, 7))
            else:  # Full Year
                return list(range(1, 13))

    
    def load_data(self):
        # Get scores from database
        try:
            # Connect to MySQL
            conn = mysql.connector.connect(**DB_STUFF)
            cursor = conn.cursor(dictionary=True)
            
            # Debug stuff
            print(f"Looking up user_id: {self.user_id} (type: {type(self.user_id)})")
            
            # Get subjects first
            cursor.execute("SELECT subject_id, subject_name FROM subjects WHERE user_id = %s", (self.user_id,))
            subjects = cursor.fetchall()
            
            # Start with empty lists for each subject
            all_data = {subject['subject_name']: [] for subject in subjects}
            
            # Then get scores if we have subjects
            if subjects:
                subj_ids = [subject['subject_id'] for subject in subjects]
                # Make SQL placeholders
                placeholders = ', '.join(['%s'] * len(subj_ids))
                
                cursor.execute(f"""
                    SELECT subjects.subject_name, scores.month, scores.year, scores.score 
                    FROM scores 
                    JOIN subjects ON subjects.subject_id = scores.subject_id 
                    WHERE subjects.subject_id IN ({placeholders})
                """, tuple(subj_ids))
                
                results = cursor.fetchall()
                print(f"Found {len(results)} scores for {len(subjects)} subjects")
                
                # Organize into our data structure
                for row in results:
                    subj = row['subject_name']
                    month = row['month']
                    year = row['year']
                    score = row['score']
                    
                    all_data[subj].append({'month': month, 'year': year, 'score': score})
            
            return all_data
            
        except mysql.connector.Error as err:
            print(f"DB Error: {err}")
            return {}
        except Exception as e:
            print(f"Something went wrong: {e}")
            return {}
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
                print("DB connection closed")

    @staticmethod
    def bubble_sort(data):  # Used bubble sort 
        sorted_data = {}
        for subj, scores in data.items():
            sorted_scores = scores.copy()
            n = len(sorted_scores)
            for i in range(n):
                for j in range(0, n-i-1):
                    if sorted_scores[j]['month'] > sorted_scores[j+1]['month']:
                        sorted_scores[j], sorted_scores[j+1] = sorted_scores[j+1], sorted_scores[j]
            sorted_data[subj] = sorted_scores
        return sorted_data

    def plot_scores(self, data, frame, selected_subjects, time_range, year):
        # Clear old graph
        for widget in frame.winfo_children():
            widget.destroy()
        
        # Stop memory leaks
        plt.close('all')
        
        # Dark theme looks way better
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # My colors - blue for Math, pink for Science, etc.
        colors = ['#1f77b4', '#ff69b4', '#ff4500', '#00cc00', '#9400d3', '#ff7f00']
        line_styles = ['-', '--', '-.', ':']
        
        # Match dark theme
        fig.patch.set_facecolor('#1a1a1a')
        ax.set_facecolor('#1a1a1a')
        
        current_year, current_month = self.get_current_year_and_month()
        months = self.get_time_range_months(year, time_range, current_year, current_month)
        
        # Fallback if something went wrong
        if not months:
            months = list(range(1, 13))
        
        month_names = [self.get_month_name(m) for m in months]
        x = np.arange(len(month_names))
        
        has_any_data = False
        plot_lines = []  # For legend
        

        # Handle both cases - with data and without


        if not data or not selected_subjects: 
            # Empty graph case
            empty_line, = ax.plot(x, [0] * len(x), label="No subjects available", 
                               marker='o', markersize=8, markerfacecolor='gray',
                               markeredgecolor='white', markeredgewidth=1.5,
                               color='gray', linestyle='--', linewidth=1.5)
            plot_lines.append(empty_line)
            ax.text(0.5, 0.5, "No subjects or data available", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, color='white', fontsize=14)
        else:
            # Plot each selected subject
            for i, subj in enumerate(selected_subjects):
                if subj not in data:
                    continue
                    
                scores = data[subj]
                my_color = colors[i % len(colors)]
                my_style = line_styles[i % len(line_styles)]
                
                # Only show scores from selected year
                year_scores = [entry for entry in scores if entry['year'] == year]
                
                # Always show a line even with no scores
                if not year_scores:
                    print(f"No {year} scores for {subj}, showing zero line")
                    # Empty line with markers
                    line, = ax.plot(x, [0] * len(x), label=f"{subj}", 
                                  marker='o', markersize=8, markerfacecolor=my_color,
                                  markeredgecolor='white', markeredgewidth=1.5,
                                  color=my_color, linestyle='--', linewidth=2)
                    plot_lines.append(line)
                    has_any_data = True
                    continue
                
                has_any_data = True
                
                
                score_month = {entry['month']: entry['score'] for entry in year_scores}
                
                # Get score for each month (0 if missing)
                values = [score_month.get(m, 0) for m in months]
                
                # Simple line for 1 point
                if len(values) < 2:
                    line, = ax.plot(x, values, label=subj, marker='o', markersize=8,
                                  color=my_color, linestyle=my_style, linewidth=2)
                    plot_lines.append(line)
                else:
                    # Try to make a smooth curve 
                    try:
                        # This looks nicer than straight lines
                        spline = CubicSpline(x, values)
                        x_smooth = np.linspace(0, len(month_names)-1, 300)
                        y_smooth = spline(x_smooth)
                        
                        line, = ax.plot(x_smooth, y_smooth, label=subj, color=my_color, 
                                      linestyle=my_style, linewidth=2.5)
                        plot_lines.append(line)
                        # Add dots for actual data points
                        ax.scatter(x, values, s=50, color=my_color, edgecolor='#ffffff', 
                                linewidth=1, zorder=4)
                    except Exception as e:
                        print(f"Spline error: {e}")
                        # Just do regular line if spline fails
                        line, = ax.plot(x, values, label=subj, marker='o', markersize=8,
                                      color=my_color, linestyle=my_style, linewidth=2)
                        plot_lines.append(line)
            
            # Still show something even with no data for this year
            if not has_any_data and selected_subjects:
                # Zero lines for each subject
                for i, subj in enumerate(selected_subjects):
                    if subj not in data:
                        continue
                    my_color = colors[i % len(colors)]
                    line, = ax.plot(x, [0] * len(x), label=f"{subj}", 
                                  marker='o', markersize=8, markerfacecolor=my_color,
                                  markeredgecolor='white', markeredgewidth=1.5,
                                  color=my_color, linestyle='--', linewidth=2)
                    plot_lines.append(line)
                    has_any_data = True
                
                # Message to explain why it's empty
                ax.text(0.5, 0.5, "No scores for selected subjects in this time period", 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, color='white', fontsize=14)
        
        # Graph settings
        ax.set_ylim(-5, 105)  # Scores 0-100 with a bit of padding
        
        # Make text visible on dark bg
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        
        # Subtle grid
        ax.grid(color='#333333', linestyle='-', linewidth=0.5, alpha=0.8)
        
        # Add legend if we have any plots
        if plot_lines:
            legend = ax.legend(handles=plot_lines, facecolor='#1a1a1a', edgecolor='#404040', 
                            fontsize=10, labelcolor='white')
            if legend:
                for txt in legend.get_texts():
                    txt.set_color("white")

        ax.set_xlabel("Month")
        ax.set_ylabel("Score")
        ax.set_title(f"Student Scores for {year} ({time_range})")
        ax.set_xticks(x)
        ax.set_xticklabels(month_names, rotation=0)
        
        # Add to the frame
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def Subject_slctr(self, parent, data, update_callback):
        # Subject selector checkboxes
        checkbox_frame = ttk.LabelFrame(parent, text="Select Subjects")
        checkbox_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        style = ttk.Style()
        style.configure("White.TCheckbutton", 
                   foreground="white", 
                   background='#141414')
        
        subject_vars = {}
        
        if data:
            # Add checkboxes for each subject
            for subj in data.keys():
                var = tk.BooleanVar(value=True)  # checked by default
                cb = ttk.Checkbutton(checkbox_frame,
                                    text=subj, 
                                    variable=var,
                                    command=update_callback,
                                    style="White.TCheckbutton")
                cb.pack(anchor=tk.W, padx=5, pady=2)
                subject_vars[subj] = var
        else:
            # Handle no data case
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(checkbox_frame,
                                text="No subjects", 
                                variable=var,
                                state="disabled",
                                style="White.TCheckbutton")
            cb.pack(anchor=tk.W, padx=5, pady=2)
            subject_vars["No subjects"] = var
            
            # Message explaining why
            tk.Label(checkbox_frame, text="No subject data available", 
                     bg='#141414', fg='gray').pack(pady=5)
                     
        return subject_vars

    def month_range_slctr(self, parent, update_callback):
        # Time range selector
        time_frame = ttk.LabelFrame(parent, text="Select Time Range")
        time_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        time_range = tk.StringVar(value="6 Months")  # default to 6 months
        choices = ["Full Year", "6 Months", "3 Months"]
        
        dropdown = ttk.Combobox(time_frame, textvariable=time_range, values=choices, state="readonly")
        dropdown.pack(padx=5, pady=5)
        
        # Need to keep ref to callback
        self.dropdown_callback = lambda event: update_callback()
        dropdown.bind("<<ComboboxSelected>>", self.dropdown_callback)
        
        return time_range

    def year_slctr(self, parent, update_callback):
        # Year selector
        year_frame = ttk.LabelFrame(parent, text="Select Year")
        year_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        current_year, _ = self.get_current_year_and_month()
        year = tk.IntVar(value=current_year)
        # Might need to add more years later
        years = [2024, 2025, 2026]  
        
        dropdown = ttk.Combobox(year_frame, textvariable=year, values=years, state="readonly")
        dropdown.pack(padx=5, pady=5)
        
        # Keep ref to callback
        self.year_callback = lambda event: update_callback()
        dropdown.bind("<<ComboboxSelected>>", self.year_callback)
        
        return year

    def update_plot(self, data, frame, subject_vars, time_range, year):
        # Figure out which subjects are checked
        selected = [s for s, var in subject_vars.items() if var.get()]
        # And redraw everything
        self.plot_scores(data, frame, selected, time_range.get(), year.get())