# db.py
import mysql.connector
import datetime
from datetime import timedelta
from config import cfg  

config = cfg

def connect(func):
    """
    Decorator to initialize a database connection, perform the function, and then close the connection
    """
    def wrapper(*args, **kwargs):
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        #start_time = time.time()  # Capture start time
        try:
            result = func(cursor, *args, **kwargs)
            connection.commit()
            return result
        finally:
            #end_time = time.time()  # Capture end time
            #print(f"{func.__name__} took {end_time - start_time:.6f} seconds to execute.")
            cursor.close()
            connection.close()
    return wrapper

@connect
def initialize(cursor):
    """Check if necessary tables exist and create them if they do not."""
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS attendance;")

        cursor.execute("USE attendance;")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student (
                roll_no INT NOT NULL PRIMARY KEY,
                fname VARCHAR(255),
                lname VARCHAR(255),
                email_id VARCHAR(255),
                present_percentage FLOAT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS record_student (
                roll_no INT,
                date DATE,
                presence ENUM('y', 'n') DEFAULT 'n',
                FOREIGN KEY (roll_no) REFERENCES student(roll_no)
            );
        """)
        return True
    except:
        pass
        
@connect
def add_student(cursor, roll_no, fname, lname, email):
    """Inserts a new student into the table student"""
    
    query = ("INSERT INTO student (roll_no, fname, lname, email_id) "
             "VALUES (%s, %s, %s, %s)")
    try:
        cursor.execute(query, (roll_no, fname, lname, email))
        return True
    except mysql.connector.IntegrityError as e:
        print(f"IntegrityError: {e}")
        return False

@connect
def update_presence(cursor, fname, lname, roll_no):
    """Updates & inserts the presence record for a student
        1. Marks today's presence as "y" in 'record_student'
        2. Creates records for all previous days without a record
        3. Updates present_percentage in 'student'
    """
    today = datetime.date.today()
    
    cursor.execute(
        "SELECT roll_no FROM student WHERE fname = %s AND lname = %s AND roll_no = %s",
        (fname, lname, roll_no))
    if not cursor.fetchone():
        print("Student not found in the database.")
        return

    # Create absent records
    cursor.execute(
        "SELECT MAX(date) FROM record_student WHERE roll_no = %s",
        (roll_no,))
    last_date_record = cursor.fetchone()[0]

    if last_date_record and last_date_record < today:
        missing_dates = [last_date_record + timedelta(days=x) for x in range(1, (today - last_date_record).days)]
        for missing_date in missing_dates:
            cursor.execute(
                "INSERT INTO record_student (roll_no, date, presence) VALUES (%s, %s, 'n')",
                (roll_no, missing_date))

    cursor.execute(
        "SELECT presence FROM record_student WHERE roll_no = %s AND date = %s",
        (roll_no, today))
    if cursor.fetchone():
        cursor.execute(
            "UPDATE record_student SET presence = 'y' WHERE roll_no = %s AND date = %s",
            (roll_no, today))
    else:
        cursor.execute(
            "INSERT INTO record_student (roll_no, date, presence) VALUES (%s, %s, 'y')",
            (roll_no, today))
        print(f"{fname} {lname}'s presence was successfully recorded")

    # Update present_percentage
    cursor.execute(
        "SELECT COUNT(*) FROM record_student WHERE roll_no = %s AND presence = 'y'",
        (roll_no,))
    days_present = cursor.fetchone()[0]
    cursor.execute(
        "SELECT COUNT(*) FROM record_student WHERE roll_no = %s",
        (roll_no,))
    total_days = cursor.fetchone()[0]
    if total_days > 0:
        new_percentage = round((days_present / total_days) * 100, 1)
        cursor.execute(
            "UPDATE student SET present_percentage = %s WHERE roll_no = %s",
            (new_percentage, roll_no))

@connect
def view(cursor, roll_no):
    """Retrieves and returns attendance records and present percentage for a student."""
    cursor.execute(
        "SELECT date, presence FROM record_student WHERE roll_no = %s",
        (roll_no,))
    records = cursor.fetchall()

    cursor.execute(
        "SELECT fname, lname, present_percentage FROM student WHERE roll_no = %s",
        (roll_no,))
    name_percentage = cursor.fetchone()

    return records, name_percentage

@connect
def delete(cursor, roll_no):
    """Deletes the records for a student"""
    cursor.execute(
        "DELETE FROM record_student WHERE roll_no = %s",
        (roll_no,))

    cursor.execute(
        "DELETE FROM student WHERE roll_no = %s",
        (roll_no,))