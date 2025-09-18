import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import json
import webbrowser

class ResourceLibrary(ctk.CTkFrame):
    def __init__(self,parent,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        
        self.resources = {}
        self.resources_loader()
        
        self.GUI()
    
    def resources_loader(self):
        try:
            with open("resources.json", "r") as file:
                self.resources = json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Error", "The file 'resources.json' was not found.")
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Error decoding 'resources.json'. Please check the file format.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load resources: {e}")
    
    def GUI(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        ctk.CTkLabel(main_frame, text="Enter Subject:").pack(pady=5)
        
        self.subject_entry = ctk.CTkEntry(main_frame)
        self.subject_entry.pack(pady=5)
        
        self.search_button = ctk.CTkButton(main_frame,fg_color="#7f5af0", text="Search", command=self.get_resource)
        self.search_button.pack(pady=5)
        
        self.resource_frame = ctk.CTkScrollableFrame(main_frame)
        self.resource_frame.pack(pady=10, fill=tk.BOTH, expand=True)
    
    def get_resource(self):
        for widget in self.resource_frame.winfo_children():
            widget.destroy()
        
        input_subject = self.subject_entry.get().strip().lower()
        if not input_subject:
            messagebox.showinfo("Input Required", "Please enter a subject to search.")
            return
        
        matched_subject = self.binary_search_match(input_subject)
        
        if not matched_subject:
            messagebox.showinfo("Not Found", "No matching subject found.")
            return
        
        resources = self.resources.get(matched_subject, [])
        if not resources:
            messagebox.showinfo("No Resources", "No resources available for this subject.")
            return
        
        for resource in resources:
            frame = ctk.CTkFrame(self.resource_frame, corner_radius=5, border_width=1)
            frame.pack(pady=5, fill=tk.X)
            
            title = ctk.CTkLabel(frame, text=resource["title"], font=("Arial", 12, "bold"))
            title.pack(anchor="w", padx=5, pady=2)
            
            description = ctk.CTkLabel(frame, text=resource["description"], wraplength=550)
            description.pack(anchor="w", padx=5, pady=2)
            
            link = ctk.CTkButton(frame, text="View Resource", command=lambda url=resource["link"]: webbrowser.open(url))
            link.pack(anchor="w", padx=5, pady=5)
    
    # binary search to get the reource 
    def binary_search_match(self, subject):
        subjects = sorted(self.resources.keys(), key=lambda s: s.lower())
        low, high = 0, len(subjects) - 1
        
        while low <= high:
            mid = (low + high) // 2
            mid_subject = subjects[mid]
            mid_subject_lower = mid_subject.lower()
            
            if mid_subject_lower == subject:
                return mid_subject
            elif mid_subject_lower < subject:
                low = mid + 1
            else:
                high = mid - 1
        
        return None

if __name__ == "__main__":
    app = ResourceLibrary()
    app.mainloop()