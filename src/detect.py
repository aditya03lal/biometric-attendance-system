#detect.py
import cv2
import face_recognition
from database import update_presence
import os

def load_known_faces(datasets_folder):
    known_face_encodings = []
    known_face_names = []
    for person_folder in os.listdir(datasets_folder):
        person_folder_path = os.path.join(datasets_folder, person_folder)
        if os.path.isdir(person_folder_path):
            for filename in os.listdir(person_folder_path):
                img_path = os.path.join(person_folder_path, filename)
                image = face_recognition.load_image_file(img_path)
                encoding = face_recognition.face_encodings(image)
                if encoding:
                    known_face_encodings.append(encoding[0])
                    # Use the folder name directly as the known name
                    known_face_names.append(person_folder)
    return known_face_encodings, known_face_names


def process_frame(frame, known_face_encodings, known_face_names):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, )

    detected_roll_no = None  # Initialize detected_roll_no at the start

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, 0.3)

        if True in matches:
            first_match_index = matches.index(True)
            matched_name = known_face_names[first_match_index]

            name_parts = matched_name.split('_')
            fname, lname, roll_no = name_parts
            detected_roll_no = roll_no  # Update detected_roll_no when a match is found

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, f"upper({fname} {lname}) Present", (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

            update_presence(fname, lname, roll_no)
        
        else:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, "Unknown", (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

    return frame, detected_roll_no