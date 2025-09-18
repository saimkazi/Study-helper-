import customtkinter as ctk
from tkinter import messagebox
from textwrap import fill
import mysql.connector

class FlashCardMainApp(ctk.CTkFrame):
    def __init__(self, parent, user_id, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Extract user_id properly
        if isinstance(user_id, tuple):
            self.user_id = user_id[0]  # Extract first element from tuple
        else:
            self.user_id = user_id # Simple attributes 
        
        print(self.user_id)
        
        # Set dark theme appearance
        self.configure(fg_color="#121212")  # Dark background
        self.main_menu()

    def connect_db(self):
        # try to connect to DB
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root", 
                password="",
                database="nea",
                buffered=True
            )
            self.cursor = self.conn.cursor(buffered=True)
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to connect to DB: {e}")

    def main_menu(self):
        # connect to DB
        self.connect_db()

        # Header
        header = ctk.CTkFrame(self, fg_color="#121212", corner_radius=0)
        header.pack(fill="x", pady=(20, 10))

        # Title
        title_labl = ctk.CTkLabel(header, text="Flashcards", font=("Arial", 28, "bold"),text_color="#FFFFFF")
        title_labl.pack(side="left", padx=20)

        # Subtitle
        subtitle_labl = ctk.CTkLabel(header, text="Study and memorize key concepts with interactive flashcards", font=("Arial", 14),text_color="#AAAAAA")
        subtitle_labl.pack(side="left", padx=10)

        # Statistics Frame
        stats_frm = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=10)
        stats_frm.pack(side="top", anchor="e", padx=20, pady=10)

        # get the stats from DB
        try:
            self.cursor.execute("""
                SELECT 
                    COUNT(front) 
                FROM flashcards 
                WHERE user_id = %s
            """, (self.user_id,))
            stats_data = self.cursor.fetchone()

            # Default valus if nothing exists
            total = stats_data[0] if stats_data else 0

        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to load stats: {e}")
            total, reviewed, pending = 0, 0, 0

        # Create stat cards inside the frame (3 columns)
        card_frm = ctk.CTkFrame(stats_frm, fg_color="#1E1E1E")
        card_frm.pack(padx=20, pady=20)

        # Stats cards
        stats = [
            {"value": str(total), "label": "REVISION", "color": "#8A2BE2"},  # Purple
            {"value": "0", "label": "WORK DONE", "color": "#9370DB"},  # Medium purple
            {"value": "7", "label": "FAILS", "color": "#9932CC"}  # Dark orchid
        ]

        for i, stat in enumerate(stats):
            stat_card = ctk.CTkFrame(card_frm, fg_color="#1E1E1E")
            stat_card.grid(row=0, column=i, padx=20)
            
            # Value
            value_labl = ctk.CTkLabel(stat_card, text=stat["value"], font=("Arial", 24, "bold"),text_color=stat["color"])
            value_labl.pack(anchor="center", pady=(0, 5))
            
            # Label
            label = ctk.CTkLabel(stat_card, text=stat["label"], font=("Arial", 12),text_color="#AAAAAA")
            label.pack(anchor="center")

        

        # Subject selection section
        subj_section = ctk.CTkFrame(self, fg_color="#121212", corner_radius=0)
        subj_section.pack(fill="x", pady=20)

        # Subject heading
        subj_heading = ctk.CTkLabel(subj_section, text="Select a Subject", font=("Arial", 20, "bold"),text_color="#FFFFFF")
        subj_heading.pack(anchor="w", padx=20, pady=(0, 10))

        # Search bar
        search_frm = ctk.CTkFrame(subj_section, fg_color="#1E1E1E", corner_radius=20, height=40)
        search_frm.pack(fill="x", padx=20, pady=10)
        
        search_icon = ctk.CTkLabel(search_frm, text="🔍", font=("Arial", 14), text_color="#AAAAAA")
        search_icon.pack(side="left", padx=(15, 5))
        
        search_entry = ctk.CTkEntry(search_frm, placeholder_text="Search subjects...",border_width=0,fg_color="#1E1E1E",text_color="#FFFFFF",font=("Arial", 14),height=38,width=400)
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 20))

        # Create the scroll frame for subjects
        self.button_frm = ctk.CTkScrollableFrame(self,width=900,height=400,fg_color="#121212",scrollbar_fg_color="#121212",scrollbar_button_color="#8A2BE2",scrollbar_button_hover_color="#9370DB")
        self.button_frm.pack(fill="both", expand=True, padx=20, pady=10)

        # Fill with subjects
        self.flashcard_selection()

    

    def flashcard_selection(self):
        def get_select_subj_db():
            #Fetch subjects from dp
            try:
                self.cursor.execute("SELECT DISTINCT subject_name FROM subjects WHERE user_id=%s", (self.user_id,))
                results = self.cursor.fetchall()
                return [row[0] for row in results]  # Extract the subject names
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"Database query failed: {e}")
                return []

        def open_subj_flashcard(subject):
            #Open the subject
            self.flash_card(subject)

        def create_flashcards():
            #unique subject button
            unique_subjects = get_select_subj_db()

            if not unique_subjects:
                # Create an empty state display
                empty_frm = ctk.CTkFrame(self.button_frm, fg_color="#121212")
                empty_frm.pack(fill="both", expand=True, pady=50)
                
                empty_labl = ctk.CTkLabel(empty_frm, text="No subjects available yet", font=("Arial", 18),text_color="#AAAAAA")
                empty_labl.pack(pady=10)
                
                add_btn = ctk.CTkButton(empty_frm,text="+ Add Your First Subject",font=("Arial", 14),fg_color="#8A2BE2",hover_color="#9370DB",corner_radius=10,height=40)
                add_btn.pack(pady=10)
                return

            # Clear existing buttons before adding new ones
            for widget in self.button_frm.winfo_children():
                widget.destroy()

            # Add our subjects as cards
            subj_card_frm = ctk.CTkFrame(self.button_frm, fg_color="#121212")
            subj_card_frm.pack(fill="both", expand=True)
            
            # Configure grid with 3 columns
            subj_card_frm.grid_columnconfigure(0, weight=1)
            subj_card_frm.grid_columnconfigure(1, weight=1)
            subj_card_frm.grid_columnconfigure(2, weight=1)
            
            # Add subject cards in a grid
            for i, subject in enumerate(unique_subjects):
                row, col = divmod(i, 3)  # 3 columns
                
                subject_card = ctk.CTkButton(subj_card_frm,text=subject,font=("Arial", 16, "bold"),fg_color="#1E1E1E",hover_color="#2A2A2A",corner_radius=10,height=150,width=280,command=lambda s=subject: open_subj_flashcard(s))
                subject_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Create the flashcards
        create_flashcards()

    def flash_card(self, subject):
        # Clear the main frame before showing flashcards
        for widget in self.winfo_children():
            widget.destroy()

        class Flashcard:
            def __init__(self, word, meaning):
                self.word = word
                self.meaning = meaning

        class FlashcardApp:
            def __init__(self, main_frame, cursor, connection, subject,user_id, parent_app):
                
                self.main_frame = main_frame
                self.parent_app = parent_app 
                self.cursor = cursor
                self.connection = connection
                self.subject = subject
                self.user_id=user_id
                self.flashcards = []
                self.current_flashcard = None
                self.showing_word = True
                self.current_index = 0


                # Action_frame
                Action_frm = ctk.CTkFrame(main_frame, fg_color="#121212", corner_radius=0)
                Action_frm.pack(fill="x", pady=(20, 10))
                
                # Back button
                back_btn = ctk.CTkButton(Action_frm,text="← Back",font=("Arial", 14),fg_color="#1E1E1E",hover_color="#2A2A2A",corner_radius=8,command=self.return_back)
                back_btn.pack(side="left", padx=20)
                
                
                subject_title = ctk.CTkLabel(Action_frm, text=f"Flashcards: {subject}", font=("Arial", 22, "bold"),text_color="#FFFFFF")
                subject_title.pack(side="left", padx=10)
                
                self.content_frm = ctk.CTkFrame(main_frame, fg_color="#121212", corner_radius=0)
                self.content_frm.pack(fill="both", expand=True, padx=20, pady=10)
                
                # Tab selector frame
                tab_selector_frm = ctk.CTkFrame(self.content_frm, fg_color="#1E1E1E", corner_radius=10, height=50)
                tab_selector_frm.pack(fill="x", pady=(0, 10))
                
                # swicthing from add to study
                def switch_tab(tab_name):
                    
                     # hasattr = check if attribute exists 
                    
                    if hasattr(self, 'create_frame'):
                        self.create_frme.pack_forget()
                    if hasattr(self, 'study_tab_frame'):
                        self.study_tab_frm.pack_forget()
                    
                    
                    self.create_tab_btn.configure(fg_color="#8A2BE2" if tab_name == "Create" else "#1E1E1E",text_color="white")

                    self.study_tab_btn.configure(fg_color="#8A2BE2" if tab_name == "Study" else "#1E1E1E",text_color="white")
                    
                    
                    if tab_name == "Create":
                        if not hasattr(self, 'create_tab_frame'):
                            self.create_new_flashcard()
                        self.create_frme.pack(fill="both", expand=True)
                    else:
                        if not hasattr(self, 'study_tab_frame'):
                            self.setup_study_tab()
                        self.study_tab_frm.pack(fill="both", expand=True)
                
                # Create tab buttons
                self.create_tab_btn = ctk.CTkButton(tab_selector_frm,text="Create",font=("Arial", 14),fg_color="#8A2BE2",  hover_color="#9370DB",corner_radius=8,height=40,width=120,command=lambda: switch_tab("Create"))
                self.create_tab_btn.pack(side="left", padx=10, pady=5)
                
                self.study_tab_btn = ctk.CTkButton(tab_selector_frm,text="Study",font=("Arial", 14),fg_color="#1E1E1E",  hover_color="#2A2A2A",corner_radius=8,height=40,width=120,command=lambda: switch_tab("Study"))
                self.study_tab_btn.pack(side="left", padx=10, pady=5)
                
                
                self.create_new_flashcard()
                
                self.load_flashcards_fromDB()
                
                self.amount_flashcard()

            def create_new_flashcard(self):
                # Create frame 
                self.create_frme = ctk.CTkFrame(self.content_frm, fg_color="#121212", corner_radius=0)
                self.create_frme.pack(fill="both", expand=True)
                
                
                frame = ctk.CTkFrame(self.create_frme, fg_color="#1E1E1E", corner_radius=10)
                frame.pack(padx=20, pady=20, fill="x")
                
                # Title
                title = ctk.CTkLabel(frame, text="Create New Flashcard", font=("Arial", 18, "bold"),text_color="#FFFFFF")
                title.pack(pady=(20, 30))
                
                # Word input
                front_labl = ctk.CTkLabel(frame, text="Term", font=("Arial", 14),text_color="#FFFFFF")
                front_labl.pack(anchor="w", padx=30)
                
                self.front_entry = ctk.CTkEntry(frame,placeholder_text="Enter term or concept",font=("Arial", 14),fg_color="#2A2A2A",text_color="#FFFFFF",height=40,width=500)
                self.front_entry.pack(padx=30, pady=(5, 20), fill="x")
                
                
                self.back_label = ctk.CTkLabel(frame, text="Definition", font=("Arial", 14),text_color="#FFFFFF")
                
                self.back_entry = ctk.CTkEntry(frame,placeholder_text="Enter definition or explanation",font=("Arial", 14),fg_color="#2A2A2A",text_color="#FFFFFF",height=40,width=500)
                
                #  button
                self.add_meaning = ctk.CTkButton(frame,text="Continue",font=("Arial", 14),fg_color="#8A2BE2",hover_color="#9370DB",corner_radius=8,height=40,command=self.flip_meaning)
                self.add_meaning.pack(pady=20)
                
                
                self.add_btn = ctk.CTkButton(frame,text="Add Flashcard",font=("Arial", 14),fg_color="#8A2BE2",hover_color="#9370DB",corner_radius=8,height=40,command=self.add_cards)
                
                # Flashcard preview section
                view_frame = ctk.CTkFrame(self.create_frme, fg_color="#121212", corner_radius=0)
                view_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                view_lbl = ctk.CTkLabel(view_frame, text="Your Flashcards", font=("Arial", 18, "bold"),text_color="#FFFFFF")
                view_lbl.pack(anchor="w", pady=(0, 10))
                
                self.flashcard_preview = ctk.CTkScrollableFrame(view_frame,fg_color="#121212",scrollbar_fg_color="#121212",scrollbar_button_color="#8A2BE2",scrollbar_button_hover_color="#9370DB",orientation="horizontal")
                self.flashcard_preview.pack(fill="x", pady=5)
                
                
                self.amount_flashcard()

            def setup_study_tab(self):

                self.study_tab_frm = ctk.CTkFrame(self.content_frm, fg_color="#121212", corner_radius=0)
                
                # Main frame
                self.flashcard_frm = ctk.CTkFrame(self.study_tab_frm, fg_color="#1E1E1E", corner_radius=10)
                self.flashcard_frm.pack(fill="both", expand=True, padx=20, pady=20)
                
                # Flashcard content
                self.flashcard_content = ctk.CTkLabel(self.flashcard_frm, text="Click 'Start Studying' to begin",font=("Arial", 24, "bold"),text_color="#FFFFFF",wraplength=700)
                self.flashcard_content.place(relx=0.5, rely=0.5, anchor="center")
                
                # Control buttons

                button_frm = ctk.CTkFrame(self.study_tab_frm, fg_color="#121212", corner_radius=0)
                button_frm.pack(fill="x", padx=20, pady=(0, 20))
                
                
                self.start_btn = ctk.CTkButton(button_frm,text="Start Studying",font=("Arial", 14),fg_color="#8A2BE2",hover_color="#9370DB",corner_radius=8,height=40,width=150,command=self.start_cards)
                self.start_btn.pack(side="left", padx=(0, 10))
                
                
                self.flip_btn = ctk.CTkButton(button_frm,text="Flip Card",font=("Arial", 14),fg_color="#1E1E1E",hover_color="#2A2A2A",corner_radius=8,height=40,width=120,command=self.flip_card)
                self.next_btn = ctk.CTkButton(button_frm,text="Next Card",font=("Arial", 14),fg_color="#8A2BE2",hover_color="#9370DB",corner_radius=8,height=40,width=120,command=self.next_card)
                
                self.delete_btn = ctk.CTkButton(button_frm,text="Delete Card",font=("Arial", 14),fg_color="#E74C3C", corner_radius=8,height=40,width=120,command=self.delete_card)


            # load the flashcard
            def amount_flashcard(self):
                def load_flashcards():
                    selected_sub = self.subject
                    try:
                        query = "SELECT DISTINCT flashcards.front FROM subjects JOIN flashcards On subjects.subject_id=flashcards.subject_id WHERE subjects.subject_name=%s AND flashcards.user_id=%s"
                        self.cursor.execute(query, (selected_sub,self.user_id))
                        results = self.cursor.fetchall()
                        return [row[0] for row in results]  # Extract the subject names
                    except mysql.connector.Error as e:
                        messagebox.showerror("Error", f"Database query failed: {e}")
                        return []
                
                #Creates the flashcard
                flashfront = load_flashcards()

                for widget in self.flashcard_preview.winfo_children():
                    widget.destroy()
                
                if not flashfront:
                    empty_label = ctk.CTkLabel(self.flashcard_preview, text="No flashcards available. Create your first flashcard above.",font=("Arial", 14),text_color="#AAAAAA")
                    empty_label.pack(pady=20)
                    return

                for subject in flashfront:
                    card_preview = ctk.CTkButton(self.flashcard_preview, text=subject,font=("Arial", 14),fg_color="#2A2A2A",hover_color="#3A3A3A",corner_radius=8,height=150,width=200)
                    card_preview.pack(side="left", padx=10, pady=5)

            def return_back(self):
                # Clear content and go back 

                for widget in self.main_frame.winfo_children():
                    widget.destroy()
                
                # Recreate the main menu
                self.parent_app.main_menu()
            
                

            def flip_meaning(self):
                word = self.front_entry.get().strip()
                if word:
                    # Hide word elements
                    #Dynamic object genrations
                    self.add_meaning.pack_forget()
                    
                    # Show meaning elements
                    self.back_label.pack(anchor="w", padx=30)
                    self.back_entry.pack(padx=30, pady=(5, 20), fill="x")
                    self.add_btn.pack(pady=20)
                else:
                    messagebox.showerror("Error", "Please enter a term")

            def add_cards(self):
                word = self.front_entry.get().strip()
                meaning = self.back_entry.get().strip()
                if word and meaning:
                    try:
                            cursor= self.connection.cursor(buffered=True)
                            # Get subject_id
                            subject_query = "SELECT subject_id FROM subjects WHERE subject_name = %s"
                            self.cursor.execute(subject_query, (self.subject,))
                            result = self.cursor.fetchone()

                            if not result:
                                messagebox.showerror("Error", "Subject not found In DB")
                                return
                            
                            subject_id = result[0]  # Get the subject id 
                            
                            # clear any pending result 
                            while self.cursor.nextset():
                                pass
                            
                            # MAKE fresh cursor for the insertion
                            insert_cursor = self.connection.cursor()
                            
                            # ADD into database
                            query = "INSERT INTO flashcards (front, back, subject_id, user_id) VALUES (%s, %s, %s, %s)"
                            insert_cursor.execute(query, (word, meaning, subject_id, self.user_id))
                            self.connection.commit()
                            insert_cursor.close()  # Close the dedicated cursor

                            # Update local  list
                            self.flashcards.append(Flashcard(word, meaning))

                            # Clear input fields
                            self.front_entry.delete(0, 'end')
                            self.back_entry.delete(0, 'end')

                            # Reset form
                            self.back_label.pack_forget()
                            self.back_entry.pack_forget()
                            self.add_btn.pack_forget()
                            self.add_meaning.pack(pady=20)

                            # Show success message
                            messagebox.showinfo("Success", "Flashcard added successfully!")

                            # Refresh flashcards
                            self.load_flashcards_fromDB()
                            self.amount_flashcard()
                            
                    except mysql.connector.Error as e:
                            messagebox.showerror("Error", f"Failed to add flashcard: {e}")
                            # Print the full error to console for debugging
                            import traceback
                            traceback.print_exc()
                else:
                    messagebox.showwarning("Input Error", "Please provide both a term and a definition")

            def load_flashcards_fromDB(self):
                try:
                    cursor = self.connection.cursor(buffered=True)
                    query = "SELECT flashcards.front AS word, flashcards.back AS meaning FROM subjects JOIN flashcards ON subjects.subject_id = flashcards.subject_id WHERE subjects.subject_name = %s AND flashcards.user_id=%s" # simple Datbase Model
                    self.cursor.execute(query, (self.subject,self.user_id,))
                    results = self.cursor.fetchall()
                    self.flashcards = [Flashcard(row[0], row[1]) for row in results]

                    if not self.flashcards:
                        self.flashcard_content.configure(
                            text=f"No flashcards for {self.subject}.\nCreate some on the 'Create' tab.",
                            font=("Arial", 18)
                        )
                    else:
                        # Update the count in start button
                        self.start_btn.configure(text=f"Start Studying ({len(self.flashcards)})")
                except mysql.connector.Error as e:
                    messagebox.showerror("Error", f"Database query failed: {e}")

            def start_cards(self):
                if not self.flashcards:
                    messagebox.showinfo("No Flashcards", "Please create some flashcards first.")
                    # Switch to create tab
                    self.create_tab_btn.invoke()
                    return
                
                # Hide start button
                self.start_btn.pack_forget()
                
                # Show control buttons
                self.flip_btn.pack(side="left", padx=(0, 10))
                self.next_btn.pack(side="left", padx=(0, 10))
                self.delete_btn.pack(side="left")
                
                # Show first flashcard
                self.next_card()

            def delete_card(self):
                if self.current_flashcard:
                    # Get the word of the current flashcard
                    word_to_delete = self.current_flashcard.word
                    
                    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{word_to_delete}'?"):
                        try:
                            # Get subject_id
                            subject_query = "SELECT subject_id FROM subjects WHERE subject_name = %s"
                            self.cursor.execute(subject_query, (self.subject,))
                            subject_result = self.cursor.fetchone()

                            if not subject_result:
                                messagebox.showerror("Error", "Subject not found.")
                                return

                            subject_id = subject_result[0]  # Get the subject_id

                            # Delete the flashcard from the database
                            delete_query = "DELETE FROM flashcards WHERE front = %s AND subject_id = %s"
                            self.cursor.execute(delete_query, (word_to_delete, subject_id))
                            self.connection.commit()

                            # Remove the flashcard from the local list
                            self.flashcards = [fc for fc in self.flashcards if fc.word != word_to_delete]

                            messagebox.showinfo("Success", f"Flashcard '{word_to_delete}' deleted successfully.")

                            # Update flashcards display
                            if self.flashcards:
                                self.next_card()
                            else:
                                self.flashcard_content.configure(
                                    text="No flashcards available.\nCreate some on the 'Create' tab.",
                                    font=("Arial", 18)
                                )
                                
                                # Hide control buttons and show start button
                                self.flip_btn.pack_forget()
                                self.next_btn.pack_forget()
                                self.delete_btn.pack_forget()
                                self.start_btn.pack(side="left", padx=(0, 10))
                        except mysql.connector.Error as e:
                            messagebox.showerror("Error", f"Failed to delete flashcard: {e}")
                else:
                    messagebox.showwarning("Warning", "No flashcard is currently displayed.")

                # Update flashcard preview
                self.amount_flashcard()

            def next_card(self):
                if self.flashcards:
                    self.current_index = (self.current_index + 1) % len(self.flashcards)
                    self.current_flashcard = self.flashcards[self.current_index]
                    self.showing_word = True
                    
                    # Update content with card counter
                    self.flashcard_content.configure(
                        text=self.current_flashcard.word,
                        font=("Arial", 28, "bold")
                    )
                    
                    # Show card counter at bottom of frame
                    self.flashcard_content_subtitle = ctk.CTkLabel(self.flashcard_frm, text=f"Card {self.current_index + 1} of {len(self.flashcards)}",font=("Arial", 14),text_color="#AAAAAA")
                    self.flashcard_content_subtitle.place(relx=0.5, rely=0.9, anchor="center")
                else:
                    self.flashcard_content.configure(
                        text="No flashcards available!",
                        font=("Arial", 18)
                    )
                    messagebox.showwarning("Warning", "No flashcards available.")
                    self.return_back()

            def flip_card(self):
                if self.current_flashcard:
                    if self.showing_word:
                        self.flashcard_content.configure(
                            text=self.current_flashcard.meaning,
                            font=("Arial", 20)
                        )
                        self.showing_word = False
                    else:
                        self.flashcard_content.configure(
                            text=self.current_flashcard.word,
                            font=("Arial", 28, "bold")
                        )
                        self.showing_word = True

        # Create the flashcard app
        FlashcardApp(self, self.cursor, self.conn, subject, self.user_id,self)