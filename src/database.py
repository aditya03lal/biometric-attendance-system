#database.py
import mysql.connector
from tkinter import messagebox
import datetime

config = {
    'user': 'root',
    'password': '1234',
    'host': 'localhost',
    'database': 'attendance',
    'raise_on_warnings': True
}

def connect(func):
    def wrapper(*args, **kwargs):
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        try:
            result = func(cursor, *args, **kwargs)
            connection.commit()
            return result
        finally:
            cursor.close()
            connection.close()
    return wrapper

@connect
def add_student(cursor, roll_no, fname, lname, email):
    query = "INSERT INTO student (roll_no, fname, lname, email_id) VALUES (%s, %s, %s, %s)"
    try:
        cursor.execute(query, (roll_no, fname, lname, email))
        return True  # Return True on successful insertion
    except mysql.connector.IntegrityError as e:
        print(f"IntegrityError: {e}")
        return False  # Return False if IntegrityError occurs

@connect
def update_presence(cursor, fname, lname, roll_no):
    # Step 1: Find the student's roll_no based on fname and lname
    cursor.execute("SELECT roll_no FROM student WHERE fname = %s AND lname = %s AND roll_no = %s" , (fname, lname, roll_no))
    result = cursor.fetchone()
    if result:
        roll_no = result[0]
        today = datetime.date.today()

        # Step 2: Check if an attendance record already exists for today
        cursor.execute("SELECT presence FROM record_student WHERE roll_no = %s AND date = %s", (roll_no, today))
        existing_record = cursor.fetchone()
        if existing_record:
            previous_presence = existing_record[0]
            if previous_presence == 'n':
                # If previous presence was 'n', update it to 'y' and show messagebox
                cursor.execute("UPDATE record_student SET presence = 'y' WHERE roll_no = %s AND date = %s", (roll_no, today))
                messagebox.showinfo("Presence detected", f"{fname} {lname}'s presence was successfully recorded")
        else:
            # If no record exists for today, insert a new record with 'n'
            cursor.execute("INSERT INTO record_student (roll_no, date, presence) VALUES (%s, %s, 'n')", (roll_no, today))

        # Calculate and update the new present_percentage based on updated attendance records
        cursor.execute("SELECT COUNT(*) FROM record_student WHERE roll_no = %s AND presence = 'y'", (roll_no,))
        days_present = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM record_student WHERE roll_no = %s", (roll_no,))
        total_days = cursor.fetchone()[0]
        if total_days > 0:
            new_percentage = (days_present / total_days) * 100
            cursor.execute("UPDATE student SET present_percentage = %s WHERE roll_no = %s", (new_percentage, roll_no))
        
        # messagebox.showinfo("Success", f"{fname} {lname}'s presence was successfully recorded")
    else:
        print("Student not found in database.")


@connect
def view(cursor, roll_no):
    query = "SELECT date, presence FROM record_student WHERE roll_no = %s"
    cursor.execute(query, (roll_no,))
    records = cursor.fetchall()
    for record in records:
        print(record)

    return records