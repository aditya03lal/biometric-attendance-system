# register.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from database import add_student
import cv2
import os

def run_registration_form(cap):
    root = tk.Toplevel()
    RegistrationForm(root, cap)
    root.mainloop()

def capture(first_name, last_name, roll_no, cap):
    datasets_dir = "src/datasets"
    person_folder = f"{first_name}_{last_name}_{roll_no}"
    person_path = os.path.join(datasets_dir, person_folder)

    os.makedirs(person_path, exist_ok=True)

    image_count = 0
    while image_count < 10:
        ret, frame = cap.read()
        if ret:
            image_count += 1
            image_path = os.path.join(person_path, f"image{image_count}.jpg")
            cv2.imwrite(image_path, frame)
            print(f"Captured image {image_count}/10 for {first_name} {last_name}")
        #cv2.imshow('Capturing Images', frame)
        #cv2.waitKey(1)

    #cv2.destroyAllWindows()

class RegistrationForm:
    def __init__(self, master, cap):
        self.master = master
        self.cap = cap
        self.setup_ui()

    def setup_ui(self):
        self.master.title("Registration Form")
        self.master.geometry("300x200")
        
        self.create_widgets()

    def create_widgets(self):
        labels = ["First Name", "Last Name", "Email", "Roll Number"]
        self.entries = {}
        for i, text in enumerate(labels):
            tk.Label(self.master, text=text).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            self.entries[text] = tk.Entry(self.master)
            self.entries[text].grid(row=i, column=1, padx=10, pady=5)

        self.registration_button_img = ImageTk.PhotoImage(Image.open("src/buttons/register.png").resize((160, 40)))
        tk.Button(self.master, image=self.registration_button_img, command=self.submit_form, borderwidth=0).place(relx=0.5, rely=0.78, anchor="center")

    def submit_form(self):
        fname = self.entries["First Name"].get()
        lname = self.entries["Last Name"].get()
        email = self.entries["Email"].get()
        roll_no = self.entries["Roll Number"].get()

        if not all([fname, lname, email, roll_no]):
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            roll_no = int(roll_no)
        except ValueError:
            messagebox.showerror("Error", "Roll Number must be an integer")
            return

        # Add student to the database
        if add_student(roll_no, fname, lname, email):
            # Proceed to capture images for the student
            capture(fname, lname, roll_no, self.cap)
            messagebox.showinfo("Success", "Registration successful")
            self.master.destroy()
        else:
            messagebox.showerror("Error", "Failed to add student to the database")