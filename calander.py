import customtkinter as ctk
import tkinter as tk
from tkinter import simpledialog, messagebox
import mysql.connector
import datetime
from calculator_normal import tm_allocation


class CustomCalendar(ctk.CTkFrame):
    
    def __init__(self, parent, user_id, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        tm_allocation(user_id)

        self.user_id = user_id
        
        # Set overall appearance
        self.configure(fg_color="#1E1E2E")  
        
        
        self.header_frm = ctk.CTkFrame(self, fg_color="#1E1E2E", corner_radius=0)
        self.header_frm.pack(fill="x", padx=20, pady=(20, 10))
        
        
        title_lbl = ctk.CTkLabel(self.header_frm, text="My Schedule", font=("Arial", 24, "bold"), text_color="#EAEAEA")
        title_lbl.pack(side="left")
        
        
        quick_add_btn = ctk.CTkButton(self.header_frm,text="+ Add Event",font=("Arial", 14),fg_color="#7C3AED",  hover_color="#6D28D9",corner_radius=8,width=120,height=36,command=lambda: self.add_event(None, None)  )
        quick_add_btn.pack(side="right")

        self.DB()  # DB

        # Days and time slots 
        self.days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.hours = [
            "07:00 AM", "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM",
            "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM",
            "05:00 PM", "06:00 PM", "07:00 PM", "08:00 PM", "09:00 PM",
            "10:00 PM", "11:00 PM", "12:00 AM"
        ]

        
        tdy = datetime.datetime.today()
        self.tdy_day = tdy.weekday()  
        self.tdy_date = tdy.date()  

        
        tdy = datetime.datetime.today()
        self.strt_week = tdy - datetime.timedelta(days=tdy.weekday())

        
        self.time_frm = ctk.CTkFrame(self, corner_radius=12, fg_color="#282838", height=60)
        self.time_frm.pack(padx=20, pady=(5, 15), fill="x")

        
        self.prev_week_btn = ctk.CTkButton(self.time_frm, text="← Previous Week", command=self.previous_week, width=140,height=36,font=("Arial", 14),fg_color="#444454",hover_color="#555565",corner_radius=8)
        self.prev_week_btn.pack(side="left", padx=15, pady=10)

        
        self.week_labl = ctk.CTkLabel(self.time_frm, text=self.this_week(), font=("Arial", 16, "bold"), text_color="#EAEAEA")
        self.week_labl.pack(side="left", expand=True)

        self.next_week_btn = ctk.CTkButton(self.time_frm, text="Next Week →", command=self.next_week, width=140,height=36,font=("Arial", 14),fg_color="#444454",hover_color="#555565",corner_radius=8)
        self.next_week_btn.pack(side="right", padx=15, pady=10)

        
        self.time_frame = ctk.CTkFrame(self, fg_color="#1E1E2E", corner_radius=0)
        self.time_frame.pack(fill="x", padx=20)
        
        self.time_labl = ctk.CTkLabel(self.time_frame, text="", font=("Arial", 14), text_color="#AAAAAA")
        self.time_labl.pack(side="right", pady=5)
        
        # Today button
        self.today_btn = ctk.CTkButton(self.time_frame,text="Today",command=self.today,width=100,height=30,font=("Arial", 13),fg_color="#7C3AED",hover_color="#6D28D9",corner_radius=8)
        self.today_btn.pack(side="left", pady=5)

       
        self.calendar_frm = ctk.CTkFrame(self, fg_color="#1E1E2E", corner_radius=0)
        self.calendar_frm.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.calendar_frm = ctk.CTkFrame(self.calendar_frm, corner_radius=12, fg_color="#282838",border_width=1,border_color="#3E3E4E")
        self.calendar_frm.pack(fill="both", expand=True, padx=0, pady=0)

        self.events = {}  
        self.event_cell = {}  

        
        self.calendar()

        
        self.time()
    
    def this_week(self):
        
        start_date = self.strt_week.date()
        end_date = start_date + datetime.timedelta(days=6)
        
        
        if start_date.month == end_date.month:
            return f"{start_date.strftime('%B %d')} - {end_date.strftime('%d, %Y')}"
        else:
            return f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
    
    def today(self):
        
        today = datetime.datetime.today()
        self.strt_week = today - datetime.timedelta(days=today.weekday())
        self.week_labl.configure(text=self.this_week())
        self.calendar()

    def DB(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",        
            password="",        
            database="nea" 
        )
        self.cursor = self.conn.cursor()

    def calendar(self):
        # Clear 
        for widget in self.calendar_frm.winfo_children():
            widget.destroy()

        
        header_frm = ctk.CTkFrame(self.calendar_frm, fg_color="#282838", corner_radius=0, height=60)
        header_frm.grid(row=0, column=0, columnspan=8, sticky="ew")
        
        
        time = ctk.CTkLabel(header_frm,text="",width=80,fg_color="#282838",corner_radius=0)
        time.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

        
        for col, day in enumerate(self.days):
            day_date = self.strt_week + datetime.timedelta(days=col)
            
            
            today = day_date.date() == self.tdy_date
            
            
            header_frm = ctk.CTkFrame(self.calendar_frm,fg_color="#7C3AED" if today else "#373747",corner_radius=8 if today else 0)
            header_frm.grid(row=0, column=col + 1, padx=4, pady=4, sticky="nsew")
            
            
            day_name = ctk.CTkLabel(header_frm,text=day,font=("Arial", 14, "bold"),text_color="#FFFFFF")
            day_name.pack(pady=(8, 0))
            
            
            date_num = ctk.CTkLabel(header_frm,text=str(day_date.day),font=("Arial", 18, "bold"),text_color="#FFFFFF")
            date_num.pack(pady=(0, 8))

        # Create tiem slot
        for row, hour in enumerate(self.hours):
            
            time_label = ctk.CTkLabel(master=self.calendar_frm,text=hour,fg_color="#373747",text_color="#CCCCCC",font=("Arial", 12),width=80,height=30,corner_radius=4)
            time_label.grid(row=row + 1, column=0, padx=4, pady=4, sticky="nsew")

        
        for col in range(8):
            self.calendar_frm.grid_columnconfigure(col, weight=1 if col > 0 else 0, uniform="equal" if col > 0 else "")
        for row in range(1, len(self.hours) + 1):
            self.calendar_frm.grid_rowconfigure(row, weight=1, uniform="equal")

        
        self.event_cell = {}

        
        self.get_event()

        # loops itself until all the necessary cells are made (this is the cells / events that the user can add)
        for row in range(1, len(self.hours) + 1):
            for col in range(len(self.days)):
                
                today_cell = col == self.tdy_day and (self.strt_week + datetime.timedelta(days=col)).date() == self.tdy_date
                
                
                event_frm = ctk.CTkFrame(master=self.calendar_frm,corner_radius=6,fg_color="#2E2E3E",border_width=1,border_color="#3E3E4E")
                event_frm.grid(row=row, column=col + 1, padx=4, pady=4, sticky="nsew")

                
                if today_cell:
                    indicator = ctk.CTkFrame(event_frm,width=4,corner_radius=2,fg_color="#7C3AED"  )
                    indicator.place(x=0, y=0, relheight=1)

                # binding mouse input 
                event_frm.bind("<Button-1>", lambda event, r=row - 1, c=col: self.add_edit_evnt(r, c))

                self.event_cell[(row - 1, col)] = event_frm

                
                event = self.events.get((row - 1, col))
                if event:
                    self.show_event(row - 1, col, event)
    
    def show_event(self, row, col, event_title):
        event_frame = self.event_cell[(row, col)]
        
        # Clear existing content
        for widget in event_frame.winfo_children():
            widget.destroy()
        
        # Create event button 
        event_button = ctk.CTkButton(master=event_frame, text=event_title,corner_radius=6, fg_color="#7C3AED", hover_color="#6D28D9",text_color="white", font=("Arial", 12),command=lambda: self.edit_event(row, col))
        event_button.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.8)

    def get_event(self):
        # Fetch events from the db
        start_date = self.strt_week.date()
        end_date = start_date + datetime.timedelta(days=6)
        self.cursor.execute("""
            SELECT date, time, title FROM events WHERE date BETWEEN %s AND %s AND user_id = %s
        """, (start_date, end_date, self.user_id))
        rows = self.cursor.fetchall()
        self.events = {}  

        # dynamic obhject genration 
        for date, time, title in rows:
            try:
                dt = datetime.datetime.strptime(time, "%H:%M:%S")
                formatted_time = dt.strftime("%I:%M %p")

                if formatted_time in self.hours:
                    time_index = self.hours.index(formatted_time)
                    day_offset = (datetime.datetime.strptime(date, "%Y-%m-%d").date() - start_date).days
                    self.events[(time_index, day_offset)] = title
            except ValueError as e:
                print(f"Error processing event with time '{time}': {e}")

    # show the last week
    def previous_week(self):
        self.strt_week -= datetime.timedelta(weeks=1)
        self.week_labl.configure(text=self.this_week())
        self.calendar()

    # changes the calander to the next week
    def next_week(self):
        # Go to the next week
        self.strt_week += datetime.timedelta(weeks=1)
        self.week_labl.configure(text=self.this_week())
        self.calendar()

    # adds the events or go through changes in the event
    def add_edit_evnt(self, row, col):
        # Check if there's already an event in the selected cell
        current_event = self.events.get((row, col), None)

        
        def decision():
            action = self.action_txt.get().strip().lower()
            self.action_frame.destroy()  # Close the prompt frame after getting input

            if action == 'yes':
                self.edit_event(row, col)
            elif action == 'no':
                pass  # Do nothing and exit
            else:
                messagebox.showerror("Invalid Input", "Please type 'Yes' or 'No'.")  # Show an error message
                self.add_edit_evnt(row, col)  # Reopen the prompt for correct input


        # Polymorphism: Same method handles both adding AND editing
        if current_event:
            
            self.action_frame = ctk.CTkFrame(master=self, width=350, height=220, corner_radius=12, fg_color="#282838",border_width=1,border_color="#3E3E4E")
            self.action_frame.place(relx=0.5, rely=0.4, anchor="center")

            
            self.action_label = ctk.CTkLabel(master=self.action_frame,text=f"Event at {self.hours[row]} on {self.days[col]}:\n{current_event}\n\nDo you want to edit this event? (Yes/No)",font=("Arial", 14),text_color="#EAEAEA")
            self.action_label.place(relx=0.5, rely=0.4, anchor="center")

            
            self.action_txt = ctk.CTkEntry(master=self.action_frame, placeholder_text="Type Yes or No",width=200,height=35,font=("Arial", 14),corner_radius=6,fg_color="#373747",border_color="#4E4E5E")
            self.action_txt.place(relx=0.5, rely=0.65, anchor="center")

            
            self.action_button = ctk.CTkButton(master=self.action_frame, command=decision, text="Confirm",width=120,height=35,font=("Arial", 14),fg_color="#7C3AED",hover_color="#6D28D9",corner_radius=6)
            self.action_button.place(relx=0.5, rely=0.85, anchor="center")

        else:
            
            self.add_event(row, col)

    def add_event(self, row, col):
        
        self.add_event_frame = ctk.CTkFrame(master=self, width=450, height=350, corner_radius=12, fg_color="#282838",border_width=1,border_color="#3E3E4E")
        self.add_event_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Frame title
        frame_title = ctk.CTkLabel(master=self.add_event_frame, text="Create New Event", font=("Arial", 20, "bold"), text_color="#EAEAEA")
        frame_title.place(relx=0.5, rely=0.1, anchor="center")

        #  (Dynamic object generation)
        if row is None or col is None:
            
            date_label = ctk.CTkLabel(master=self.add_event_frame, text="Date:", font=("Arial", 14), text_color="#EAEAEA")
            date_label.place(relx=0.1, rely=0.25, anchor="w")
            
            
            week_dates = []
            for i in range(7):
                date = self.strt_week + datetime.timedelta(days=i)
                week_dates.append(f"{self.days[i]} ({date.day}/{date.month})")
            
            self.date_combo = ctk.CTkComboBox(master=self.add_event_frame,values=week_dates,width=200,height=35,font=("Arial", 14),corner_radius=6,dropdown_font=("Arial", 14))
            self.date_combo.place(relx=0.6, rely=0.25, anchor="w")
            self.date_combo.set(week_dates[0])  # Default to first day
            
            
            time_label = ctk.CTkLabel(master=self.add_event_frame, text="Time:", font=("Arial", 14), text_color="#EAEAEA")
            time_label.place(relx=0.1, rely=0.35, anchor="w")
            
            self.time_combo = ctk.CTkComboBox(master=self.add_event_frame,values=self.hours,width=200,height=35,font=("Arial", 14),corner_radius=6,dropdown_font=("Arial", 14))
            self.time_combo.place(relx=0.6, rely=0.35, anchor="w")
            self.time_combo.set(self.hours[0])  
            
            
            title_y_position = 0.45
        else:
            
            slot_info = ctk.CTkLabel(master=self.add_event_frame, text=f"Day: {self.days[col]} | Time: {self.hours[row]}", font=("Arial", 14), text_color="#AAAAAA")
            slot_info.place(relx=0.5, rely=0.2, anchor="center")
            
            
            title_y_position = 0.35

        # Title Label and Entry
        title_label = ctk.CTkLabel(master=self.add_event_frame, text="Event Title:", font=("Arial", 14), text_color="#EAEAEA")
        title_label.place(relx=0.1, rely=title_y_position, anchor="w")

        self.event_title_entry = ctk.CTkEntry(master=self.add_event_frame, placeholder_text="Enter event title",width=300,height=35,font=("Arial", 14),corner_radius=6,fg_color="#373747",border_color="#4E4E5E")
        self.event_title_entry.place(relx=0.5, rely=title_y_position+0.1, anchor="center")

        

        # Buttons
        button_frame = ctk.CTkFrame(master=self.add_event_frame,fg_color="transparent")
        button_frame.place(relx=0.5, rely=0.85, anchor="center")

        
        self.save_button = ctk.CTkButton(master=button_frame,text="Save Event",command=lambda: self.save_event(row, col),width=150,height=40,font=("Arial", 14),fg_color="#7C3AED",hover_color="#6D28D9",corner_radius=6)
        self.save_button.pack(side="left", padx=10)

       
        self.cancel_button = ctk.CTkButton(master=button_frame,text="Cancel",command=lambda: self.add_event_frame.place_forget(),width=120,height=40,font=("Arial", 14),fg_color="#444454",hover_color="#555565",corner_radius=6)
        self.cancel_button.pack(side="left", padx=10)

    def save_event(self, row, col):
        # Save the event details
        event_name = self.event_title_entry.get().strip()
        
        
        if row is None or col is None:
            
            date_str = self.date_combo.get()
            day_indx = self.days.index(date_str.split()[0][:3])  # Get day index from the selected text
            event_date = (self.strt_week + datetime.timedelta(days=day_indx)).date()
            event_time = self.time_combo.get()
            time_indx = self.hours.index(event_time)
        else:
            
            event_date = (self.strt_week + datetime.timedelta(days=col)).date()
            event_time = self.hours[row]
            time_indx = row

        
        try:
            # convert 12 format to 24 format
            event_time_24hr = datetime.datetime.strptime(event_time, "%I:%M %p").strftime("%H:%M:%S")

            if event_name:
                try:
                    
                    self.cursor.execute("""
                        INSERT INTO events (user_id, title, date, time)
                        VALUES (%s, %s, %s, %s)
                    """, (self.user_id, event_name, event_date, event_time_24hr))
                    self.conn.commit()

                    
                    if row is not None and col is not None:
                        self.events[(row, col)] = {
                            "title": event_name,
                        }
                        
                    # Refresh 
                    self.calendar()
                    messagebox.showinfo("Success", "Event added successfully!")

                except mysql.connector.Error as e:
                    messagebox.showerror("Error", f"Failed to save event: {e}")
                finally:
                    # Hide the event entry frame after saving
                    self.add_event_frame.destroy()
            else:
                messagebox.showwarning("Warning", "Event title cannot be empty.")
        except ValueError as e:
            print(f"Error converting time '{event_time}' to 24-hour format: {e}")

    def show_event(self, row, col, event_name):
        
        
        event_frame = self.event_cell[(row, col)]
        
        # Clear 
        for widget in event_frame.winfo_children():
            widget.destroy()

        if event_name:
            
            event_button = ctk.CTkButton(master=event_frame, text=event_name, fg_color="#7C3AED", hover_color="#6D28D9",text_color="white", font=("Arial", 12),corner_radius=6,command=lambda: self.edit_event(row, col))
            event_button.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.8)
        else:
            # Empty cell
            pass

    def edit_event(self, row, col):
        # Retrieve from the db
        current_event = self.events.get((row, col), None)

        
        if current_event:
            current_title = current_event["title"]
        else:
            current_title = ""

        # pop up frame 
        edit_popup = ctk.CTkFrame(master=self, width=400, height=300, corner_radius=12, fg_color="#282838",border_width=1,border_color="#3E3E4E")
        edit_popup.place(relx=0.5, rely=0.5, anchor="center")

        
        title = ctk.CTkLabel(master=edit_popup, text="Edit Event", font=("Arial", 20, "bold"), text_color="#EAEAEA")
        title.place(relx=0.5, rely=0.15, anchor="center")

        
        name_labl = ctk.CTkLabel(edit_popup, text="Event Title:", font=("Arial", 14), text_color="#EAEAEA")
        name_labl.place(relx=0.1, rely=0.3, anchor="w")
        
        name_entry = ctk.CTkEntry(edit_popup,width=250,height=35,font=("Arial", 14),corner_radius=6,fg_color="#373747",border_color="#4E4E5E")
        name_entry.insert(0, current_title)  # Set current event title as default
        name_entry.place(relx=0.5, rely=0.4, anchor="center")

        
        time_labl = ctk.CTkLabel(edit_popup, text="Select Time:", font=("Arial", 14), text_color="#EAEAEA")
        time_labl.place(relx=0.1, rely=0.55, anchor="w")
        
        time_combo = ctk.CTkComboBox(edit_popup, values=self.hours, width=250,height=35,font=("Arial", 14),corner_radius=6,dropdown_font=("Arial", 14))
        time_combo.set(self.hours[row])  # Set the current time slot as default
        time_combo.place(relx=0.5, rely=0.65, anchor="center")

        # Buttons
        button_frm = ctk.CTkFrame(edit_popup, fg_color="transparent")
        button_frm.place(relx=0.5, rely=0.85, anchor="center")

        # Confirm button to save the changes
        confirm_btn = ctk.CTkButton(button_frm, text="Save Changes", width=150,height=40,font=("Arial", 14),fg_color="#7C3AED",hover_color="#6D28D9",corner_radius=6,command=lambda: self.confirm_edit(row, col, name_entry.get(), time_combo.get(), edit_popup))
        confirm_btn.pack(side="left", padx=10)
        
        
        delete_btn = ctk.CTkButton(button_frm, text="Delete", width=100,height=40,font=("Arial", 14),fg_color="#E11D48",  hover_color="#BE123C",corner_radius=6,command=lambda: self.delete_event(row, col, edit_popup))
        delete_btn.pack(side="left", padx=10)
    
    def delete_event(self, row, col, popup):
        
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this event?"):
            try:
                
                event_date = (self.strt_week + datetime.timedelta(days=col)).date()
                old_time_obj = datetime.datetime.strptime(self.hours[row], "%I:%M %p")
                old_time = old_time_obj.strftime("%H:%M:%S")
                
                
                self.cursor.execute("""
                    DELETE FROM events
                    WHERE user_id = %s AND date = %s AND time = %s
                """, (self.user_id, event_date, old_time))
                self.conn.commit()
                
                # Remove from local events dictionary
                if (row, col) in self.events:
                    del self.events[(row, col)]
                
                # Close popup
                popup.destroy()
                
                # Refresh calendar
                self.calendar()
                
                messagebox.showinfo("Success", "Event deleted successfully!")
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"Failed to delete event: {e}")

    def confirm_edit(self, row, col, new_name, new_time, popup):
        
        if new_name:
           
            if new_time != self.hours[row]:
                new_time_index = self.hours.index(new_time)
                
                if (row, col) in self.events:
                    del self.events[(row, col)]
                self.events[(new_time_index, col)] = {"title": new_name}
                
                # Update the db
                try:
                    
                    event_date = (self.strt_week + datetime.timedelta(days=col)).date()
                    old_time = datetime.datetime.strptime(self.hours[row], "%I:%M %p").strftime("%H:%M:%S")
                    new_time = datetime.datetime.strptime(new_time, "%I:%M %p").strftime("%H:%M:%S")
                    self.cursor.execute("""
                        UPDATE events
                        SET title = %s, time = %s
                        WHERE date = %s AND time = %s AND user_id = %s
                    """, (new_name, new_time, event_date, old_time, self.user_id))
                    self.conn.commit()
                    # Refresh the calendar
                    self.calendar()
                    messagebox.showinfo("Success", "Event updated successfully!")

                except mysql.connector.Error as e:
                    messagebox.showerror("Error", f"Failed to update event: {e}")
            else:
                
                self.events[(row, col)] = {"title": new_name}
                
                # Update the db
                try:
                    event_date = (self.strt_week + datetime.timedelta(days=col)).date()
                    old_time = datetime.datetime.strptime(self.hours[row], "%I:%M %p").strftime("%H:%M:%S")
                    self.cursor.execute("""
                        UPDATE events
                        SET title = %s
                        WHERE date = %s AND time = %s AND user_id = %s
                    """, (new_name, event_date, old_time, self.user_id))
                    self.conn.commit()
                    
                    self.calendar()
                    messagebox.showinfo("Success", "Event updated successfully!")

                except mysql.connector.Error as e:
                    messagebox.showerror("Error", f"Failed to update event: {e}")

            
            popup.destroy()
        else:
            messagebox.showwarning("Warning", "Event name cannot be empty.")

    def time(self):
        
        curnt_time = datetime.datetime.now().strftime("%A, %B %d, %Y | %I:%M:%S %p")
        self.time_labl.configure(text=curnt_time)

        # Call this function every 1000 milliseconds (1 second)
        self.after(1000, self.time)