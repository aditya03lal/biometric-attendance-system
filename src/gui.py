#gui.py
import tkinter as tk
from PIL import Image, ImageTk
import cv2
from detect import process_frame, load_known_faces
from register import run_registration_form
from database import view  # Assuming this function is properly defined
from tkinter import ttk

class App:
    def __init__(self, master):
        self.master = master
        self.stop_webcam_update = False  # Initialize the attribute here
        self.setup_ui()

    def setup_ui(self):
        self.master.title("EBAS")
        self.master.geometry("375x575")
        self.master.resizable(False, False)
        
        self.webcam_label = tk.Label(self.master)
        self.webcam_label.pack(pady=10)
        
        self.setup_buttons()
        self.initialize_webcam()
        self.load_faces()
        self.update_webcam()

    def setup_buttons(self):
        self.attendance_button_img = ImageTk.PhotoImage(Image.open("src/buttons/attendance.png").resize((240, 60)))
        self.attendance_button = tk.Button(self.master, image=self.attendance_button_img, command=self.run_attendance_script, borderwidth=0)
        self.attendance_button.pack(pady=10)
        
        self.registration_button_img = ImageTk.PhotoImage(Image.open("src/buttons/registration.png").resize((240, 60)))
        self.registration_button = tk.Button(self.master, image=self.registration_button_img, command=lambda: run_registration_form(self.cap), borderwidth=0)
        self.registration_button.pack(pady=10)

    def initialize_webcam(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Failed to access webcam")
            self.master.destroy()

    def load_faces(self):
        self.known_face_encodings, self.known_face_names = load_known_faces("src/datasets")

    def update_webcam(self):
        if self.stop_webcam_update:
            # Skip updating the webcam feed if stopped
            return

        ret, frame = self.cap.read()
        if ret:
            frame, detected_roll_no = process_frame(frame, self.known_face_encodings, self.known_face_names)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = self.resize_frame(frame)
            webcam_img = ImageTk.PhotoImage(Image.fromarray(frame))
            self.webcam_label.config(image=webcam_img)
            self.webcam_label.image = webcam_img
            self.master.after(30, self.update_webcam)
            if detected_roll_no is not None:
                self.detected_roll_no = detected_roll_no
 
    def resize_frame(self, frame):
        height, width, _ = frame.shape
        new_height = 375
        new_width = int((width / height) * new_height)
        return cv2.resize(frame, (new_width, new_height))

    def run_attendance_script(self):
        if hasattr(self, 'detected_roll_no') and self.detected_roll_no:
            # Hide buttons
            self.attendance_button.pack_forget()
            self.registration_button.pack_forget()

            attendance_info = view(self.detected_roll_no)  # Assuming view returns (attendance_records, (fname, lname, present_percentage))
            self.display_attendance_records(attendance_info)
        else:
            print("No student selected or detected")
   
    def display_attendance_records(self, attendance_info):
        # Stop the webcam feed update
        self.stop_webcam_update = True

        # Clear the existing content in webcam_label
        self.webcam_label.pack_forget()

        attendance_records, name_percentage = attendance_info
        fname, lname, present_percentage = name_percentage

        # Change the main window title to show present percentage
        self.master.title(f"{fname} {lname}'s Record - Present Percentage: {present_percentage}%")

        # Use the existing webcam_label space for Treeview
        self.tree_frame = tk.Frame(self.master)
        self.tree_frame.pack(pady=10, expand=True, fill=tk.BOTH)

        columns = ('date', 'presence')
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings')
        
        self.tree.heading('date', text='Date')
        self.tree.heading('presence', text='Presence')
        
        self.tree.column('date', width=120, anchor=tk.CENTER)
        self.tree.column('presence', width=120, anchor=tk.CENTER)

        for record in attendance_records:
            date, presence = record
            presence_str = "Present" if presence == 'y' else "Absent"
            self.tree.insert('', tk.END, values=(date, presence_str))

        scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        self.tree.pack(expand=True, fill=tk.BOTH)

        # Button to return to webcam view
        self.return_button_img = ImageTk.PhotoImage(Image.open("src/buttons/return.png").resize((240, 60)))
        self.return_to_webcam_button = tk.Button(self.master, image=self.return_button_img, command=self.resume_webcam_feed, borderwidth=0)
        self.return_to_webcam_button.pack(pady=10)

    def resume_webcam_feed(self):
        # Clear the attendance records and restore the main window title
        self.master.title("EBAS")
        self.tree_frame.pack_forget()
        self.return_to_webcam_button.pack_forget()
        
        # Restore the webcam feed and buttons
        self.webcam_label.pack(pady=10)
        self.attendance_button.pack(pady=10)
        self.registration_button.pack(pady=10)

        self.stop_webcam_update = False
        self.update_webcam()

    def run_registration_script(self):
        # This method will be triggered when the "Registration" button is clicked
        run_registration_form(self.cap)
