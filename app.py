from flask import Flask, render_template, request, redirect, flash, Response
"""import mysql.connector"""
import sqlite3
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "students.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        course TEXT,
        gender TEXT,
        dob TEXT,
        address TEXT
    )
    """)

    conn.commit()
    conn.close()

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

@app.route("/")
def home():
    return render_template("index.html")

"""db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = db.cursor()"""

def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect('students.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            course TEXT,
            gender TEXT,
            dob TEXT,
            address TEXT
        )
    ''')
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_student():

    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    course = request.form['course']
    gender = request.form['gender']
    dob = request.form['dob']
    address = request.form['address']

    conn = get_db_connection()
    conn.execute(
    """
    INSERT INTO students(name,email,phone,course,gender,dob,address)
    VALUES(?,?,?,?,?,?,?)
    """,
    (name, email, phone, course, gender, dob, address)
)
    conn.commit()
    conn.close()
    flash("Student registered successfully 🎉")
    return redirect('/students')

@app.route('/students')
def students():

    conn = get_db_connection()

    data = conn.execute("SELECT * FROM students").fetchall()

    total_students = len(data)

    courses = conn.execute("SELECT COUNT(DISTINCT course) FROM students").fetchone()[0]

    chart_data = conn.execute("""
        SELECT course, COUNT(*) 
        FROM students 
        GROUP BY course
    """).fetchall()

    conn.close()

    labels = [row["course"] for row in chart_data]
    values = [row[1] for row in chart_data]

    return render_template(
        'dashboard.html',
        students=data,
        total_students=total_students,
        total_courses=courses,
        labels=labels,
        values=values
    )


@app.route('/delete/<int:id>')
def delete_student(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Student deleted successfully 🗑️")
    return redirect('/students')

@app.route('/edit/<int:id>')
def edit_student(id):
    conn = get_db_connection()
    student = conn.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template('edit.html', student=student)

@app.route('/update/<int:id>', methods=['POST'])
def update_student(id):

    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    course = request.form['course']
    gender = request.form['gender']
    dob = request.form['dob']
    address = request.form['address']

    conn = get_db_connection()
    conn.execute(
    """
    UPDATE students
    SET name=?, email=?, phone=?, course=?,
        gender=?, dob=?, address=?
    WHERE id=?
    """,
    (name, email, phone, course, gender, dob, address, id)
)
    conn.commit()
    conn.close()
    flash("Student updated successfully ✅")
    return redirect('/students')

@app.route('/search')
def search_student():
    query = request.args.get('query', '')
    conn = get_db_connection()
    search_term = "%" + query + "%"
    data = conn.execute(
    """
    SELECT * FROM students
    WHERE name LIKE ?
       OR email LIKE ?
       OR course LIKE ?
    """,
(search_term, search_term, search_term)
).fetchall()
    conn.close()
    """data = cursor.fetchall()"""
    return render_template('dashboard.html', students=data)

@app.route('/export')
def export_csv():

    """cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()"""

    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    csv_data = "ID,Name,Email,Phone,Course,Gender,DOB,Address\n"
    
    for student in students:
        csv_data += f"{student['id']},{student['name']},{student['email']},{student['phone']},{student['course']},{student['gender']},{student['dob']},{student['address']}"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition":"attachment; filename=students.csv"}
    )

app = Flask(__name__)

@app.before_first_request
def initialize():
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))