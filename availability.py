import customtkinter as ctk
from tkinter import messagebox
import json
import re
import os
import mysql.connector
from calculator_normal import tm_allocation

class AvailabilityEditor(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.txt_entries = {}
        self.user_id = user_id
        self.avl = self.load_data_avl()
        self.ui()
    
    def load_data_avl(self):
        #Load from db then if that fails load from file
        
        default_avl = {day: [] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
        
        # First try loading from database
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="nea"
            )
            cursor = conn.cursor()
            
            
            cursor.execute("SELECT day, hours FROM availability WHERE user_id = %s", (self.user_id,))
            results = cursor.fetchall()
            
            if results:
                db_avl = default_avl.copy()
                for day, hours_str in results:
                    # Default to empty list (which means "0" in the UI)
                    hours_list = []
                    
                    # Only try to parse if hours is not NULL and not empty
                    if hours_str:
                        try:
                            # Convert the comma-separated string back to a list of integers
                            hours_list = [int(h) for h in hours_str.split(',') if h.strip()]
                        except (ValueError, AttributeError) as e:
                            print(f"Error parsing hours for {day}: {e}")
                    
                    # Store the hours list (empty or with values)
                    db_avl[day] = hours_list
                
                print(f"Loaded availability from database for user {self.user_id}: {db_avl}")
                return db_avl
                
        except Exception as e:
            print(f"Error loading availability from database: {e}")
        finally:
            if 'conn' in locals() and conn and conn.is_connected():
                cursor.close()
                conn.close()
        
        # If database load failed, try loading from file
        try:
            # Try to load from user-specific JSON file
            filename = f"availability_data/availability_{self.user_id}.json"
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, "r") as file:
                    data = json.load(file)
                    print(f"Loaded availability from file for user {self.user_id}: {data}")
                    return data
        except Exception as e:
            print(f"Error loading availability from file: {e}")
        
        print(f"Using default availability for user {self.user_id}")
        return default_avl
    
    def save_data(self, data):
        #Save availability 
        try:
            try:
                # First attempt to save to database
                self.save_DB(data)
            except Exception as e:
                print(f"Warning: Couldn't save to database, using file storage only: {e}")
                # If database fails, make sure we save to file
                self.save_file(data)
                
            messagebox.showinfo("Success", "Availability saved successfully!")
            
            # Run the time allocation calculation
            tm_allocation(self.user_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save availability: {e}")
    
    def save_DB(self, data):
        """Attempt to save to database - this is a best-effort approach"""
        conn = None
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="nea"
            )
            cursor = conn.cursor()
            
            # First try removing existing records for this user
            cursor.execute("DELETE FROM availability WHERE user_id = %s", (self.user_id,))
            
            # Now insert new records
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
                hours = data.get(day, [])
                
                if not hours:
                    # No hours for this day 
                    cursor.execute(
                        "INSERT INTO availability (user_id, day, hours) VALUES (%s, %s, NULL)",
                        (self.user_id, day)
                    )
                    print(f"Saved {day} with NULL hours to database")
                else:
                    
                    if len(hours) > 24:  # Max 24 hours in a day
                        hours = hours[:24]
                    
                    hours_str = ','.join(str(h) for h in hours)
                    cursor.execute(
                        "INSERT INTO availability (user_id, day, hours) VALUES (%s, %s, %s)",
                        (self.user_id, day, hours_str)
                    )
                    print(f"Saved {day} with hours {hours_str} to database")
            
            conn.commit()
            print(f"Successfully saved all availability data to database for user {self.user_id}")
            
            #  save to file as backup
            self.save_file(data)
            
        except Exception as e:
            print(f"Database save error: {e}")
            if conn:
                conn.rollback()
            raise  

        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    
    def save_file(self, data):
        
        try:
            os.makedirs("availability_data", exist_ok=True)
            filename = f"availability_data/availability_{self.user_id}.json"
            with open(filename, "w") as file:
                json.dump(data, file)
            print(f"Saved availability data to file: {filename}")
        except Exception as e:
            print(f"Error saving to file: {e}")
    
    def update(self):
        updated_data = {}
        for day, entry in self.txt_entries.items():
            text = entry.get().strip()
            times = []
            
            # Check for "0" entry which explicitly indicates no availability
            if text == "0":
                # User explicitly says not available on this day
                times = []  # Empty list indicates no availability
            elif text:
                matches = re.findall(r"(\d{1,2})-(\d{1,2})", text)
                for start, end in matches:
                    start, end = int(start), int(end)
                    if start < end:
                        times.extend(range(start, end))
            
            updated_data[day] = times
        self.save_data(updated_data)
    
    def ui(self):
        frm = ctk.CTkFrame(self)
        frm.pack(padx=10, pady=10, fill="both", expand=True)

        ctk.CTkLabel(frm, text="Enter availability (e.g., 9-12, 14-16 or 0 for no availability):", 
                    font=("Arial", 12, "bold")).pack()

        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            row_frame = ctk.CTkFrame(frm)
            row_frame.pack(fill="x", pady=2)
            ctk.CTkLabel(row_frame, text=day, font=("Arial", 10, "bold"), width=10).pack(side="left", padx=5)
            entry = ctk.CTkEntry(row_frame, width=150, height=10)
            
            # Get times from availability dictionary, defaulting to empty list
            existing_times = self.avl.get(day, [])
            
            # Print debug info
            print(f"Day: {day}, Times: {existing_times}")
            
            if not existing_times:
                # No times for this day
                entry.insert(0, "0")  # Insert "0" to indicate no availability
            else:
                # Sort times to ensure proper range creation
                existing_times.sort()
                
                # Group consecutive times into ranges
                time_ranges = []
                if existing_times:
                    start = existing_times[0]
                    current_end = start
                    
                    for i in range(1, len(existing_times)):
                        if existing_times[i] != existing_times[i - 1] + 1:
                            # End of a consecutive range
                            time_ranges.append(f"{start}-{current_end + 1}")
                            start = existing_times[i]
                        
                        current_end = existing_times[i]
                    
                    # Add the final range
                    time_ranges.append(f"{start}-{current_end + 1}")
                
                entry.insert(0, ", ".join(time_ranges))
            
            entry.pack(side="right", padx=5)
            self.txt_entries[day] = entry

        ctk.CTkButton(self, text="Save", command=self.update, font=("Arial", 10, "bold"),).pack(pady=10)