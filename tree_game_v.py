import tkinter as tk
from tkinter import messagebox, font, ttk
from PIL import Image, ImageTk
import os
import random
import math
import requests
import json
import sys

class TreeNode:
    def __init__(self, question, answers, correct_answer, platform, difficulty=1):
        self.question = question
        self.answers = answers
        self.correct_answer = correct_answer
        self.platform = platform
        self.difficulty = difficulty
        self.children = {
            "correct": None,   # correct answer
            "incorrect": None  # wrong answer
        }
    
    def add_child(self, node, path_type="correct"):
        # cprrect and wrong nodes 
        self.children[path_type] = node
        return node

class TreeDefenderGame(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Store the parent
        self.parent = parent
        
        # Game background
        self.bg_color = "#1A2A3A"  # Darker blue background
        self.configure(bg=self.bg_color)
        
       
        self.main_frm = tk.Frame(self, bg=self.bg_color)
        self.main_frm.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Game state
        self.boss_hlth = 3
        self.player_hlth = 3
        self.crnt_platform_indx = -1  # Track player position
        self.attacking = False
        self.allowed_move = True  # New flag to control player movement
        self.score = 0
        self.level = 1
        self.platforms = []
        self.crnt_node = None  # Current question node
        self.debug_mode = True  # Enable debug output
        
        # Available subjects
        self.subj = ["Math", "Geography", "Science", "History", "Literature", "Mixed"]
        self.selected_subj = tk.StringVar(value=self.subj[0])

        
        self.assests()
        
        # GUI Setup
        self.ui()
        
    def assests(self):
        # Create placeholder images if they don't exist
        if not os.path.exists("window.png"):
            self.backup_entity("player.png", (40, 40), "blue")
        if not os.path.exists("boss.png"):
            self.backup_entity("home.png", (100, 100), "red")

    def backup_entity(self, filename, size, color):
        from PIL import Image, ImageDraw
        img = Image.new('RGBA', size, color)
        img.save(filename)
        
    def ui(self):
        self.title_font = font.Font(family="Arial", size=24, weight="bold")
        self.question_font = font.Font(family="Arial", size=16)
        self.button_font = font.Font(family="Arial", size=14, weight="bold")
        
        # Grid configuration to ensure resizing works
        self.main_frm.grid_columnconfigure(0, weight=1)
        
        # Game 
        self.title_label = tk.Label(self.main_frm, text="TREE DEFENDER", 
                                   font=self.title_font, 
                                   fg="#F1C40F", bg=self.bg_color)
        self.title_label.grid(row=0, column=0, pady=(10, 10), sticky="ew")
        
        
        self.subject_frame = tk.Frame(self.main_frm, bg=self.bg_color)
        self.subject_frame.grid(row=1, column=0, pady=(0, 10), sticky="ew")
        self.subject_frame.grid_columnconfigure(0, weight=1)
        self.subject_frame.grid_columnconfigure(1, weight=1)
        
        self.subject_labl = tk.Label(self.subject_frame, text="Select Subject:", font=self.button_font, fg="white", bg=self.bg_color)
        self.subject_labl.grid(row=0, column=0, padx=10, sticky="e")
        
        self.subject_select = ttk.Combobox(self.subject_frame, textvariable=self.selected_subj,values=self.subj, width=15, font=self.button_font)
        self.subject_select.grid(row=0, column=1, padx=10, sticky="w")
        
        
        self.canvas_frm = tk.Frame(self.main_frm, bg=self.bg_color, bd=2, relief=tk.SUNKEN)
        self.canvas_frm.grid(row=2, column=0, pady=10, sticky="nsew")
        self.main_frm.grid_rowconfigure(2, weight=3)  # Give canvas most of the vertical space
        
        
        self.canvas = tk.Canvas(self.canvas_frm, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Player and boss elements
        self.player_img = ImageTk.PhotoImage(Image.open("pics/player.png").resize((50, 50)))
        self.player = self.canvas.create_image(100, 350, image=self.player_img)

        self.boss_img = ImageTk.PhotoImage(Image.open("pics/boss.png").resize((120, 120)))
        self.boss = self.canvas.create_image(650, 100, image=self.boss_img)
        
        # Create platforms
        platform_width = 100
        platform_height = 40
        platform_colors = ["#1ABC9C", "#2ECC71", "#3498DB", "#9B59B6"]
        
        for i in range(4):
            x = 150 + i * 150
            y = 350
            platform = self.canvas.create_rectangle(
                x - platform_width/2, y + 30,
                x + platform_width/2, y + 30 + platform_height,
                fill=platform_colors[i], outline="#FFFFFF", width=2
            )
            self.platforms.append({"shape": platform, "x": x, "y": y + 30 + platform_height/2})
            
            # Add platform number
            self.canvas.create_text(x, y + 30 + platform_height/2, 
                                   text=str(i+1), fill="white", font=self.button_font)
        
        # Health and score displays
        heart_emoji = "❤️"
        self.boss_health_txt = self.canvas.create_text(
            650, 40, text=f"Boss Health: {self.boss_hlth} {heart_emoji}", 
            fill="#E74C3C", font=self.title_font
        )

        self.player_health_txt = self.canvas.create_text(
            150, 40, text=f"Your Health: {self.player_hlth} {heart_emoji}", 
            fill="#2ECC71", font=self.title_font
        )
        
        self.score_txt = self.canvas.create_text(
            400, 40, text=f"Score: {self.score} | Level: {self.level}", 
            fill="#F1C40F", font=self.title_font
        )

        
        if self.debug_mode:
            self.debug_text = self.canvas.create_text(
                400, 380, text="Debug: Ready", 
                fill="#FFFFFF", font=("Arial", 10)
            )

        # Question display
        self.question_frm = tk.Frame(self.main_frm, bg=self.bg_color, padx=20, pady=10,
                                      bd=2, relief=tk.GROOVE)
        self.question_frm.grid(row=3, column=0, pady=(10, 10), sticky="ew")
        self.question_frm.grid_columnconfigure(0, weight=1)
        
        self.question_lbl = tk.Label(self.question_frm, text="", font=self.question_font, wraplength=700, fg="white", bg=self.bg_color)
        self.question_lbl.pack(pady=10, fill=tk.X)
        
        
        self.controls_frm = tk.Frame(self.main_frm, bg=self.bg_color)
        self.controls_frm.grid(row=4, column=0, pady=(10, 10), sticky="ew")
        self.controls_frm.grid_columnconfigure(0, weight=1)
        
        # Button frame
        self.btn_frm = tk.Frame(self.controls_frm, bg=self.bg_color)
        self.btn_frm.pack(fill=tk.X)
        
        
        self.btn_frm.grid_columnconfigure(0, weight=1)
        self.btn_frm.grid_columnconfigure(1, weight=1)
        self.btn_frm.grid_columnconfigure(2, weight=1)
        self.btn_frm.grid_columnconfigure(3, weight=1)
        
        self.btns = []
        
        for i in range(4):
            btn = tk.Button(self.btn_frm, text="", width=15, height=2,bg=platform_colors[i], fg="white", font=self.button_font,
                           command=lambda idx=i: self.check_answer(idx))
            btn.grid(row=0, column=i, padx=10, sticky="ew")
            self.btns.append(btn)

        
        self.strt_btn_frm = tk.Frame(self.main_frm, bg=self.bg_color)
        self.strt_btn_frm.grid(row=5, column=0, pady=(10, 10), sticky="ew")
        
        # Start button with glow effect
        self.strt_btn = tk.Button(self.strt_btn_frm, text="Start Game", font=self.button_font,
                                     bg="#F1C40F", fg="#000000", relief=tk.RAISED, bd=3,
                                     padx=20, pady=10, command=self.start_game)
        self.strt_btn.pack()
        
        # Loading indicator and tree path visualization in status frame
        self.status_frm = tk.Frame(self.main_frm, bg=self.bg_color, bd=1, relief=tk.SUNKEN)
        self.status_frm.grid(row=6, column=0, pady=(5, 5), sticky="ew")
        
        
        self.loading_labl = tk.Label(self.status_frm, text="", font=self.button_font,
                                     fg="#F1C40F", bg=self.bg_color)
        self.loading_labl.pack(pady=5)
        
        
        self.tree_path = tk.Label(self.status_frm, text="Question Tree Path: Root", 
                                        font=("Arial", 10), fg="#F1C40F", bg=self.bg_color)
        self.tree_path.pack(pady=5)
        
        # Add blinking effect to start button
        self.str_btn_animation()
        
       
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def on_canvas_resize(self, event):
        # depending on the size of the window the boss will need to chang position and also the player has to change the position 
        width = event.width
        height = event.height
        
        # Calculate new positions 
        canvas_center_x = width / 2
        boss_x = width - 150  
        player_x = 100        
        
        # Update 
        self.canvas.coords(self.boss, boss_x, 100)
        self.canvas.coords(self.player, player_x, height - 80)
        
        
        self.canvas.coords(self.boss_health_txt, boss_x, 40)
        self.canvas.coords(self.player_health_txt, player_x + 50, 40)
        self.canvas.coords(self.score_txt, canvas_center_x, 40)
        
        # Update position
        if self.debug_mode:
            self.canvas.coords(self.debug_text, canvas_center_x, height - 20)
        
        
        platform_spacing = (width - 300) / 3
        for i in range(4):
            x = 150 + i * platform_spacing
            y = height - 80 + 30  # Position below player
            
            # Update platform rectangle
            platform_width = 100
            platform_height = 40
            self.canvas.coords(
                self.platforms[i]["shape"],
                x - platform_width/2, y,
                x + platform_width/2, y + platform_height
            )
            
            # Update platform position data
            self.platforms[i]["x"] = x
            self.platforms[i]["y"] = y + platform_height/2
            
            # Update platform number text (need to get the text item first)
            # Get all items at platform position to find the text
            items = self.canvas.find_overlapping(x-1, y+platform_height/2-1, x+1, y+platform_height/2+1)
            for item in items:
                if self.canvas.type(item) == "text":
                    self.canvas.coords(item, x, y + platform_height/2)
    
    def debug_log(self, message):
        #Helper function me to see where the program ends up in the code
        if self.debug_mode:
            print(f"DEBUG: {message}")
            self.canvas.itemconfig(self.debug_text, text=f"Debug: {message}")

    def str_btn_animation(self):
        current_color = self.strt_btn.cget("background")
        next_color = "#F39C12" if current_color == "#F1C40F" else "#F1C40F"
        self.strt_btn.config(background=next_color)
        self.after(500, self.str_btn_animation)
        
    def make_qst_tree(self, subject):
        #Create a tree of questions 
        try:
            self.debug_log(f"Creating question tree for subject: {subject}")
            self.loading_labl.config(text="Building question tree...")
            
            # Get questions from API or fallback
            questions = self.get_qst_api(subject, count=15)
            
            # Group questions by difficulty (if available from API), or assign difficulties
            easy_questions = [q for q in questions if q.difficulty <= 1]
            medium_questions = [q for q in questions if q.difficulty == 2]
            hard_questions = [q for q in questions if q.difficulty >= 3]
            
            # redistrubution if not enough question
            if len(easy_questions) < 5:
                
                random.shuffle(questions)
                easy_questions = questions[:5]
                for q in easy_questions:
                    q.difficulty = 1
                
            if len(medium_questions) < 5:
                
                remaining = [q for q in questions if q not in easy_questions]
                if len(remaining) >= 5:
                    medium_questions = remaining[:5]
                else:
                    
                    medium_questions = remaining + random.sample(easy_questions, 5 - len(remaining))
                for q in medium_questions:
                    q.difficulty = 2
                    
            if len(hard_questions) < 5:
                
                used = easy_questions + medium_questions
                remaining = [q for q in questions if q not in used]
                if len(remaining) >= 5:
                    hard_questions = remaining[:5]
                else:
                    
                    hard_questions = remaining + random.sample(medium_questions, 5 - len(remaining))
                for q in hard_questions:
                    q.difficulty = 3
            
            #5 question limit
            easy_questions = easy_questions[:5]
            medium_questions = medium_questions[:5]
            hard_questions = hard_questions[:5]
            
            # Create question adn levels
            root = easy_questions[0]
            
            
            self.debug_log("Building question tree structure...")
            
            # Track nodes 
            added_nodes = {root}
            
            # filter question
            current_correct = root
            for i in range(1, len(easy_questions)):
                if easy_questions[i] not in added_nodes:
                    current_correct = current_correct.add_child(easy_questions[i], "correct")
                    added_nodes.add(easy_questions[i])
            
            
            if medium_questions and medium_questions[0] not in added_nodes:
                current_correct = current_correct.add_child(medium_questions[0], "correct")
                added_nodes.add(medium_questions[0])
            
            
            for i in range(1, len(medium_questions)):
                if medium_questions[i] not in added_nodes:
                    current_correct = current_correct.add_child(medium_questions[i], "correct")
                    added_nodes.add(medium_questions[i])
            
            
            if hard_questions and hard_questions[0] not in added_nodes:
                current_correct = current_correct.add_child(hard_questions[0], "correct")
                added_nodes.add(hard_questions[0])
            
            
            for i in range(1, len(hard_questions)):
                if hard_questions[i] not in added_nodes:
                    current_correct = current_correct.add_child(hard_questions[i], "correct")
                    added_nodes.add(hard_questions[i])
            
            #  create the incorrect paths 
            
            nodes_process = [root]
            
            while nodes_process:
                node = nodes_process.pop(0)
                
                
                if node.children["correct"]:
                    nodes_process.append(node.children["correct"])
                
                
               
                if node.difficulty == 1:
                    
                    avl = [q for q in easy_questions if q not in added_nodes]
                    if not avl:
                        
                        node.children["incorrect"] = root
                    else:
                        incorrect_node = random.choice(avl)
                        node.children["incorrect"] = incorrect_node
                        added_nodes.add(incorrect_node)
                        nodes_process.append(incorrect_node)
                
                elif node.difficulty == 2:
                    
                    avl = [q for q in easy_questions + medium_questions[:2] if q not in added_nodes]
                    if not avl:
                        
                        node.children["incorrect"] = medium_questions[0] if medium_questions else easy_questions[0]
                    else:
                        incorrect_node = random.choice(avl)
                        node.children["incorrect"] = incorrect_node
                        added_nodes.add(incorrect_node)
                        nodes_process.append(incorrect_node)
                
                elif node.difficulty == 3:
                    
                    avl = [q for q in medium_questions if q not in added_nodes]
                    if not avl:
                        
                        node.children["incorrect"] = medium_questions[0] if medium_questions else root
                    else:
                        incorrect_node = random.choice(avl)
                        node.children["incorrect"] = incorrect_node
                        added_nodes.add(incorrect_node)
                        nodes_process.append(incorrect_node)
            
            self.loading_labl.config(text="")
            self.debug_log("Question tree built successfully")
            return root
            
        except Exception as e:
            self.debug_log(f"Error creating question tree: {str(e)}")
            # Create a simple fallback tree
            return self.make_backup_tree(subject)
    
    def make_backup_tree(self, subject):
        #Create a simple fallback tree if API or tree creation fails
        backup_questions = self.get_backup_qsts(subject)
        
        if not backup_questions:
            return None
            
        root = backup_questions[0]
        
        current = root
        for i in range(1, len(backup_questions)):
            current.add_child(backup_questions[i], "correct")
            current = backup_questions[i]
        
        # Create loops for incorrect answers 
        for i in range(len(backup_questions)):
            if i >= 3:  
                target_index = i - 3
                backup_questions[i].add_child(backup_questions[target_index], "incorrect")
            else:
                
                backup_questions[i].add_child(root, "incorrect")
        
        return root
    
    def get_qst_api(self, subject, count=15):
        #Fetch questions from API 
        self.loading_labl.config(text="Loading questions...")
        
        try:
            
            
            api_url = "https://opentdb.com/api.php"
            
            # Map the subjects to API categories 
            category_map = {
                "Math": 19,  
                "Geography": 22,
                "Science": 17,
                "History": 23,
                "Literature": 10,
                "Mixed": None  
            }
            
            # Prepare parameters
            params = {
                "amount": count,
                "type": "multiple"  # Multiple choice questions
            }
            
            # Add category if not Mixed
            if subject != "Mixed" and category_map[subject]:
                params["category"] = category_map[subject]
                
            # Make API request
            self.debug_log(f"Fetching questions for subject: {subject}")
            response = requests.get(api_url, params=params)
            data = response.json()
            
            # Check if we got valid response
            if response.status_code == 200 and data["response_code"] == 0:
                questions = []
                
                for i, item in enumerate(data["results"]):
                    # Get all answers and shuffle them
                    all_answers = [item["correct_answer"]] + item["incorrect_answers"]
                    random.shuffle(all_answers)
                    
                    # Find the index of the correct answer
                    correct_index = all_answers.index(item["correct_answer"])
                    
                    # Assign difficulty based on position in results (first 5 easy, next 5 medium, last 5 hard)
                    difficulty = 1 if i < 5 else (2 if i < 10 else 3)
                    
                    # Create TreeNode
                    node = TreeNode(
                        question=item["question"],
                        answers=all_answers,
                        correct_answer=correct_index,
                        platform=item["category"],
                        difficulty=difficulty
                    )
                    
                    questions.append(node)
                
                self.loading_labl.config(text="")
                return questions
            else:
                # API error - use fallback questions
                self.debug_log(f"API Error: {data.get('response_code', 'Unknown')}")
                self.loading_labl.config(text="Could not load questions. Using defaults.")
                return self.get_backup_qsts(subject)
                
        except Exception as e:
            # Handle any errors (network issues, etc.)
            self.debug_log(f"Error fetching questions: {str(e)}")
            self.loading_labl.config(text="Network error. Using default questions.")
            return self.get_backup_qsts(subject)
    
    def get_backup_qsts(self, subject):
        #Provide fallback questions 
        fallback_questions = []
        
        if subject == "Math" or subject == "Mixed":
            fallback_questions.extend([
                TreeNode("What is 5 + 3?", ["6", "7", "8", "9"], 2, "Math", 1),
                TreeNode("What is 12 × 3?", ["33", "36", "39", "42"], 1, "Math", 1),
                TreeNode("What is the square root of 64?", ["6", "7", "8", "9"], 2, "Math", 2),
                TreeNode("What is 20% of 80?", ["12", "16", "20", "24"], 1, "Math", 2),
                TreeNode("If x + 5 = 12, what is x?", ["5", "6", "7", "8"], 2, "Math", 3)
            ])
        
        if subject == "Geography" or subject == "Mixed":
            fallback_questions.extend([
                TreeNode("What is the capital of France?", ["Berlin", "Madrid", "Paris", "Rome"], 2, "Geography", 1),
                TreeNode("What is the capital of Japan?", ["Beijing", "Seoul", "Tokyo", "Bangkok"], 2, "Geography", 1),
                TreeNode("Which is the largest ocean?", ["Atlantic", "Indian", "Arctic", "Pacific"], 3, "Geography", 2),
                TreeNode("What is the capital of Australia?", ["Sydney", "Melbourne", "Canberra", "Perth"], 2, "Geography", 2),
                TreeNode("Which country is known as the Land of the Rising Sun?", ["China", "Japan", "Thailand", "Korea"], 1, "Geography", 3)
            ])
        
        if subject == "Science" or subject == "Mixed":
            fallback_questions.extend([
                TreeNode("Which planet is known as the Red Planet?", ["Earth", "Mars", "Jupiter", "Venus"], 1, "Science", 1),
                TreeNode("Which element has the symbol 'O'?", ["Gold", "Silver", "Oxygen", "Osmium"], 2, "Science", 1),
                TreeNode("What is the largest planet in our solar system?", ["Earth", "Mars", "Jupiter", "Saturn"], 2, "Science", 2),
                TreeNode("What is the chemical symbol for water?", ["Wa", "H2O", "W", "HO"], 1, "Science", 2),
                TreeNode("Which animal has the longest lifespan?", ["Elephant", "Giant Tortoise", "Whale", "Human"], 1, "Science", 3)
            ])
        
        if subject == "History" or subject == "Mixed":
            fallback_questions.extend([
                TreeNode("In which year did World War II end?", ["1943", "1945", "1947", "1950"], 1, "History", 1),
                TreeNode("Who was the first President of the United States?", ["Thomas Jefferson", "George Washington", "John Adams", "Benjamin Franklin"], 1, "History", 1),
                TreeNode("In which year did the Titanic sink?", ["1910", "1912", "1915", "1918"], 1, "History", 2),
                TreeNode("Which empire was ruled by Caesar?", ["Greek", "British", "Roman", "Persian"], 2, "History", 2),
                TreeNode("Which war is also known as the Great War?", ["Civil War", "World War I", "World War II", "Cold War"], 1, "History", 3)
            ])
        
        if subject == "Literature" or subject == "Mixed":
            fallback_questions.extend([
                TreeNode("Who wrote 'Romeo and Juliet'?", ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"], 1, "Literature", 1),
                TreeNode("Who wrote 'Pride and Prejudice'?", ["Emily Brontë", "Jane Austen", "Virginia Woolf", "Charlotte Brontë"], 1, "Literature", 1),
                TreeNode("Who created Sherlock Holmes?", ["Agatha Christie", "Arthur Conan Doyle", "Edgar Allan Poe", "H.G. Wells"], 1, "Literature", 2),
                TreeNode("Which book features a character named Harry Potter?", ["The Hobbit", "Harry Potter and the Philosopher's Stone", "The Lion, the Witch and the Wardrobe", "Percy Jackson"], 1, "Literature", 2),
                TreeNode("Who wrote 'To Kill a Mockingbird'?", ["J.D. Salinger", "Harper Lee", "F. Scott Fitzgerald", "Ernest Hemingway"], 1, "Literature", 3)
            ])
        
        # For Mixed, we already added some from each category
        # If not Mixed and we're here, we have all the questions for the specific subject
        
        # Shuffle the fallback questions
        random.shuffle(fallback_questions)
        
        # Limit to 15 questions maximum
        return fallback_questions[:15]

    def start_game(self):
        # Disable subject dropdown
        self.subject_select.config(state="disabled")
        
        # Remove start button
        self.strt_btn_frm.pack_forget()
            
        # Hide any messages
        self.loading_labl.config(text="")
        
        # Get selected subject
        subject = self.selected_subj.get()
        self.debug_log(f"Starting game with subject: {subject}")
        
        # Create question tree
        self.question_tree_root = self.make_qst_tree(subject)
        
        # Start with the root node
        self.crnt_node = self.question_tree_root
        self.path_history = ["Root"]
        
        # Animate boss entrance
        self.boss_entry_anm()
        
    def boss_entry_anm(self):
        # Animate the boss flying in
        current_x = 800
        current_y = 100
        
        def updt_boss_pos(x, y):
            if x > 650:
                self.canvas.coords(self.boss, x, y)
                self.after(50, lambda: updt_boss_pos(x - 10, y))
            else:
                self.Intro_msg()
                
        self.canvas.coords(self.boss, current_x, current_y)
        updt_boss_pos(current_x, current_y)
        
    def Intro_msg(self):
        subject = self.selected_subj.get()
        messagebox.showinfo("Tree Defender", f"The {subject} Syntax Wave Boss is attacking the knowledge tree! Answer correctly to defend and defeat the boss!")
        # Display the first question (root of the tree)
        self.current_qst()

    def current_qst(self):
        #Display the current question from the tree traversal
        if not self.crnt_node:
            self.debug_log("No current node! Showing victory")
            self.win_anm()
            return
            
        # Update tree path visualization
        self.tree_path.config(text=f"Question Tree Path: {' -> '.join(self.path_history)}")
        
        # Update question with animation effect
        self.question_lbl.config(text="")
        question_text = f"[{self.crnt_node.platform}] {self.crnt_node.question}"
        
        def animate_txt(text, i=0):
            if i <= len(text):
                self.question_lbl.config(text=text[:i])
                self.after(30, lambda: animate_txt(text, i + 1))
                
        animate_txt(question_text)
        
        # Enable and update answer buttons
        for i, ans in enumerate(self.crnt_node.answers):
            self.btns[i].config(text=ans, state=tk.NORMAL)
        
        # Reset player movement flag to allow movement
        self.allowed_move = True

    def check_answer(self, chosen_index):
        if self.attacking or not self.allowed_move:
            self.debug_log("Player tried to move while locked")
            return  # Prevent input during attacks or when movement is locked
            
        # Disable buttons during animation
        for btn in self.btns:
            btn.config(state=tk.DISABLED)
            
        # Move player to selected platform
        self.move_player(chosen_index)
        
        if chosen_index == self.crnt_node.correct_answer:
            self.correct_answer()
        else:
            self.wrong_answer(chosen_index)

    def move_player(self, platform_index):
        if not self.allowed_move:
            self.debug_log("Movement blocked - player cannot move")
            return
            
        self.crnt_platform_indx = platform_index
        target_x = self.platforms[platform_index]["x"]
        target_y = self.platforms[platform_index]["y"] - 25  # Position above platform
        
        current_x, current_y = self.canvas.coords(self.player)
        self.movement_anm(current_x, current_y, target_x, target_y)

    def movement_anm(self, current_x, current_y, target_x, target_y, steps=20):
        if steps <= 0:
            return
            
        # Calculate movement 
        dx = (target_x - current_x) / steps
        dy = (target_y - current_y) / steps
        
        # Update position
        self.canvas.coords(self.player, current_x + dx, current_y + dy)
        
        # Continue animation
        self.after(20, lambda: self.movement_anm(
            current_x + dx, current_y + dy, target_x, target_y, steps - 1))

    def correct_answer(self):
        # Visual feedback for correct answer
        platform = self.platforms[self.crnt_node.correct_answer]["shape"]
        original_color = self.canvas.itemcget(platform, "fill")
        
        def platform_anm(count=6):
            if count > 0:
                color = "#2ECC71" if count % 2 == 0 else original_color
                self.canvas.itemconfig(platform, fill=color)
                self.after(200, lambda: platform_anm(count - 1))
            else:
                self.canvas.itemconfig(platform, fill=original_color)
                self.attack_boss()
                
        platform_anm()
        messagebox.showinfo("Correct!", "✅ Excellent! Time to counter-attack!")
        
    def attack_boss(self):
        # Create player attack projectile
        player_x, player_y = self.canvas.coords(self.player)
        boss_x, boss_y = self.canvas.coords(self.boss)
        
        self.debug_log(f"Creating attack from player to boss")
        
        # Create an energy bolt
        bolt = self.canvas.create_oval(
            player_x - 10, player_y - 10, 
            player_x + 10, player_y + 10, 
            fill="#2ECC71", outline="#FFFFFF"
        )
        
        def update_bolt(obj, x, y):
            # Calculate distance to boss
            distance = math.sqrt((boss_x - x)**2 + (boss_y - y)**2)
            
            if distance > 20:  # Stop when we get close to the boss
                # Calculate trajectory
                dx = (boss_x - x) / 10
                dy = (boss_y - y) / 10
                
                # Move the bolt
                self.canvas.move(obj, dx, dy)
                x += dx
                y += dy
                
                self.after(30, lambda: update_bolt(obj, x, y))
            else:
                # Bolt hit the boss
                self.debug_log("Bolt hit boss")
                self.canvas.delete(obj)
                self.boss_hit_anm()
                
        update_bolt(bolt, player_x, player_y)
        
    def boss_hit_anm(self):
        # Visual effect for boss hit
        boss_x, boss_y = self.canvas.coords(self.boss)
        
        # Flag to ensure update_boss_health is called only once
        self.hit_processed = False
        
        # Flash effect
        explosion = self.canvas.create_oval(
            boss_x - 30, boss_y - 30,
            boss_x + 30, boss_y + 30,
            fill="#E74C3C", outline="#F1C40F", width=2
        )
        
        self.debug_log("Starting explosion effect")
        
        def fade_explosion(obj, size=30, alpha=1.0):
            if size < 60 and alpha > 0:
                self.canvas.coords(
                    obj,
                    boss_x - size, boss_y - size,
                    boss_x + size, boss_y + size
                )
                size += 3
                alpha -= 0.1
                self.after(50, lambda: fade_explosion(obj, size, alpha))
            else:
                self.canvas.delete(obj)
                # Only call update_boss_health once
                if not self.hit_processed:
                    self.hit_processed = True
                    self.debug_log("Explosion complete, calling update_boss_health")
                    self.upd_boss_health()
                
        fade_explosion(explosion)
        
    def upd_boss_health(self):
        self.debug_log(f"Boss health before: {self.boss_hlth}")
        self.boss_hlth -= 1
        self.score += 100 * self.crnt_node.difficulty  # Higher score for harder questions
        self.debug_log(f"Boss health after: {self.boss_hlth}")
        
        # Update display
        heart_emoji = "❤️"
        self.canvas.itemconfig(
            self.boss_health_txt, 
            text=f"Boss Health: {self.boss_hlth} {heart_emoji}"
        )
        
        self.canvas.itemconfig(
            self.score_txt,
            text=f"Score: {self.score} | Level: {self.level}"
        )
        
        # Update the current node and traverse to the next correct node
        next_node = self.crnt_node.children["correct"]
        if next_node:
            self.debug_log(f"Moving to next node in 'correct' path")
            self.crnt_node = next_node
            # Update path history
            difficulty_emoji = "🟢" if next_node.difficulty == 1 else ("🟡" if next_node.difficulty == 2 else "🔴")
            self.path_history.append(f"{difficulty_emoji} Q{len(self.path_history)}")
        else:
            # No more nodes in the tree, player wins!
            self.debug_log("No more nodes in the 'correct' path - Victory!")
            self.crnt_node = None
        
        # Check if boss is defeated
        if self.boss_hlth <= 0:
            self.debug_log("Boss defeated! Triggering victory animation")
            self.win_anm()
        else:
            self.debug_log("Boss still alive, continuing game")
            self.after(1000, self.continue_game)
            
    def win_anm(self):
        # Make boss disappear with explosion effect
        boss_x, boss_y = self.canvas.coords(self.boss)
        
        # Create multiple explosion particles
        particles = []
        for _ in range(10):
            angle = random.uniform(0, 3.14 * 2)
            speed = random.uniform(2, 8)
            dx = speed * math.cos(angle)
            dy = speed * math.sin(angle)
            size = random.randint(5, 15)
            color = random.choice(["#E74C3C", "#F39C12", "#F1C40F"])
            
            particle = self.canvas.create_oval(
                boss_x - size, boss_y - size,
                boss_x + size, boss_y + size,
                fill=color
            )
            
            particles.append({
                "obj": particle,
                "dx": dx,
                "dy": dy,
                "life": 20
            })
            
        def upd_particle():
            still_alive = False
            for p in particles:
                if p["life"] > 0:
                    self.canvas.move(p["obj"], p["dx"], p["dy"])
                    p["life"] -= 1
                    p["dx"] *= 0.95
                    p["dy"] *= 0.95
                    still_alive = True
                else:
                    self.canvas.delete(p["obj"])
                    
            if still_alive:
                self.after(50, upd_particle)
            else:
                self.canvas.delete(self.boss)
                self.victor_msg()
                
        upd_particle()
        
    def victor_msg(self):
        subject = self.selected_subj.get()
        messagebox.showinfo("Victory!", f"🎉 You defeated the {subject} Syntax Wave Boss!\nYou completed the knowledge tree with a score of {self.score}!")
        
        # Show a diagram of the path taken through the tree
        path_str = " -> ".join(self.path_history)
        messagebox.showinfo("Tree Path", f"Your path through the knowledge tree:\n{path_str}")
        
        # Ask if player wants to continue to next level
        if messagebox.askyesno("Next Level", "Do you want to proceed to the next level?"):
            self.level += 1
            self.boss_hlth = 3 + self.level  # Increase difficulty
            self.canvas.itemconfig(
                self.score_txt,
                text=f"Score: {self.score} | Level: {self.level}"
            )
            
            # Recreate boss
            self.boss_img = ImageTk.PhotoImage(Image.open("pics/boss.png").resize((120, 120)))
            self.boss = self.canvas.create_image(800, 100, image=self.boss_img)
            
            # Update boss health display
            heart_emoji = "❤️"
            self.canvas.itemconfig(
                self.boss_health_txt, 
                text=f"Boss Health: {self.boss_hlth} {heart_emoji}"
            )
            
            # Get selected subject and create new question tree
            subject = self.selected_subj.get()
            self.question_tree_root = self.make_qst_tree(subject)
            
            # Reset path history and start with the root node
            self.crnt_node = self.question_tree_root
            self.path_history = ["Root"]
            
            # Start new round
            self.boss_entry_anm()
        else:

            # Recreate boss
            self.boss_img = ImageTk.PhotoImage(Image.open("pics/boss.png").resize((120, 120)))
            self.boss = self.canvas.create_image(800, 100, image=self.boss_img)
            # Reset game for a new session
            self.reset_game()
            
    def reset_game(self):
        #Reset the game 
        # Reset game state
        self.boss_hlth = 3
        self.player_hlth = 3
        self.score = 0
        self.level = 1
        self.crnt_node = None
        self.path_history = ["Root"]
        self.attacking = False
        self.allowed_move = True
        
        # Update displays
        heart_emoji = "❤️"
        self.canvas.itemconfig(
            self.boss_health_txt, 
            text=f"Boss Health: {self.boss_hlth} {heart_emoji}"
        )
        self.canvas.itemconfig(
            self.player_health_txt, 
            text=f"Your Health: {self.player_hlth} {heart_emoji}"
        )
        self.canvas.itemconfig(
            self.score_txt,
            text=f"Score: {self.score} | Level: {self.level}"
        )
        
        # Reset player and boss positions
        self.canvas.coords(self.boss, 650, 100)
        self.canvas.coords(self.player, 100, 350)
        
        # Enable subject selection
        self.subject_select.config(state="normal")
        
        # Clear question text and buttons
        self.question_lbl.config(text="")
        for btn in self.btns:
            btn.config(text="", state=tk.DISABLED)
        
        # Clear tree path label
        self.tree_path.config(text="Question Tree Path: Root")
        
        # Show the start button frame again - make sure it's visible!
        self.strt_btn_frm.grid(row=5, column=0, pady=(10, 10), sticky="ew")
        
        # Make sure the start button is visible
        self.strt_btn.pack()
        
        # Update loading label
        self.loading_labl.config(text="Select a subject and click 'Start Game' to begin!")

    def wrong_answer(self, chosen_index):
        # Set the attack flag and prevent player movement during attack sequence
        self.attacking = True
        self.allowed_move = False
        self.debug_log(f"Wrong answer selected: {chosen_index}. Player locked in place.")
        
        # Store the chosen platform index - this ensures the attack hits the right platform
        self.target_platform = chosen_index
        
        # Visual feedback for wrong platform
        platform = self.platforms[chosen_index]["shape"]
        original_color = self.canvas.itemcget(platform, "fill")
        self.canvas.itemconfig(platform, fill="#E74C3C")
        
        # Show correct answer
        correct_platform = self.platforms[self.crnt_node.correct_answer]["shape"]
        self.canvas.itemconfig(correct_platform, fill="#2ECC71")
        
        # Show message before attack
        messagebox.showinfo("Incorrect!", f"❌ Wrong answer! The correct answer was: {self.crnt_node.answers[self.crnt_node.correct_answer]}")
        messagebox.showinfo("Boss Attack", "The boss is attacking!")
        
        # Boss attack animation
        self.animate_boss_attack(chosen_index)
        
        # Reset platform colors after a delay
        def reset_colors():
            self.canvas.itemconfig(platform, fill=original_color)
            self.canvas.itemconfig(correct_platform, fill=original_color)
            
        self.after(2000, reset_colors)

    def animate_boss_attack(self, target_platform):
        # Get positions
        boss_x, boss_y = self.canvas.coords(self.boss)
        target_x = self.platforms[target_platform]["x"]
        target_y = self.platforms[target_platform]["y"] - 25
        
        # Create attack projectile
        fireball = self.canvas.create_text(
            boss_x, boss_y, text="🔥", font=("Arial", 100),fill="red",
        )
        
        self.debug_log(f"Boss attack launched at platform {target_platform}")
        
        # Animate projectile
        def update_fireball(obj, x, y, steps=0):
            # Calculate direction vector
            dx = (target_x - x) / 20
            dy = (target_y - y) / 20
            
            # Check if we've reached target (or close enough)
            distance = math.sqrt((target_x - x)**2 + (target_y - y)**2)
            
            if distance > 20 and steps < 100:  # Add steps limit as failsafe
                # Move the fireball
                self.canvas.move(obj, dx, dy)
                x += dx
                y += dy
                
                self.after(20, lambda: update_fireball(obj, x, y, steps + 1))
            else:
                # Create explosion effect
                self.debug_log(f"Fireball reached target at ({x:.2f}, {y:.2f})")
                
                # Clear the fireball
                self.canvas.delete(obj)
                
                explosion = self.canvas.create_oval(
                    target_x - 20, target_y - 20,
                    target_x + 20, target_y + 20,
                    fill="#E74C3C", outline="#F1C40F", width=2
                )
                
                def fade_explosion(exp_obj, size=20):
                    if size < 40:
                        self.canvas.coords(
                            exp_obj,
                            target_x - size, target_y - size,
                            target_x + size, target_y + size
                        )
                        size += 2
                        self.after(30, lambda: fade_explosion(exp_obj, size))
                    else:
                        self.canvas.delete(exp_obj)
                        # Explicitly apply damage here
                        self.debug_log("Explosion complete - applying damage to player")
                        self.apply_damage_to_player()
                
                fade_explosion(explosion)
        
        update_fireball(fireball, boss_x, boss_y)
        
    def apply_damage_to_player(self):
        """Apply damage to player regardless of position, as they've committed to the wrong answer"""
        self.debug_log("Player taking damage from boss attack")
        
        # Reduce player health
        self.player_hlth -= 1
        
        # Update health display with animation
        heart_emoji = "❤️"
        
        # Flash the health text red
        def flash_health_text(count=6):
            if count > 0:
                color = "#FF0000" if count % 2 == 0 else "#2ECC71"
                self.canvas.itemconfig(self.player_health_txt, fill=color)
                self.after(100, lambda: flash_health_text(count - 1))
            else:
                self.canvas.itemconfig(
                    self.player_health_txt, 
                    text=f"Your Health: {self.player_hlth} {heart_emoji}",
                    fill="#2ECC71"
                )
                self.check_game_over()
        
        flash_health_text()
        
        # Visual feedback for player hit
        player_x, player_y = self.canvas.coords(self.player)
        hit_effect = self.canvas.create_oval(
            player_x - 25, player_y - 25,
            player_x + 25, player_y + 25,
            fill="#E74C3C", outline="white", width=2
        )
        
        def fade_hit(obj, opacity=1.0):
            if opacity > 0:
                # Can't change opacity directly in tkinter, so simulate it
                self.after(100, lambda: fade_hit(obj, opacity - 0.2))
            else:
                self.canvas.delete(obj)
        
        fade_hit(hit_effect)
        
    def check_game_over(self):
        if self.player_hlth <= 0:
            subject = self.selected_subj.get()
            messagebox.showerror("Game Over", f"💀 You were defeated by the {subject} Syntax Wave Boss!")
            
            # Show path taken before defeat
            path_str = " -> ".join(self.path_history)
            messagebox.showinfo("Tree Path", f"Your path through the knowledge tree:\n{path_str}")
            
            # Ask if player wants to restart
            if messagebox.askyesno("Play Again?", "Would you like to play again with the same subject?"):
                # Reset game to start state with same subject
                self.debug_log("Resetting game to initial state with same subject")
                
                # Reset all game variables
                self.boss_hlth = 3
                self.player_hlth = 3
                self.score = 0
                self.level = 1
                self.crnt_node = None
                self.path_history = ["Root"]
                self.attacking = False
                self.allowed_move = True
                
                # Update displays
                heart_emoji = "❤️"
                self.canvas.itemconfig(
                    self.boss_health_txt, 
                    text=f"Boss Health: {self.boss_hlth} {heart_emoji}"
                )
                self.canvas.itemconfig(
                    self.player_health_txt, 
                    text=f"Your Health: {self.player_hlth} {heart_emoji}"
                )
                self.canvas.itemconfig(
                    self.score_txt,
                    text=f"Score: {self.score} | Level: {self.level}"
                )
                
                # Reset player and boss positions
                self.canvas.coords(self.boss, 650, 100)
                self.canvas.coords(self.player, 100, 350)
                
                # Disable subject selection since we're using the same subject
                self.subject_select.config(state="disabled")
                
                # Clear question text and buttons
                self.question_lbl.config(text="")
                for btn in self.btns:
                    btn.config(text="", state=tk.DISABLED)
                
                # Clear tree path label
                self.tree_path.config(text="Question Tree Path: Root")
                
                # Create a new question tree based on the selected subject
                subject = self.selected_subj.get()
                self.question_tree_root = self.make_qst_tree(subject)
                
                # Set current node to the root of the tree
                self.crnt_node = self.question_tree_root
                
                # Simply call start_game directly to restart
                self.start_game()
            else:
                # Reset the game completely
                self.reset_game()
        else:
            self.attacking = False
            
            # Tree traversal happens here for incorrect answers
            # Move to the incorrect branch of the tree
            next_node = self.crnt_node.children["incorrect"]
            if next_node:
                self.debug_log(f"Moving to next node in 'incorrect' path")
                self.crnt_node = next_node
                # Update path history for incorrect path
                difficulty_emoji = "🟢" if next_node.difficulty == 1 else ("🟡" if next_node.difficulty == 2 else "🔴")
                self.path_history.append(f"{difficulty_emoji} Q{len(self.path_history)}*")  # * marks incorrect path
            else:
                # No incorrect path defined, stay on current node and retry
                self.debug_log("No 'incorrect' path defined - retrying current question")
            
            self.allowed_move = True  # Re-enable player movement
            self.debug_log("Attack sequence complete, player movement re-enabled")
            self.after(1000, self.continue_game)

    def continue_game(self):
        for btn in self.btns:
            btn.config(state=tk.DISABLED)
            
        # Reset attack flag
        self.attacking = False
        self.allowed_move = True  # Ensure player can move again
        
        # Tree traversal - display the current node (either next correct node or incorrect branch)
        if self.crnt_node:
            self.current_qst()
        else:
            # No more nodes in the tree, player wins!
            self.win_anm()