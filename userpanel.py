import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from graph_bar import ScoreVisualizer
from resources import ResourceLibrary
from analyse import StudyAdvisorApp
from quotes import MotivationQuote
from examcountdow import ExamCountdown
from availability import AvailabilityEditor
from scores import ScoreManager

class Userpanel(ctk.CTkFrame):
    def __init__(self, parent, user_id, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        
        self.user_id = user_id

        #color scheme 
        self.colors = {
            "bg_main": "#111827",           
            "header": "#1E293B",            
            "section_header": "#2C3E50",    
            "bg_card": "#1F2A3C",           
            "accent_purple": "#8B5CF6",     
            "accent_blue": "#3B82F6",        
            "button_red": "#EF4444",        
            "text_primary": "#FFFFFF",      
            "text_secondary": "#D1D5DB"     
        }

        self.configure(fg_color=self.colors["bg_main"])
        
        # Configure the grid with proper weights
        self.columnconfigure(0, weight=1)  
        self.columnconfigure(1, weight=2)  
        self.columnconfigure(2, weight=1)  
        self.rowconfigure(0, weight=0)     
        self.rowconfigure(1, weight=1)     
        
        # Create the UI components
        self.header()
        self.main_sections()

    def header(self):
        #Create a header bar 
        hdr = ctk.CTkFrame(self, fg_color=self.colors["header"], corner_radius=0, height=50) # hdr = header 
        hdr.grid(row=0, column=0, columnspan=3, sticky="ew", padx=0, pady=(0, 0))
        
        # Title
        title = ctk.CTkLabel(hdr, text="ECLIPSE DASHBOARD", font=("Arial", 16, "bold"),text_color=self.colors["text_primary"])
        title.pack(side="left", padx=20, pady=8)
        
        # User info
        user_frm = ctk.CTkFrame(hdr, fg_color="transparent")
        user_frm.pack(side="right", padx=20, pady=8)
        
        user_dipl = ctk.CTkLabel( user_frm, text=f"👤 User ID: {self.user_id}", font=("Arial", 12),text_color=self.colors["text_primary"]) # dipl = display
        user_dipl.pack(side="right")

    def main_sections(self):
        padding = {"padx": 8, "pady": 8}

        # I use this to see 
        
        # 1.  (LEFT COLUMN)
        left_sect = self.section_frame(0, "Resources & Deadlines", padding)
        self.resources(left_sect)
        self.exam_countdown(left_sect)
        
        # 2.  (CENTER COLUMN)
        center_sect = self.section_frame(1, "Progress & Performance", padding)
        self.Run_quotes(center_sect)
        self.Graph(center_sect)
        
        # 3.  (RIGHT COLUMN)
        right_sect = self.section_frame(2, "Schedule & Scores", padding)
        self.availability(right_sect)
        self.score_manager(right_sect)
        self.analysis(right_sect)

    def section_frame(self, column, title, padding):
        # main frame for section
        section = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        section.grid(row=1, column=column, sticky="nsew", **padding)
        
    
        section.columnconfigure(0, weight=1)
        
        
        section.rowconfigure(0, weight=0) 
        section.rowconfigure(1, weight=1)  
        section.rowconfigure(2, weight=1)  
        section.rowconfigure(3, weight=0)  
        
        # Add the section title
        title_frame = ctk.CTkFrame(section, fg_color=self.colors["bg_card"], corner_radius=8, height=36)
        title_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 8))
        
        # Title text
        title_label = ctk.CTkLabel(
            title_frame, 
            text=title, 
            font=("Arial", 14, "bold"),
            text_color=self.colors["text_primary"]
        )
        title_label.pack(pady=8)
        
        return section

    def resources(self, parent_frame):
        
        resources_frm = ctk.CTkFrame(parent_frame, fg_color=self.colors["bg_card"], corner_radius=8)
        resources_frm.grid(row=1, column=0, sticky="nsew", padx=0, pady=(0, 8))
        
        

        resource_ttl_frm = ctk.CTkFrame(resources_frm, fg_color="transparent", height=30)
        resource_ttl_frm.pack(fill="x", padx=15, pady=(10, 0))
        
        resource_ttl = ctk.CTkLabel(resource_ttl_frm, text="📚 Learning Resources", font=("Arial", 14, "bold"),text_color=self.colors["text_primary"])
        resource_ttl.pack(anchor="w")
        
        
        resource_cont = ctk.CTkFrame(resources_frm, fg_color="#2D3748")
        resource_cont.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.resource_lib = ResourceLibrary(resource_cont)
        self.resource_lib.pack(fill="both", expand=True)

    def exam_countdown(self, parent_frame):
        
        
        sched_frame = ctk.CTkFrame(parent_frame, fg_color=self.colors["bg_card"], corner_radius=8)
        sched_frame.grid(row=2, column=0, sticky="nsew", padx=0, pady=(0, 8))
        
        # Exam schedule title
        sched_ttl_frame = ctk.CTkFrame(sched_frame, fg_color="transparent", height=30)
        sched_ttl_frame.pack(fill="x", padx=15, pady=(10, 0))
        
        sched_title = ctk.CTkLabel(sched_ttl_frame, text="📅 Exam Schedule", font=("Arial", 14, "bold"),text_color=self.colors["text_primary"])
        sched_title.pack(anchor="w")
        
        # Initialize Exam Countdown - DO NOT set fg_color here
        exam_container = ctk.CTkFrame(sched_frame, fg_color="#2D3748")
        exam_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.countdown = ExamCountdown(exam_container)
        self.countdown.pack(fill="both", expand=True)

    def Run_quotes(self, parent_frame):
        
        
        quote = ctk.CTkFrame(parent_frame, fg_color=self.colors["accent_purple"], corner_radius=8)
        quote.grid(row=1, column=0, sticky="nsew", padx=0, pady=(0, 8))
        
        # Initialize Motivation Quote directly in the purple frame
        self.quotes = MotivationQuote(quote)
        # Important: Don't change its fg_color, which could cause rendering issues
        self.quotes.pack(fill="both", expand=True, padx=10, pady=10)

    def Graph(self, parent_frame):
        
        
        performa = ctk.CTkFrame(parent_frame, fg_color=self.colors["bg_card"], corner_radius=8)
        performa.grid(row=2, column=0, sticky="nsew", padx=0, pady=(0, 8))
        
        # Performance title
        title_frame = ctk.CTkFrame(performa, fg_color="transparent", height=30)
        title_frame.pack(fill="x", padx=15, pady=(10, 0))
        
        title = ctk.CTkLabel(title_frame, text="📊 Performance Metrics", font=("Arial", 14, "bold"),text_color=self.colors["text_primary"])
        title.pack(anchor="w")
        
        
        self.progress = ctk.CTkFrame(performa, fg_color="#2D3748", height=400)
        self.progress.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Important: Don't override ScoreVisualizer's internal styling
        self.graph = ScoreVisualizer(self.progress, self.user_id)
        self.graph.pack(fill="both", expand=True)

    def availability(self, parent_frame):
        
        # Container for the first component (Availability)
        avail_frame = ctk.CTkFrame(parent_frame, fg_color=self.colors["bg_card"], corner_radius=8)
        avail_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=(0, 8))
        
        # Availability title
        title_frame = ctk.CTkFrame(avail_frame, fg_color="transparent", height=30)
        title_frame.pack(fill="x", padx=15, pady=(10, 0))
        
        title = ctk.CTkLabel(title_frame, text="⏰ Weekly Availability", font=("Arial", 14, "bold"),text_color=self.colors["text_primary"])
        title.pack(anchor="w")
        
        # Initialize Availability Editor - Important: give it enough height
        avail_container = ctk.CTkFrame(avail_frame, fg_color="#2D3748", height=350)
        avail_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Create the availability editor without changing its fg_color
        availability = AvailabilityEditor(avail_container, self.user_id)
        availability.pack(fill="both", expand=True)

    def score_manager(self, parent_frame):
        
        # Container for the second component (Score Manager)
        score_frame = ctk.CTkFrame(parent_frame, fg_color=self.colors["bg_card"], corner_radius=8)
        score_frame.grid(row=2, column=0, sticky="nsew", padx=0, pady=(0, 8))
        
        # Score manager title
        title_frame = ctk.CTkFrame(score_frame, fg_color="transparent", height=30)
        title_frame.pack(fill="x", padx=15, pady=(10, 0))
        
        title = ctk.CTkLabel(title_frame, text="🎯 Score Manager", font=("Arial", 14, "bold"),text_color=self.colors["text_primary"])
        title.pack(anchor="w")
        
        container = ctk.CTkFrame(score_frame, fg_color="#2D3748", height=300)
        container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Create score manager without changing its fg_color
        score_manager = ScoreManager(container, self.user_id)
        score_manager.pack(fill="both", expand=True)

    def analysis(self, parent_frame):
        
        
        btn_frm = ctk.CTkFrame(parent_frame, fg_color="transparent")
        btn_frm.grid(row=3, column=0, sticky="nsew", padx=0, pady=(0, 0))
        
        
        self.analysis_brn = ctk.CTkButton(btn_frm, text='📈 Analyze Performance', command=self.run_analysis,fg_color=self.colors["button_red"],hover_color="#E73535",font=("Arial", 14, "bold"),corner_radius=6,height=45)
        self.analysis_brn.pack(fill="x", pady=0)

    def run_analysis(self):

        
        for widget in self.grid_slaves():
            if int(widget.grid_info()["column"]) == 1 and int(widget.grid_info()["row"]) == 1:
                widget.destroy()
                break
        
        # create analysis ui
        analysis_sect = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        analysis_sect.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)
        
        
        title_frm = ctk.CTkFrame(analysis_sect, fg_color=self.colors["bg_card"], corner_radius=8, height=36)
        title_frm.pack(fill="x", pady=(0, 8))
        
        title = ctk.CTkLabel(title_frm, text="Advanced Analytics", font=("Arial", 14, "bold"),text_color=self.colors["text_primary"])
        title.pack(pady=8)
        
        
        content_frame = ctk.CTkFrame(analysis_sect, fg_color=self.colors["bg_card"], corner_radius=8, height=600)
        content_frame.pack(fill="both", expand=True, pady=(0, 8))
        
        
        self.analysis = StudyAdvisorApp(content_frame,self.user_id)
        self.analysis.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Return button
        btn_frame = ctk.CTkFrame(analysis_sect, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        return_btn = ctk.CTkButton(btn_frame,text="← Return to Dashboard",command=self.exit,fg_color=self.colors["bg_card"],hover_color="#324056",font=("Arial", 14),corner_radius=6,height=40)
        return_btn.pack(fill="x")

    def exit(self):
        #Return to the main dashboard view
        
        for widget in self.grid_slaves():
            if int(widget.grid_info()["column"]) == 1 and int(widget.grid_info()["row"]) == 1:
                widget.destroy()
                break
        
        # Recreate the center section
        center_sect = self.section_frame(1, "Progress & Performance", {"padx": 8, "pady": 8})
        self.Run_quotes(center_sect)
        self.Graph(center_sect)