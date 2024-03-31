#database.py
import mysql.connector
from tkinter import messagebox
import datetime
from datetime import date, timedelta

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
    today = datetime.date.today()
    
    # Ensure the student exists in the database.
    cursor.execute("SELECT roll_no FROM student WHERE fname = %s AND lname = %s AND roll_no = %s", (fname, lname, roll_no))
    if not cursor.fetchone():
        print("Student not found in the database.")
        return
    
    # Check for the last date recorded to find any missing dates.
    cursor.execute("SELECT MAX(date) FROM record_student WHERE roll_no = %s", (roll_no,))
    last_date_record = cursor.fetchone()[0]
    
    # If there is a last recorded date and it's before today, fill the gap.
    if last_date_record and last_date_record < today:
        missing_dates = [last_date_record + timedelta(days=x) for x in range(1, (today - last_date_record).days)]
        for missing_date in missing_dates:
            cursor.execute("INSERT INTO record_student (roll_no, date, presence) VALUES (%s, %s, 'n')", (roll_no, missing_date))
    
    # Insert today's record with presence "y" or update if already exists.
    cursor.execute("SELECT presence FROM record_student WHERE roll_no = %s AND date = %s", (roll_no, today))
    if cursor.fetchone():
        cursor.execute("UPDATE record_student SET presence = 'y' WHERE roll_no = %s AND date = %s", (roll_no, today))
    else:
        cursor.execute("INSERT INTO record_student (roll_no, date, presence) VALUES (%s, %s, 'y')", (roll_no, today))
        messagebox.showinfo("Presence detected", f"{fname} {lname}'s presence was successfully recorded")

    # Update present percentage.
    cursor.execute("SELECT COUNT(*) FROM record_student WHERE roll_no = %s AND presence = 'y'", (roll_no,))
    days_present = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM record_student WHERE roll_no = %s", (roll_no,))
    total_days = cursor.fetchone()[0]
    if total_days > 0:
        new_percentage = round((days_present / total_days) * 100, 1)  # Rounded to one decimal place.
        cursor.execute("UPDATE student SET present_percentage = %s WHERE roll_no = %s", (new_percentage, roll_no))


@connect
def view(cursor, roll_no):
    # Query to retrieve attendance records.
    cursor.execute("SELECT date, presence FROM record_student WHERE roll_no = %s", (roll_no,))
    records = cursor.fetchall()

    # Query to retrieve student's first name, last name, and present percentage.
    cursor.execute("SELECT fname, lname, present_percentage FROM student WHERE roll_no = %s", (roll_no,))
    name_percentage = cursor.fetchone()  # Expecting a tuple like ('John', 'Doe', 75.0)

    return records, name_percentage