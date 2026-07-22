from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    # Students Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS students 
                      (id TEXT PRIMARY KEY, name TEXT)''')
    
    # Detailed Attendance Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance 
                      (date TEXT, day TEXT, time TEXT, student_id TEXT, status TEXT)''')
    
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        dummy_students = [("101", "Aman Verma"), ("102", "Rahul Sharma"), ("103", "Priya Singh")]
        cursor.executemany("INSERT INTO students VALUES (?, ?)", dummy_students)
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d')
    current_day = now.strftime('%A')       # E.g., Wednesday
    current_time = now.strftime('%I:%M %p') # E.g., 06:45 PM
    
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM students")
    students_list = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    conn.close()
    
    return render_template('index.html', 
                           students=students_list, 
                           date=current_date, 
                           day=current_day, 
                           time=current_time)

@app.route('/mark', methods=['POST'])
def mark_attendance():
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d')
    current_day = now.strftime('%A')
    current_time = now.strftime('%I:%M:%S %p')
    
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM students")
    all_ids = [row[0] for row in cursor.fetchall()]
    
    for s_id in all_ids:
        status = request.form.get(s_id, "Absent")
        # Direct Insert taaki har baar ki submission date/time ke sath record ho
        cursor.execute("INSERT INTO attendance (date, day, time, student_id, status) VALUES (?, ?, ?, ?, ?)", 
                       (current_date, current_day, current_time, s_id, status))
        
    conn.commit()
    conn.close()
    return redirect(url_for('history'))

@app.route('/add_student', methods=['POST'])
def add_student():
    student_id = request.form.get('student_id')
    student_name = request.form.get('student_name')
    
    if student_id and student_name:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO students (id, name) VALUES (?, ?)", (student_id, student_name))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        conn.close()
    return redirect(url_for('index'))

# --- NEW: Student Remove Route ---
@app.route('/delete_student/<student_id>', methods=['POST'])
def delete_student(student_id):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/history')
def history():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    # History with Date, Day, Time, Roll No, Name, Status
    cursor.execute('''SELECT attendance.date, attendance.day, attendance.time, attendance.student_id, students.name, attendance.status 
                      FROM attendance 
                      JOIN students ON attendance.student_id = students.id
                      ORDER BY attendance.date DESC, attendance.time DESC''')
    records = cursor.fetchall()
    conn.close()
    
    return render_template('history.html', records=records)

if __name__ == '__main__':
    app.run(debug=True)
