from customtkinter import *
import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
from pomodoro_timer import pomodoro_timer
from flashcard_v import FlashCardMainApp
from calander import CustomCalendar
from userpanel import Userpanel
from home_page import Homepage
from user_profile import UserProfile
from tree_game_v import TreeDefenderGame
from calculator_normal import check_setup, complete_setup



class MainApp(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()

        self.user_id = user_id
        self.user_id_tp = tuple(str(user_id))

        # Configure main window
        self.title("Eclipse")
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        set_appearance_mode("dark")

        # Protocol for closing the window
        self.protocol("WM_DELETE_WINDOW", self.on_close) 

        # Main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        
        if check_setup(self.user_id):
            self.finish_singup()
        else:
            self.start_app()

    def finish_singup(self):
        #Show a welcome screen 
        
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        welcome_frm = ctk.CTkFrame(self.main_frame)
        welcome_frm.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Welcome message
        ctk.CTkLabel(welcome_frm, text="Welcome to Eclipse Learning!", font=("Arial", 24, "bold")).pack(pady=(50, 20))
        
        ctk.CTkLabel(welcome_frm, text="Before you begin, we need to set up your availability and subjects.", font=("Arial", 16),wraplength=600).pack(pady=(0, 30))
        
        # Info
        info_frm = ctk.CTkFrame(welcome_frm)
        info_frm.pack(fill="x", padx=50, pady=20)
        
        ctk.CTkLabel(info_frm, text="We'll need you to:", font=("Arial", 14, "bold"),anchor="w").pack(fill="x", pady=(10, 5), padx=10)
        
        ctk.CTkLabel(info_frm, text="• Add your subjects (e.g., Math, English, Science)", font=("Arial", 14),anchor="w").pack(fill="x", pady=5, padx=30)
        
        ctk.CTkLabel(info_frm, text="• Set your weekly availability for each day", font=("Arial", 14),anchor="w").pack(fill="x", pady=5, padx=30)
        
        ctk.CTkLabel(info_frm, text="• This helps us create an optimal study schedule for you", font=("Arial", 14),anchor="w").pack(fill="x", pady=(5, 10), padx=30)
        
        # Button to continue to setup
        ctk.CTkButton(welcome_frm, text="Continue to Setup", font=("Arial", 16, "bold"),width=250, height=50,command=self.start_setup).pack(pady=40)

    def start_setup(self):
        #Show a setup screen
        complete_setup(self.user_id, callback=self.start_app)

    def start_app(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Tab bar (left sidebar)
        self.Func_frm = CTkFrame(master=self.main_frame, fg_color="#22333B", width=250)
        self.Func_frm.pack_propagate(False)  # Prevent size changes
        self.Func_frm.pack(side="left", fill="y")

        logo_frm = CTkFrame(self.Func_frm, fg_color="transparent", width=50, height=200)
        logo_frm.pack(fill="both", expand=False, side="top")

        CTkFrame(self.Func_frm, fg_color="transparent", width=50, height=200).pack(fill="both", expand=False, side="top")
        
        # Application 
        self.application_frm = CTkFrame(master=self.main_frame, fg_color="#222222")
        self.application_frm.pack(side="right", expand=True, fill="both")

        self.tab_buttons = {}
        tab_container = CTkFrame(self.Func_frm, fg_color="transparent")
        tab_container.pack(fill="both", side="top")

        # Load images
        self.images = {
            'logo': CTkImage(Image.open("Pics/user_profile.png"), size=(100, 100)),
            'timer': CTkImage(Image.open("Pics/hourglass_fb.png"), size=(50, 50)),
            'calendar': CTkImage(Image.open("Pics/calander.png"), size=(50, 50)),
            'flashcards': CTkImage(Image.open("Pics/flashcard.png"), size=(50, 50)),
            'user': CTkImage(Image.open("Pics/userpanel.png"), size=(50, 50)),
            'home': CTkImage(Image.open("Pics/home.png"), size=(50, 50)),
            'settings': CTkImage(Image.open("Pics/Setting.png"), size=(50, 50)),
            'full_screen': CTkImage(Image.open("Pics/window.png"), size=(50, 50)),
            'minigame': CTkImage(Image.open("Pics/minigame.png"), size=(50, 50)),
        }

        # buttons
        tabs = [
            ('home', "Home", self.home_page),
            ('timer', "Pomodoro", self.pomodortimer),
            ('calendar', "Calendar", self.calendar),
            ('flashcards', "Flashcards", self.flashcard),
            ('user', "User Panel", self.user_panel),
            ('minigame', "MiniGame", self.MiniGame)
        ]

        Logo = CTkButton(logo_frm,image=self.images['logo'],text="",compound="left",anchor="center",fg_color="transparent", text_color="white",hover_color="#3a3a3a",command=self.user_profile)
        Logo.pack(side="top", fill="x", pady=2)

        for tab_id, text, command in tabs:
            btn = CTkButton(tab_container,text=text,image=self.images[tab_id],compound="left",anchor="w",fg_color="transparent", text_color="white",hover_color="#3a3a3a",command=command)
            btn.pack(fill="x", pady=5)
            self.tab_buttons[tab_id] = btn

        
        self.settings_btn = CTkButton(self.Func_frm,image=self.images['settings'],text="Settings",compound="left",anchor="w",fg_color="transparent", text_color="white",hover_color="#3a3a3a",command=self.settings)
        self.settings_btn.pack(side="bottom", fill="x", pady=20, padx=10)

        # start homepage
        self.tab_swicth('Home')
        self.home_page()

    def on_close(self):
        #event close
        
        if hasattr(self, 'homepage'):
            self.homepage.task_viewr.save_deletions()  
        self.destroy()  

    def tab_swicth(self, tab_id):
        
        for btn in self.tab_buttons.values():
            btn.configure(fg_color="transparent")  
        
        # Highlight active tab
        if tab_id in self.tab_buttons:
            self.tab_buttons[tab_id].configure(fg_color="#3a3a3a")

    def clear_frame(self): 
        for widget in self.application_frm.winfo_children():
            widget.destroy()

    def pomodortimer(self):
        self.clear_frame()
        self.tab_swicth('timer')
        pomodoro_timer(self.application_frm)

    def user_profile(self):
        self.clear_frame()
        self.tab_swicth('user_profile')
        self.user_profile = UserProfile(self.application_frm, self.user_id)
        self.user_profile.pack(fill="both", expand=True)

    def calendar(self):
        self.clear_frame()
        self.tab_swicth('calendar')
        self.calendar = CustomCalendar(self.application_frm, self.user_id)
        self.calendar.pack(fill="both", expand=True)

    def flashcard(self):
        self.clear_frame()
        self.tab_swicth('flashcards')
        self.flashcard_app = FlashCardMainApp(self.application_frm, self.user_id)
        self.flashcard_app.pack(fill="both", expand=True)

    def user_panel(self):
        self.clear_frame()
        self.tab_swicth('user')
        self.user_panel = Userpanel(self.application_frm, user_id=self.user_id)
        self.user_panel.pack(fill="both", expand=True)

    def home_page(self):
        self.clear_frame()
        self.tab_swicth('home')
        self.homepage = Homepage(self.application_frm, self.user_id, main_frame=self)
        self.homepage.pack(fill="both", expand=True)
    
    def MiniGame(self):
        self.clear_frame()
        self.tab_swicth('minigame')
        self.minigame = TreeDefenderGame(self.application_frm)
        self.minigame.pack(fill="both", expand=True)

    def settings(self):
        self.clear_frame()
        
    
        def toggle_fullscreen():
            self.attributes("-fullscreen", not self.attributes("-fullscreen"))

        
        self.settings_panel = CTkFrame(self.application_frm, fg_color="#3a3a3a")
        self.settings_panel.pack(side="bottom", fill="both", expand=True)
        
        fullscreen_btn = CTkButton(self.settings_panel,text="Toggle Fullscreen",image=self.images['full_screen'],command=toggle_fullscreen)
        fullscreen_btn.grid(row=1, column=0)

        fullscreen_info = CTkLabel(self.settings_panel,text="allows you to go full screen")
        fullscreen_info.grid(row=1, column=1)