# func.py
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from db import add_student, delete, view
from face import capture
import os

class RegistrationAttendance:
    def __init__(self, app):
        self.app = app

    def registration_form(self):
        '''
        Registration form with fields for fname, lname, email and roll_no
        '''
        self.app.clear_window()
        self.app.registration_frame = tk.Frame(self.app.master)
        self.app.registration_frame.pack(expand=True)

        labels = ["First Name", "Last Name", "Email", "Roll Number"]
        entries = {}
        label_font = ("Arial", 12, "bold")
        entry_font = ("Arial", 12)

        for i, text in enumerate(labels):
            label = tk.Label(self.app.registration_frame, text=text, font=label_font)
            entry = tk.Entry(self.app.registration_frame, font=entry_font)
            label.grid(row=i, column=0, padx=10, pady=10, sticky="e")
            entry.grid(row=i, column=1, padx=10, pady=10)
            entries[text] = entry

        register_button_img = ImageTk.PhotoImage(Image.open("src/buttons/register.png").resize((180, 45)))
        register_button = tk.Button(self.app.registration_frame, image=register_button_img, command=lambda: self.submit_registration_form(entries), borderwidth=0)
        register_button.grid(row=len(labels), column=0, columnspan=2, pady=20)
        self.app.master.register_button_img = register_button_img

    def submit_registration_form(self, entries):
        '''
        1. Triggers the capture function from face.py
        2. Adds student to the database with add_student from db.py
        '''
        fname = entries["First Name"].get()
        lname = entries["Last Name"].get()
        email = entries["Email"].get()
        roll_no = entries["Roll Number"].get()

        if not all([fname, lname, email, roll_no]):
            messagebox.showerror("Error", "All fields are required")
            return
        
        try:
            roll_no = int(roll_no)
        except ValueError:
            messagebox.showerror("Error", "Roll Number must be an integer")
            return      
        
        if add_student(roll_no, fname, lname, email):
            capture(fname, lname, roll_no, self.app.cap)
            messagebox.showinfo("Success", "Registration successful")
            self.app.resume_webcam_feed()
            self.app.registration_frame.destroy()
        else:
            messagebox.showerror("Error", "Failed to add student to the database")

    def attendance_script(self): 
        if hasattr(self.app, 'detected_roll_no') and self.app.detected_roll_no:
            self.app.clear_window()
            attendance_info = view(self.app.detected_roll_no)

            attendance_records, (fname, lname, present_percentage) = attendance_info
            self.app.master.title(f"{fname} {lname}'s Presence: {present_percentage}%")

            self.app.tree_frame = tk.Frame(self.app.master)
            self.app.tree_frame.pack(pady=10, expand=True, fill=tk.BOTH)

            columns = ('date', 'presence')
            self.app.tree = ttk.Treeview(self.app.tree_frame, columns=columns, show='headings')
            self.app.tree.heading('date', text='Date')
            self.app.tree.heading('presence', text='Presence')
            self.app.tree.column('date', width=120, anchor=tk.CENTER)
            self.app.tree.column('presence', width=120, anchor=tk.CENTER)

            for record in attendance_records:
                self.app.tree.insert('', 'end', values=record)

            scrollbar = ttk.Scrollbar(self.app.tree_frame, orient='vertical', command=self.app.tree.yview)
            self.app.tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side='right', fill='y')
            self.app.tree.pack(expand=True, fill='both')

            self.app.return_button_img = ImageTk.PhotoImage(Image.open("src/buttons/return.png").resize((160, 40)))
            self.app.return_to_webcam_button = tk.Button(self.app.master, image=self.app.return_button_img, command=self.app.resume_webcam_feed, borderwidth=0)
            self.app.return_to_webcam_button.pack(side=tk.LEFT, padx=10, pady=10)

            self.app.delete_button_img = ImageTk.PhotoImage(Image.open("src/buttons/delete.png").resize((160, 40)))
            self.app.delete_button = tk.Button(self.app.master, image=self.app.delete_button_img, command=lambda: self.delete_student(fname, lname, self.app.detected_roll_no), borderwidth=0)
            self.app.delete_button.pack(side=tk.LEFT, padx=10, pady=10)

    def delete_student(self, fname, lname, roll_no):
        '''
        Deletes student records from the database (using delete from db.py) and datasets folder
        '''
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {fname} {lname} and all their records?"):
            delete(roll_no)

            # Remove all files in the directory
            directory = os.path.join('src', 'datasets', f"{fname}_{lname}_{roll_no}")          
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                os.remove(file_path)  # Remove the file        
            os.rmdir(directory)
            self.app.resume_webcam_feed()
            messagebox.showinfo("Deleted", "Records and images have been deleted.")