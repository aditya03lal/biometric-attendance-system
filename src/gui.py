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
            attendance_records = view(self.detected_roll_no)
            self.display_attendance_records(attendance_records)
        else:
            print("No student selected or detected")
   

    def display_attendance_records(self, attendance_info):
        attendance_records, name_percentage = attendance_info
        fname, lname, present_percentage = name_percentage

        # Create a new pop-up window for displaying attendance records
        records_window = tk.Toplevel(self.master)
        records_window_title = f"{fname}'s Record - Present Percentage: {present_percentage}%"
        records_window.title(records_window_title)
        records_window.geometry("300x300")  # Adjust size as needed

        # Define Treeview with columns
        columns = ('date', 'presence')
        tree = ttk.Treeview(records_window, columns=columns, show='headings')
        
        # Define headings
        tree.heading('date', text='Date')
        tree.heading('presence', text='Presence')
        
        # Format columns
        tree.column('date', width=120, anchor=tk.CENTER)
        tree.column('presence', width=120, anchor=tk.CENTER)

        # Insert data into the treeview
        for record in attendance_records:
            date, presence = record
            presence_str = "Present" if presence == 'y' else "Absent"
            tree.insert('', tk.END, values=(date, presence_str))

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(records_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def run_registration_script(self):
        # This method will be triggered when the "Registration" button is clicked
        run_registration_form(self.cap)
