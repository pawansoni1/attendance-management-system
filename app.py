from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Database Initialize karne ka function
def init_db():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    # Students table
    cursor.execute('''CREATE TABLE IF NOT EXISTS students 
                      (id TEXT PRIMARY KEY, name TEXT)''')
    # Attendance records table
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance 
                      (date TEXT, student_id TEXT, status TEXT, 
                       PRIMARY KEY (date, student_id))''')
    
    # Dummy data agar table khali ho to
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        dummy_students = [("101", "Aman Verma"), ("102", "Rahul Sharma"), ("103", "Priya Singh")]
        cursor.executemany("INSERT INTO students VALUES (?, ?)", dummy_students)
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    today = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    # Sabhi students ko le kar aao
    cursor.execute("SELECT id, name FROM students")
    all_students = cursor.fetchall()
    
    # Aaj ki attendance status check karo agar pehle se mark ho to
    cursor.execute("SELECT student_id, status FROM attendance WHERE date = ?", (today,))
    today_attendance = dict(cursor.fetchall())
    
    students_list = []
    for s_id, name in all_students:
        status = today_attendance.get(s_id, "Absent") # Default Absent
        students_list.append({"id": s_id, "name": name, "status": status})
        
    conn.close()
    return render_template('index.html', students=students_list, date=today)

@app.route('/mark', methods=['POST'])
def mark_attendance():
    today = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM students")
    all_ids = [row[0] for row in cursor.fetchall()]
    
    for s_id in all_ids:
        status = request.form.get(s_id, "Absent")
        # INSERT ya REPLACE taaki agar dubara save karein to update ho jaye
        cursor.execute("INSERT OR REPLACE INTO attendance (date, student_id, status) VALUES (?, ?, ?)", 
                       (today, s_id, status))
        
    conn.commit()
    conn.close()
    return redirect(url_for('history')) # Save karne ke baad history page par bhej rahe hain

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
            pass # ID pehle se hai to ignore karein
        conn.close()
    return redirect(url_for('index'))

# --- NAYA PAGE: Purani Attendance Dekhne Ke Liye ---
@app.route('/history')
def history():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    # Saari attendance records nikalna students ke naam ke sath
    cursor.execute('''SELECT attendance.date, attendance.student_id, students.name, attendance.status 
                      FROM attendance 
                      JOIN students ON attendance.student_id = students.id
                      ORDER BY attendance.date DESC, attendance.student_id ASC''')
    records = cursor.fetchall()
    conn.close()
    
    return render_template('history.html', records=records)

if __name__ == '__main__':
    app.run(debug=True)
