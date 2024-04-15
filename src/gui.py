# gui.py
import cv2
import tkinter as tk
from PIL import Image, ImageTk
from func import RegistrationAttendance

class App:
    def __init__(self, master):
        self.master = master
        self.stop_webcam_update = False
        self.ra = RegistrationAttendance(self)  # Proper class name for better clarity
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
        '''
        Setups the two buttons for Viewing Attendance and Registration
        '''
        self.attendance_button_img = ImageTk.PhotoImage(Image.open("src/buttons/attendance.png").resize((240, 60)))
        self.attendance_button = tk.Button(self.master, image=self.attendance_button_img, command=self.ra.attendance_script, borderwidth=0)
        self.attendance_button.pack(pady=10)

        self.registration_button_img = ImageTk.PhotoImage(Image.open("src/buttons/registration.png").resize((240, 60)))
        self.registration_button = tk.Button(self.master, image=self.registration_button_img, command=self.ra.registration_form, borderwidth=0)
        self.registration_button.pack(pady=10)

    def initialize_webcam(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Failed to access webcam")
            self.master.destroy()

    def load_faces(self):
        from face import load_known_faces  # Assuming face.py handles face recognition
        self.known_face_encodings, self.known_face_names = load_known_faces("src/datasets")

    def update_webcam(self):
        from face import process_frame
        if self.stop_webcam_update:
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
        '''
        Sets the frame's aspect ratio to fit in the main window
        '''
        height, width, _ = frame.shape
        new_height = 375
        new_width = int((width / height) * new_height)
        return cv2.resize(frame, (new_width, new_height))

    def clear_window(self):
        self.webcam_label.pack_forget()
        self.attendance_button.pack_forget()
        self.registration_button.pack_forget()
        self.stop_webcam_update = True
        
    def resume_webcam_feed(self):
        '''
        Restores the main window's webcam feed and associated buttons after viewing/deleting records or registration
        '''
        self.master.title("EBAS")
        
        # Destroy potential widgets that are specific to views other than the main webcam feed
        for attr in ['tree_frame', 'return_to_webcam_button', 'delete_button']:
            widget = getattr(self, attr, None)
            if widget is not None:
                widget.destroy()
                delattr(self, attr)

        # Ensure webcam label is visible
        if self.webcam_label.winfo_manager() == '':
            self.webcam_label.pack(pady=10)

        # Repack the buttons if they are not currently managed
        for button in [self.attendance_button, self.registration_button]:
            if button.winfo_manager() == '':
                button.pack(pady=10)

        # Reload known faces in case of new registration or deletion
        self.load_faces()
        self.stop_webcam_update = False
        self.update_webcam()