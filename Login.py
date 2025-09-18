from customtkinter import *
import customtkinter as ctk
from PIL import Image, ImageTk
import pymysql
from server import *


# Main login window creator
def login_page():
    app = ctk.CTk()
    app.title("ECLIPSE LEARNING")

    # Set window  
    app.geometry("1000x600")
    app.minsize(1000, 600)
    

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Load the background
    image = Image.open("Pics/wave.png")
    background_image = CTkImage(dark_image=image, light_image=image, size=(500, 600))  

    #image = CTkLabel(left_panel, text="", image=background_image) #  keep this just in case
    #image.place(relx=0.5, rely=0.5, anchor="center")
    
    # Setup the main frame - this holds everything
    main_frm = CTkFrame(app, fg_color="#16161A")
    main_frm.pack(fill="both", expand=True)

    # Left side for the bg image
    left_frm = CTkFrame(main_frm, fg_color="#16161A", width=500)
    left_frm.pack(side="left", fill="both", expand=True)

    # Right panel - this is where login stuff goes
    right_panel = CTkFrame(main_frm, fg_color="#16161A", width=500)
    right_panel.pack(side="right", fill="both")

    # Container for login form
    login_frame = CTkFrame(right_panel, fg_color="transparent", width=400)
    login_frame.place(relx=0.5, rely=0.5, anchor="center")

    image = CTkLabel(left_frm, text="", image=background_image)
    image.place(relx=0.5, rely=0.5, anchor="center")
    

    # Sign up window function
    def sign_up_page():
        # Handle the signup button click
        def signup_handler():
            # Grab the data from form
            username_signup = username_inpt.get().strip()
            print(username_signup)  # debug

            password_signup = password_entry_box.get()
            print(password_signup)  # debug

            confirm_password_signup = confirm_password_entry.get()
            print(confirm_password_signup)  # debug
            
            # List to store validation errors
            errors = []
            
            # Super basic validation
            if not username_signup:
                errors.append("Username cannot be empty")
                print("Username cannot be empty")
            elif len(username_signup) < 4:
                errors.append("Username must be at least 4 characters")
                print("Username must be at least 4 characters")
                
            if not password_signup:
                errors.append("Password cannot be empty")
                print("no password")
            elif len(password_signup) < 4:
                errors.append("Password must be at least 4 characters")
                
            if password_signup != confirm_password_signup:
                errors.append("Passwords do not match")
            
            # Check if username exists in DB
            try:
                query = "SELECT * FROM users WHERE username = %s"
                cursor.execute(query, (username_signup,))
                result = cursor.fetchone()
                if result:
                    errors.append("Username is already taken")
                    print("DB username taken")
            except Exception as e:
                errors.append(f"Database error: {str(e)}")
                print("DB fail")
            
            # Show errors
            if errors:
                error_frame = CTkFrame(signup_frame, fg_color="red",  corner_radius=10)
                error_frame.place(relx=0.5, rely=0.9, anchor="center", relwidth=0.9)
                
                # Make a bullet list of errors
                text_error = "\n".join([f"• {error}" for error in errors])
                error_label = CTkLabel(error_frame, text=text_error, font=("Helvetica", 10), text_color="black", wraplength=300,justify="left")
                error_label.pack(padx=10, pady=10)
                
                # Auto-destroy errors after 5s
                error_frame.after(3000, error_frame.destroy)
                return
            
            # Create the user
            try:
                query = "INSERT INTO users (username, password) VALUES (%s, %s)"
                cursor.execute(query, (username_signup, password_signup))
                db_connection.commit()  # save to db
                print("user created")
                
                # Show success message
                show_message("Success", "Your account has been created successfully!","#2CB67D",  lambda: [signup_frame.destroy(),])
            except Exception as e:
                show_message("Error",f"Failed to create account: {str(e)}","red", ) #  red color for error

        # Helper function for popup messages
        def show_message(title, message, color, on_close):
            message_frame = CTkFrame(signup_frame, fg_color=color,corner_radius=10,border_width=1,border_color=color)
            message_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.4)
            
            title_label = CTkLabel(message_frame, text=title, font=("Helvetica", 16, "bold"), text_color=color)
            title_label.pack(pady=(20, 10))
            
            msg_label = CTkLabel(message_frame, text=message, font=("Helvetica", 12), text_color="#FFFFFE",wraplength=300)
            msg_label.pack(pady=10)
            
            # Close button
            close_button = CTkButton(message_frame, text="Close", font=("Helvetica", 12),fg_color=color,text_color="#FFFFFE",hover_color=color,corner_radius=10,command=lambda: [message_frame.destroy(), on_close() if on_close else None])
            close_button.pack(pady=10)

        #  signup popup frame
        signup_frame = CTkFrame(right_panel, fg_color="#242629",corner_radius=10,border_width=1,border_color="#94A1B2",width=400, height=500)  # make sure the sizing is alr 
        signup_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Header part
        header_frame = CTkFrame(signup_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        header = CTkLabel(header_frame, text="Create an Account", font=("Helvetica", 20, "bold"), text_color="#FFFFFE")
        header.pack(side="left")
        
        close_btn = CTkButton(header_frame, text="✕", font=("Helvetica", 12),fg_color="transparent",text_color="#94A1B2",hover_color="#16161A",width=30,height=30,corner_radius=15,command=signup_frame.destroy)
        close_btn.pack(side="right")
        
      
        container = CTkFrame(signup_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        #  input fields 
        username_label = CTkLabel(container, text="Username", font=("Helvetica", 12), text_color="#FFFFFE",anchor="w")
        username_label.pack(fill="x", pady=5)
        
        username_inpt = CTkEntry(container, font=("Helvetica", 12),fg_color="#16161A",text_color="#FFFFFE",border_color="#94A1B2",corner_radius=10,height=40)
        username_inpt.pack(fill="x", pady=10)
        
        password_label = CTkLabel(container, text="Password", font=("Helvetica", 12), text_color="#FFFFFE",anchor="w")
        password_label.pack(fill="x", pady=5)
        
        password_entry_box = CTkEntry(  container, font=("Helvetica", 12),fg_color="#16161A",text_color="#FFFFFE",border_color="#94A1B2",corner_radius=10,height=40,show="●" ) # hide password
        password_entry_box.pack(fill="x", pady=10)
        
        confirm_password_label = CTkLabel(container, text="Confirm Password", font=("Helvetica", 12), text_color="#FFFFFE",anchor="w")
        confirm_password_label.pack(fill="x", pady=5)
        
        confirm_password_entry = CTkEntry(container, font=("Helvetica", 12),fg_color="#16161A",text_color="#FFFFFE",border_color="#94A1B2",corner_radius=10,height=40,show="●")  # hide password
        confirm_password_entry.pack(fill="x", pady=10)
        
        # Sign Up button 
        signup_button = CTkButton(container, text="Sign Up", font=("Helvetica", 12, "bold"),fg_color="#7F5AF0", text_color="#FFFFFE",hover_color="#7F5AF0", corner_radius=10,height=45,command=signup_handler)
        signup_button.pack(fill="x", pady=10)
        
        # back to login button 
        back_to_login = CTkFrame(container, fg_color="transparent")
        back_to_login.pack(fill="x", pady=10)
        
        login_text = CTkLabel(back_to_login, text="Already have an account?", font=("Helvetica", 10), text_color="#94A1B2")
        login_text.pack(side="left")
        
        back_to_login = CTkButton(back_to_login, text="Log In", font=("Helvetica", 10),fg_color="transparent",text_color="#7F5AF0",hover_color="blue",  hover=False,width=50,height=20,command=lambda: signup_frame.destroy())
        back_to_login.pack(side="left", padx=5)
    
    # Function to show the login form
    def login_page():
        # Handle login button press
        def handler_login():  
            username_inpt = username_entry.get().strip()
            password_inpt = password_entry.get()
            
            # Basic validation
            if not username_inpt or not password_inpt:
                error("Please enter both username and password")
                return
            
            # Check login in DB
            try:
                query = "SELECT user_id, username FROM users WHERE username = %s AND password = %s"
                cursor.execute(query, (username_inpt, password_inpt))
                result = cursor.fetchone()
                
                if result:
                    # Login worked 
                    user_id, username = result
                    
                    # Show success and proceed
                    show_success(f"Welcome back, {username}!", user_id)
                else:
                    # Bad login
                    error("Invalid username or password")
            except Exception as e:
                # DB error
                error(f"Database error: {str(e)}")
        
        # Show error messages
        def error(message):
            error = CTkFrame(login_frame, fg_color="red",corner_radius=10)
            error.place(relx=0.5, rely=0.85, anchor="center", relwidth=0.9)
            
            error_label = CTkLabel(error, text=message, font=("Helvetica", 10), text_color="black")
            error_label.pack(padx=10, pady=10)
            
            # Auto-hide after 5s
            error.after(5000, error.destroy)
        
        # Success login handler
        def show_success(message, user_id):
            # Green success popup
            success_frm = CTkFrame(right_panel, fg_color="#2CB67D",corner_radius=10,border_width=1,border_color="#2CB67D")
            success_frm.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.5)
            
            success_icon = CTkLabel(success_frm, text="✓", font=("Arial", 48, "bold"), text_color="#2CB67D")
            success_icon.pack(pady=20)

            success_msg = CTkLabel(success_frm, text=message, font=("Helvetica", 16, "bold"), text_color="black")
            success_msg.pack(pady=10)
            
            
            loading = CTkLabel(success_frm, text="Preparing your dashboard...", font=("Helvetica", 12), text_color="#94A1B2")
            loading.pack(pady=10)
            
            # Fake loading bar 
            progress_container = CTkFrame(success_frm, fg_color="#16161A", height=10, width=200, corner_radius=5)
            progress_container.pack(pady=10)
            
            progress_bar = CTkFrame(progress_container, fg_color="#2CB67D", height=10, width=0, corner_radius=5)
            progress_bar.place(x=0, y=0)
            
            # Make the progress bar fill up 
            def loading_animation(value=0):
                if value <= 100:
                    width = (value / 100) * 200
                    progress_bar.configure(width=width)
                    # Increase by 2% each time - not perfect but looks ok
                    success_frm.after(30, lambda: loading_animation(value + 2))
                else:
                    # Ready to launch the main app
                    success_frm.after(500, lambda: [app.destroy(), launch_main_app(user_id)])
            
            # Start the progress animation
            success_frm.after(500, lambda: loading_animation())
        
        # Launch the main app
        def launch_main_app(user_id):
            # Import the main app only when needed
            from main import MainApp
            main = MainApp(user_id)
            main.mainloop()
        
        # title 
        login_title = CTkLabel(login_frame, text="Welcome Back", font=("Helvetica", 24, "bold"), text_color="#FFFFFE" )
        login_title.pack(pady=5)
        
        
        login_subtitle = CTkLabel(login_frame, text="Sign in to continue your learning journey", font=("Helvetica", 12), text_color="#94A1B2" )
        login_subtitle.pack(pady=20)

        # app logo 
        branding_frm = CTkFrame(left_frm, fg_color="transparent")
        branding_frm.place(relx=0.5, rely=0.2, anchor="center")
        
        logo_frm = CTkFrame(branding_frm, fg_color="#7F5AF0", width=80, height=80, corner_radius=40)
        logo_frm.pack(pady=20)
        
        logo_txt = CTkLabel(logo_frm, text="Eclipse", font=("Arial", 40, "bold"), text_color="#FFFFFE")
        logo_txt.place(relx=0.5, rely=0.5, anchor="center")
        
            
        # user input fields
        username_labl = CTkLabel(login_frame, text="Username", font=("Helvetica", 12), text_color="#FFFFFE" ,anchor="w")
        username_labl.pack(fill="x", pady=5)
        
        username_entry = CTkEntry(login_frame, font=("Helvetica", 12),fg_color="#16161A" ,text_color="#FFFFFE",border_color="#94A1B2",corner_radius=10,height=45,width=400)
        username_entry.pack(fill="x", pady=10)
        
        
        password_labl = CTkLabel(login_frame, text="Password", font=("Helvetica", 12), text_color="#FFFFFE" ,anchor="w")
        password_labl.pack(fill="x", pady=5)
        
        password_entry = CTkEntry(login_frame, font=("Helvetica", 12),fg_color="#16161A" ,text_color="#FFFFFE" ,border_color="#94A1B2" ,corner_radius=10,height=45,width=400,show="●")  # Hide password with bullet
        password_entry.pack(fill="x", pady=10)
        
        #  buttons
        login_btn = CTkButton(login_frame, text="Log In", font=("Helvetica", 12, "bold"),fg_color="#7F5AF0",text_color="#FFFFFE",hover_color="#7F5AF0", corner_radius=10,height=45,width=400,command=handler_login   )
        login_btn.pack(pady=10)
        
         
        register_frm = CTkFrame(login_frame, fg_color="transparent")
        register_frm.pack(pady=5)
        
        register_txt = CTkLabel(register_frm, text="Don't have an account?", font=("Helvetica", 10), text_color="#94A1B2")
        register_txt.pack(side="left")
        
        
        register_btn = CTkButton(  register_frm, text="Sign Up", font=("Helvetica", 10),fg_color="transparent",text_color="#7F5AF0",hover_color="blue",hover=False,width=60,height=20,command=sign_up_page)
        register_btn.pack(side="left", padx=5)
        
        # Just some info text 
        frm_info = CTkFrame(login_frame, fg_color="#16161A" , corner_radius=10)
        frm_info.pack(fill="x", pady=20)
        
        I_label = CTkLabel(  frm_info, text="Welcome to eclipse ", font=("Helvetica", 10), text_color="#94A1B2")
        I_label.pack(pady=5)
        
        I = CTkLabel( frm_info, text="PLease remember your password", font=("Helvetica", 10), text_color="#94A1B2")
        I.pack()
        
        # might add more info here later if needed 
        I_2 = CTkLabel(frm_info, text="...", font=("Helvetica", 10), text_color="#94A1B2")
        I_2.pack(pady=5)

    # Show login form initially
    login_page()

    # Start the app
    app.mainloop()

if __name__ == "__main__":
    login_page()