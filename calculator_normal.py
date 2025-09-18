import mysql.connector
import json
import os
from datetime import datetime, timedelta
import random
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

def load_json(filename, default_data):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file)
    return default_data

def save_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def save_plan(user_id, plan):
    conn = mysql.connector.connect(host="localhost", user="root", password="", database="nea")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE user_id = %s", (user_id,))  # Clear old plans for the user
    for date, time, title in plan:
        cursor.execute("INSERT INTO events (user_id, date, time, title) VALUES (%s, %s, %s, %s)", (user_id, date, time, title))
    conn.commit()
    conn.close()

def get_user_avl(user_id):
    #Load availability data 
    default_aval = {day: [] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
    
    try:
        # First try to load from user-specific JSON file
        if not os.path.exists("availability_data"):
            os.makedirs("availability_data")
            
        filename = f"availability_data/availability_{user_id}.json"
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            try:
                with open(filename, "r") as file:
                    data = json.load(file)
                    if isinstance(data, dict) and all(day in data for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
                        return data
            except json.JSONDecodeError:
                print(f"Warning: Invalid JSON in {filename}")
        
        # If file doesn't exist, try to load from database as a fallback
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="", database="nea")
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT day, hours FROM availability WHERE user_id = %s", (user_id,))
            results = cursor.fetchall()
            conn.close()
            
            if results:
                # Convert database results to our format
                avail = {day: [] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
                for row in results:
                    day = row['day']
                    hours_str = row['hours']
                    
                    # Parse hours from LONGTEXT format
                    if hours_str and hours_str.strip():
                        try:
                            # Try to parse as comma-separated values first
                            hours = [int(h.strip()) for h in hours_str.split(',') if h.strip().isdigit()]
                        except:
                            # If parsing fails, use empty list
                            hours = []
                    else:
                        hours = []
                    
                    avail[day] = hours
                
                # Save to file for future use
                with open(filename, "w") as file:
                    json.dump(avail, file, indent=4)
                
                return avail
        except Exception as e:
            print(f"Warning: Database access failed: {e}")
        
        
        if os.path.exists("availability.json") and os.path.getsize("availability.json") > 0:
            try:
                with open("availability.json", "r") as file:
                    avail_data = json.load(file)
                    if isinstance(avail_data, dict):
                        return avail_data
            except json.JSONDecodeError:
                print("Warning: Invalid JSON in availability.json")
    except Exception as e:
        print(f"Error loading availability: {e}")
    
    
    return default_aval

def subj_weight(weight):
    if isinstance(weight, list):
        # Extract the latest score entry (highest year/month)
        latest_entry = max(weight, key=lambda x: (x["year"], x["month"]))
        return 100 - latest_entry["score"]  # Prioritize LOW scores
    return 100 - int(weight)

def subj_scores(user_id=1):
    #Get subject scores from database or fallback to file-based storage
    try:
        # First try to get scores from the database
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="nea")
        cursor = conn.cursor(dictionary=True)
        
        # Get subjects with their latest scores
        cursor.execute("""
            SELECT s.subject_name, sc.score, sc.month, sc.year
            FROM subjects s
            LEFT JOIN (
                SELECT subject_id, score, month, year,
                       ROW_NUMBER() OVER (PARTITION BY subject_id ORDER BY year DESC, month DESC) as rn
                FROM scores
            ) sc ON s.subject_id = sc.subject_id AND sc.rn = 1
            WHERE s.user_id = %s
        """, (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        if results:
            return {row['subject_name']: subj_weight(row['score']) for row in results if row['score'] is not None}
        
       
        
       
        
    except Exception as e:
        print(f"Error getting subject scores: {e}")
    
    
    return {}


def check_setup(user_id):
    
    daily_hours = get_user_avl(user_id)
    

    conn = mysql.connector.connect(host="localhost", user="root", password="", database="nea")
    cursor = conn.cursor(dictionary=True)
        
        # Get subjects with their latest scores
    cursor.execute("""
            SELECT subject_name FROM subjects WHERE user_id = %s
        """, (user_id,))
        
    subjects = cursor.fetchall()
    conn.close()
    
    # Check if we have any available hours and subjects for this user
    has_hours = any(len(hours) >= 0 for hours in daily_hours.values())
    has_subjects = len(subjects) > 0
    
    return not (has_hours and has_subjects)

def complete_setup(user_id, callback=None):
    #Run the setup window if needed and then call the callback
    if check_setup(user_id):
        setup_window(user_id, callback)
    else:
        tm_allocation(user_id)
        if callback:
            callback()

def setup_window(user_id, callback=None):
    # setup window (new users)
    global callback_function
    callback_function = callback
    
    setup_window = ctk.CTk()
    setup_window.title("Initial Setup")
    setup_window.geometry("600x500")
    
    
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    main_frm = ctk.CTkFrame(setup_window)
    main_frm.pack(fill="both", expand=True, padx=20, pady=20)
    
    
    welcome_labl = ctk.CTkLabel(main_frm, text="Welcome to Eclipse Learning!", font=("Arial", 18, "bold"))
    welcome_labl.pack(pady=(10, 20))
    
    info_labl = ctk.CTkLabel(main_frm, text="Please complete your initial setup to get started.", font=("Arial", 14))
    info_labl.pack(pady=(0, 20))
    
    
    tabview = ctk.CTkTabview(main_frm, width=550, height=350)
    tabview.pack(fill="both", expand=True, padx=20, pady=20)
   
    tab_subjs = tabview.add("Subjects")
    tab_avail = tabview.add("Availability")
    
    
    subjects_frm = ctk.CTkFrame(tab_subjs)
    subjects_frm.pack(fill="both", expand=True, padx=20, pady=20)
    
    ctk.CTkLabel(subjects_frm, text="Add your subjects:", font=("Arial", 14, "bold")).pack(pady=(0, 10))
    
    
    subj_entry_frm = ctk.CTkFrame(subjects_frm)
    subj_entry_frm.pack(fill="x", pady=10)
    
    subj_entry = ctk.CTkEntry(subj_entry_frm, placeholder_text="Enter subject name", width=300)
    subj_entry.pack(side="left", padx=10)
    
    subjects_list = []
    
    def add_subject():
        subject = subj_entry.get().strip()
        if subject and subject not in subjects_list:
            subjects_list.append(subject)
            subj_entry.delete(0, 'end')
            update_subj_disp()
    
    add_btn = ctk.CTkButton(subj_entry_frm, text="Add", command=add_subject)
    add_btn.pack(side="right", padx=10)
    
    # Subjects display frame
    subj_disp_frm = ctk.CTkFrame(subjects_frm)
    subj_disp_frm.pack(fill="both", expand=True, pady=10)
    
    def update_subj_disp():
        # Clear current display
        for widget in subj_disp_frm.winfo_children():
            widget.destroy()
        
        # Show subjects
        for i, subject in enumerate(subjects_list):
            subject_frame = ctk.CTkFrame(subj_disp_frm)
            subject_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(subject_frame, text=subject, width=300).pack(side="left", padx=10)
            
            # Add remove button
            remove_btn = ctk.CTkButton(subject_frame, text="Remove", width=80, 
                                    command=lambda s=subject: remove_subj(s))
            remove_btn.pack(side="right", padx=10)
    
    def remove_subj(subject):
        subjects_list.remove(subject)
        update_subj_disp()
    
    
    availability_frm = ctk.CTkFrame(tab_avail)
    availability_frm.pack(fill="both", expand=True, padx=20, pady=20)
    
    ctk.CTkLabel(availability_frm, text="Set your weekly availability:", 
              font=("Arial", 14, "bold")).pack(pady=(0, 10))
    
    ctk.CTkLabel(availability_frm, text="Enter time ranges for each day (e.g., 9-12, 14-16)", 
              font=("Arial", 12)).pack(pady=(0, 5))
              
    ctk.CTkLabel(availability_frm, text="Or enter '0' to indicate no availability for that day", 
              font=("Arial", 12)).pack(pady=(0, 10))
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_entries = {}
    
    for day in days:
        day_frm = ctk.CTkFrame(availability_frm)
        day_frm.pack(fill="x", pady=5)
        
        ctk.CTkLabel(day_frm, text=day, width=100).pack(side="left", padx=10)
        
        entry = ctk.CTkEntry(day_frm, placeholder_text="e.g., 9-12, 14-16 or 0", width=300)
        entry.pack(side="right", padx=10)
        
        day_entries[day] = entry
    
    # Save button
    def save_setup():
        # Validate subjects
        if not subjects_list:
            messagebox.showerror("Error", "Please add at least one subject.")
            return
        
        # Validate and process availability
        avail_data = {}
        for day, entry in day_entries.items():
            text = entry.get().strip()
            times = []
            
            
            if text == "0":
                
                times = []  
            elif text:  
                ranges = [r.strip() for r in text.split(',')]
                for time_range in ranges:
                    if '-' in time_range:
                        try:
                            start, end = map(int, time_range.split('-'))
                            if start < end and 0 <= start <= 23 and 1 <= end <= 24:
                                times.extend(range(start, end))
                            else:
                                messagebox.showerror("Error", f"Invalid time range for {day}: {time_range}\nHours must be between 0-23 and end time must be greater than start time.")
                                return
                        except ValueError:
                            messagebox.showerror("Error", f"Invalid format for {day}: {time_range}\nUse format like '9-12'")
                            return
            
            avail_data[day] = times
        
        try:
            # Save subjects to database
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="nea"
            )
            cursor = conn.cursor()
            
            # Add subjects to the database
            for subject in subjects_list:
                try:
                    cursor.execute("INSERT INTO subjects (user_id, subject_name) VALUES (%s, %s)", 
                                (user_id, subject))
                except:
                    # Subject might already exist, skip the error
                    pass
                
            
            if not os.path.exists("availability_data"):
                os.makedirs("availability_data")
                
            with open(f"availability_data/availability_{user_id}.json", "w") as file:
                json.dump(avail_data, file, indent=4)
            
            
            try:
                # Clear existing records for this user
                cursor.execute("DELETE FROM availability WHERE user_id = %s", (user_id,))
                
                
                for day, hours in avail_data.items():
                    if not hours:
                        # If no hours, insert with NULL for hours
                        cursor.execute(
                            "INSERT INTO availability (user_id, day, hours) VALUES (%s, %s, NULL)",
                            (user_id, day)
                        )
                    else:
                        
                        if len(hours) > 10:
                            hours = hours[:10]  
                        hours_str = ','.join(str(h) for h in hours)
                        cursor.execute(
                            "INSERT INTO availability (user_id, day, hours) VALUES (%s, %s, %s)",
                            (user_id, day, hours_str)
                        )
            except Exception as e:
                print(f"Warning: Could not save availability to database: {e}")
                # Continue with file-based approach only
            
            conn.commit()
            conn.close()
            
            # Close the setup window
            setup_window.destroy()
            
            # Run the calculate_time_allocation function with the new data
            # Wrap in try-except to prevent crashes
            try:
                tm_allocation(user_id)
            except Exception as e:
                print(f"Warning: Failed to calculate time allocation: {e}")
            
            # If callback function was provided, call it
            if callback_function is not None:
                callback_function()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save setup: {e}")
            return
    
    save_button = ctk.CTkButton(main_frm, text="Save and Continue", 
                            command=save_setup, 
                            font=("Arial", 14, "bold"))
    save_button.pack(pady=20)
    
    # Run the setup window
    setup_window.mainloop()

def tm_allocation(user_id):
    print(f"Welcome to the Study Time Allocation Program for user {user_id}!")
    
    # Get availability and subjects
    daily_hours = get_user_avl(user_id)
    subjects = subj_scores(user_id)
    
    total_time = sum(len(hours) for hours in daily_hours.values())
    print(f"\nTotal weekly study time: {total_time} hours")
    
    # Check if we have any subjects or available hours
    if not subjects:
        print("Error: No subjects found. Please add subjects first.")
        return False
    
    if total_time == 0:
        print("Error: No available hours found. Please set your availability first.")
        return False
    
    # Use the stored weight directly
    adjusted_weights = {subject: score for subject, score in subjects.items()}
    total_weight = sum(adjusted_weights.values())
    
    if total_weight == 0:
        print("Warning: Total weight is 0, using equal weights for all subjects")
        adjusted_weights = {subject: 1 for subject in subjects}
        total_weight = len(subjects)
    
    weighted_allocation = {
        subject: max(round((weight / total_weight) * total_time), 1)
        for subject, weight in adjusted_weights.items()
    }
    
    allocation_sum = sum(weighted_allocation.values())
    if allocation_sum != total_time and weighted_allocation:  # Make sure weighted_allocation is not empty
        difference = total_time - allocation_sum
        # Safely get the weakest subject or just use the first subject if they're all equal
        try:
            weakest_subject = min(weighted_allocation, key=weighted_allocation.get)
            weighted_allocation[weakest_subject] += difference
        except ValueError:  # In case weighted_allocation is empty
            print("Warning: Could not adjust allocation, using equal allocation")
            if subjects:
                equal_time = total_time // len(subjects)
                weighted_allocation = {subject: equal_time for subject in subjects}
    
    # Print allocation for debugging
    print("\nTime allocation per subject:")
    for subject, hours in weighted_allocation.items():
        print(f"{subject}: {hours} hours")

    start_date = datetime.today()
    start_week = start_date - timedelta(days=start_date.weekday())
    
    dly_subject_allocation = []
    remaining_hours = weighted_allocation.copy()

    # Map day index to day name
    day_map = {
        0: "Monday", 1: "Tuesday", 2: "Wednesday", 
        3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"
    }

    for i in range(7):  # Iterate through all 7 days
        day_name = day_map[i]
        hours = daily_hours.get(day_name, [])
        
        if not hours:
            continue
            
        date = (start_week + timedelta(days=i)).strftime('%Y-%m-%d')
        slot_index = 0
        available_subjects = sorted(remaining_hours.keys(), key=lambda x: remaining_hours[x], reverse=True)
        
        while slot_index < len(hours) and available_subjects:
            for subject in available_subjects:
                if remaining_hours[subject] > 0:
                    start_time = hours[slot_index]
                    end_time = start_time + 1
                    time_str = f"{start_time:02}:00:00"
                    dly_subject_allocation.append((date, time_str, subject))
                    remaining_hours[subject] -= 1
                    
                    if (slot_index + 1 < len(hours) and remaining_hours[subject] > 0 and 
                        hours[slot_index + 1] == end_time and random.random() < 0.5):
                        start_time = hours[slot_index + 1]
                        end_time = start_time + 1
                        time_str = f"{start_time:02}:00:00"
                        dly_subject_allocation.append((date, time_str, subject))
                        remaining_hours[subject] -= 1
                        slot_index += 1
                    
                    slot_index += 1
                    break
            
            # Update available subjects list
            available_subjects = [s for s in available_subjects if remaining_hours[s] > 0]
            if slot_index >= len(hours) or not available_subjects:
                break
    
    save_plan(user_id, dly_subject_allocation)
    print("\nTime Allocation for the Week:")
    for date, time, title in dly_subject_allocation:
        print(f"{date} - {time}: {title}")
    
    print("\nGood luck with your studies!")
    return True

