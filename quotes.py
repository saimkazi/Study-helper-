import customtkinter as ctk
import json
import random
from datetime import datetime

# Load quotes and tips
def load_quotes():
    with open("quotes.json", "r") as file:
        data = json.load(file)
    return data["quotes"], data["tips"]

# Select a quote or tip for the day
def daily_msg():
    tdy = datetime.today().strftime("%Y-%m-%d")
    
    try:
        with open("last_message.json", "r") as file:
            last_data = json.load(file)
            if last_data["date"] == tdy:
                return last_data["message"]
    except FileNotFoundError:
        pass

    # Pick a new quote or tip
    quotes, tips = load_quotes()
    message = random.choice(quotes + tips)

    # Save the message to keep it for the day
    with open("last_message.json", "w") as file:
        json.dump({"date": tdy, "message": message}, file)

    return message

# CustomTkinter UI
class MotivationQuote(ctk.CTkFrame):
    def __init__(self,parent,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)


        self.labl = ctk.CTkLabel(self, text="📢 Today's Motivation", font=("Arial", 20))
        self.labl.pack(pady=20)

        self.msg = daily_msg()
        self.quote_label = ctk.CTkLabel(self, text=self.msg, wraplength=400, font=("Arial", 16))
        self.quote_label.pack(pady=20)

    def refresh_message(self):
        self.msg = daily_msg()
        self.quote_label.configure(text=self.msg)


