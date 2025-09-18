import customtkinter as ctk
from PIL import Image, ImageTk

def pomodoro_timer(main_app):
    # Set appearance mode and color theme
    ctk.set_appearance_mode("dark")
     
    
    # Get screen dimensions 
    screen_width = main_app.winfo_screenwidth()
    screen_height = main_app.winfo_screenheight()
    
    # Container frame
    container = ctk.CTkFrame(main_app, fg_color="#16161A")
    container.pack(fill="both", expand=True)
    
    
    global seconds, running, time
    seconds = 0  
    running = False
    time = seconds  
    
    # Header section with title
    header_frm = ctk.CTkFrame(container, fg_color="transparent")
    header_frm.pack(fill="x", padx=20, pady=(20, 10))
    
    title_labl = ctk.CTkLabel(header_frm, text="Pomodoro Timer", font=("Arial", 24, "bold"),text_color="#FFFFFE" )
    title_labl.pack(side="left")
    
    # Main content
    content_frm = ctk.CTkFrame(container, fg_color="transparent")
    content_frm.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Left side - Timer card 
    timer_card = ctk.CTkFrame(content_frm, fg_color="#242629" , corner_radius=15)
    timer_card.pack(fill="both", expand=True, pady=10)
    
   
    inner_frm = ctk.CTkFrame(timer_card, fg_color="transparent")
    inner_frm.pack(fill="both", expand=True, padx=20, pady=20)
    inner_frm.grid_columnconfigure(0, weight=3)  # Left side (controls)
    inner_frm.grid_columnconfigure(1, weight=2)  # Right side (timer)
    
    # Left side  controls and session 
    controls_side = ctk.CTkFrame(inner_frm, fg_color="transparent")
    controls_side.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    
    # right side timer 
    timer_side = ctk.CTkFrame(inner_frm, fg_color="transparent")
    timer_side.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
    
    # Session type 
    session_frm = ctk.CTkFrame(controls_side, fg_color="transparent")
    session_frm.pack(anchor="center", pady=(20, 30))
    
    session_type = ctk.CTkLabel(session_frm, text="Focus Session", font=("Arial", 18, "bold"),text_color="#7F5AF0")
    session_type.pack()
    
    # Progress bar
    progress_frm = ctk.CTkFrame(controls_side, fg_color="transparent")
    progress_frm.pack(fill="x", pady=(0, 30))
    
    progress_bg = ctk.CTkProgressBar(progress_frm, width=300,height=12,corner_radius=6,fg_color="#333333",progress_color="#7F5AF0")
    progress_bg.pack()
    progress_bg.set(0)  # Start empty
    
    # Timer label - 
    timer_labl = ctk.CTkLabel(timer_side, text="00:00", font=("Arial", 120, "bold"),text_color="#FFFFFE" )
    timer_labl.place(relx=0.5, rely=0.5, anchor="center")
    
    # Timer selection controls - on left side
    select_timer = ctk.CTkFrame(controls_side, fg_color="transparent")
    select_timer.pack(fill="x", pady=(0, 20))
    
    
    button_frm = ctk.CTkFrame(controls_side, fg_color="transparent")
    button_frm.pack(pady=30)
    
    # Define all functions first to avoid scope issues
    def timer_25_min():
        global seconds, time
        seconds = 25 * 60
        time = seconds
        timer_labl.configure(text="25:00")  # Update the label
        session_type.configure(text="Focus Session", text_color="#7F5AF0")
        progress_bg.configure(progress_color="#7F5AF0")
        progress_bg.set(0)

    def timer_5_min():
        global seconds, time
        seconds = 5 * 60
        time = seconds
        timer_labl.configure(text="05:00")  # Update the label
        session_type.configure(text="Break Session", text_color="#2CB67D")
        progress_bg.configure(progress_color="#2CB67D")
        progress_bg.set(0)
    
    def countdown(remaining_seconds):
        global running, time
        time = remaining_seconds  # Keep track of remaining time

        if running:
            mins, secs = divmod(remaining_seconds, 60)
            timer = f'{mins:02}:{secs:02}'
            timer_labl.configure(text=timer)
            
            # Update progress bar
            if seconds > 0:  # Prevent division by zero
                progress = 1.0 - (remaining_seconds / seconds)
                progress_bg.set(progress)
            
            if remaining_seconds > 0:
                container.after(1000, countdown, remaining_seconds - 1)
            else:
                # Timer completed
                timer_labl.configure(text="Time's up!")
                running = False
                
                # Show completion notification
                show_completion()
                
                # Reset buttons to start
                reset_timer()
    
    def timer_controller():
        # Clear existing buttons if they exist
        for widget in button_frm.winfo_children():
            widget.destroy()
        
        # Pause button
        pause_btn = ctk.CTkButton(button_frm,text="Pause",font=("Arial", 16, "bold"),fg_color="#555555",text_color="white",hover_color="#444444",corner_radius=8,width=100,height=45,command=pause_timer)
        pause_btn.pack(side="left", padx=5)
        
        # Reset button
        reset_btn = ctk.CTkButton(button_frm,text="Reset",font=("Arial", 16, "bold"),fg_color="#E45858",text_color="white",hover_color="#C0392B",corner_radius=8,width=100,height=45,command=reset_timer)
        reset_btn.pack(side="left", padx=5)
        
        # Make pause button accessible to other functions
        return pause_btn
    
    def pause_timer():
        global running
        running = False
        
        # Replace with unpause button
        for widget in button_frm.winfo_children():
            widget.destroy()
        
        # Unpause button
        unpause_button = ctk.CTkButton(button_frm,text="Resume",font=("Arial", 16, "bold"),fg_color="#7F5AF0",text_color="white",hover_color="#6344D0",corner_radius=8,width=100,height=45,command=unpause_timer)
        unpause_button.pack(side="left", padx=5)
        
        # Reset button
        reset_button = ctk.CTkButton(button_frm,text="Reset",font=("Arial", 16, "bold"),fg_color="#E45858",text_color="white",hover_color="#C0392B",corner_radius=8,width=100,height=45,command=reset_timer)
        reset_button.pack(side="left", padx=5)
    
    def unpause_timer():
        global running
        running = True
        timer_controller()  # Restore normal buttons
        countdown(time)  # Resume from where left off
    
    def reset_timer():
        global running, seconds, time
        running = False
        
        # Reset  display
        mins, secs = divmod(seconds, 60)
        timer_labl.configure(text=f"{mins:02}:{secs:02}")
        progress_bg.set(0)
        
        # Reset timer 
        time = seconds
        
        # Restore start btn
        for widget in button_frm.winfo_children():
            widget.destroy()
        
        # Start button
        start_btn = ctk.CTkButton(button_frm,text="Start",font=("Arial", 16, "bold"),fg_color="#7F5AF0",text_color="white",hover_color="#6344D0",corner_radius=8,width=100,height=45,command=start_timer)
        start_btn.pack(side="left", padx=5)
    
    def show_completion():
        # Create notification popup
        notify_frm = ctk.CTkFrame(container, fg_color="#242629" ,corner_radius=15)
        notify_frm.place(relx=0.5, rely=0.5, anchor="center", width=400, height=250)
        
        # Emoji for completion
        emoji_labl = ctk.CTkLabel(notify_frm,text="🎉",font=("Arial", 40))
        emoji_labl.pack(pady=(20, 0))
        
        # Completion message
        complete_label = ctk.CTkLabel(notify_frm,text="Time's Up!",font=("Arial", 22, "bold"),text_color="#FFFFFE" )
        complete_label.pack(pady=(10, 5))
        
        # Subtext
        if session_type.cget("text") == "Focus Session":
            msg = "Great job! Take a break before your next focus session."
            next_session = "Break"
            next_color = "#2CB67D"
            next_command = timer_5_min
        else:
            msg = "Break time is over. Ready to get back to work?"
            next_session = "Focus"
            next_color = "#7F5AF0"
            next_command = timer_25_min
        
        message_label = ctk.CTkLabel(notify_frm,text=msg,font=("Arial", 14),text_color="#94A1B2" ,wraplength=350)
        message_label.pack(pady=(0, 20))
        
        # Next session button
        next_button = ctk.CTkButton(notify_frm,text=f"Start {next_session} Session",font=("Arial", 14),fg_color=next_color,text_color="white",hover_color="#6344D0" if next_session == "Focus" else "#247A58",corner_radius=8,width=200,height=40,command=lambda: [next_command(), notify_frm.destroy(), start_timer()])
        next_button.pack(pady=5)
        
        # Close button
        close_button = ctk.CTkButton(notify_frm,text="Close",font=("Arial", 14),fg_color="transparent",text_color="#FFFFFE" ,hover_color="#16161A",corner_radius=8,border_width=1,border_color="#94A1B2" ,width=200,height=40,command=notify_frm.destroy)
        close_button.pack(pady=5)
    
    # Function to start the timer - adapted from original code
    def start_timer():
        global running, time, seconds
        if seconds > 0:  # Ensure a time has been selected
            pause_button = timer_controller()
            if not running:
                running = True
                time = seconds  # Start from the selected time
                countdown(time)
        else:
            # Show notification to select time
            notify_frm = ctk.CTkFrame(container, fg_color="#242629" ,corner_radius=15)
            notify_frm.place(relx=0.5, rely=0.5, anchor="center", width=400, height=200)
            
            notify_labl = ctk.CTkLabel(notify_frm,text="Please select a time first",font=("Arial", 18, "bold"),text_color="#FFFFFE" )
            notify_labl.pack(pady=(40, 20))
            
            close_btn = ctk.CTkButton(notify_frm,text="Close",font=("Arial", 14),fg_color="#7F5AF0",text_color="white",hover_color="#6344D0",corner_radius=8,width=120,height=40,command=notify_frm.destroy)
            close_btn.pack(pady=10)
    
    # Focus Duration
    focus_labl = ctk.CTkLabel(select_timer, text="Focus Duration", font=("Arial", 14),text_color="#94A1B2" )
    focus_labl.pack(pady=(0, 5))
    
    focus_btn = ctk.CTkButton(select_timer,text="25 min",font=("Arial", 12),fg_color="#7F5AF0",text_color="white",hover_color="#6344D0",corner_radius=8,width=120,height=30,command=timer_25_min)
    focus_btn.pack(pady=(0, 15))
    
    # Break Duration
    break_label = ctk.CTkLabel(select_timer, text="Break Duration", font=("Arial", 14),text_color="#94A1B2" )
    break_label.pack(pady=(0, 5))
    
    break_btn = ctk.CTkButton(select_timer,text="5 min",font=("Arial", 12),fg_color="#2CB67D",text_color="white",hover_color="#247A58",corner_radius=8,width=120,height=30,command=timer_5_min)
    break_btn.pack()
    
    # Start button
    start_button = ctk.CTkButton(button_frm,text="Start",font=("Arial", 16, "bold"),fg_color="#7F5AF0",text_color="white",hover_color="#6344D0",corner_radius=8,width=100,height=45,command=start_timer)
    start_button.pack(side="left", padx=5)