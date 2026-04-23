from flask import Flask, render_template, request, redirect, flash, Response
import mysql.connector
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = db.cursor()

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

    sql = """
    INSERT INTO students(name,email,phone,course,gender,dob,address)
    VALUES(%s,%s,%s,%s,%s,%s,%s)
    """

    values = (name,email,phone,course,gender,dob,address)

    cursor.execute(sql, values)
    db.commit()
    flash("Student registered successfully 🎉")
    return redirect('/students')

@app.route('/students')
def students():

    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()

    total_students = len(data)

    cursor.execute("SELECT COUNT(DISTINCT course) FROM students")
    courses = cursor.fetchone()[0]

    cursor.execute("""
        SELECT course, COUNT(*) 
        FROM students 
        GROUP BY course
    """)
    chart_data = cursor.fetchall()

    labels = [row[0] for row in chart_data]
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
    cursor.execute("DELETE FROM students WHERE id=%s", (id,))
    db.commit()
    flash("Student deleted successfully 🗑️")
    return redirect('/students')

@app.route('/edit/<int:id>')
def edit_student(id):
    cursor.execute("SELECT * FROM students WHERE id=%s", (id,))
    student = cursor.fetchone()
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

    sql = """
    UPDATE students
    SET name=%s, email=%s, phone=%s, course=%s,
        gender=%s, dob=%s, address=%s
    WHERE id=%s
    """

    values = (name, email, phone, course, gender, dob, address, id)

    cursor.execute(sql, values)
    db.commit()
    flash("Student updated successfully ✅")
    return redirect('/students')

@app.route('/search')
def search_student():

    query = request.args.get('query')

    sql = """
    SELECT * FROM students
    WHERE name LIKE %s
       OR email LIKE %s
       OR course LIKE %s
    """

    search_term = "%" + query + "%"

    cursor.execute(sql, (search_term, search_term, search_term))
    data = cursor.fetchall()

    return render_template('dashboard.html', students=data)

@app.route('/export')
def export_csv():

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    csv_data = "ID,Name,Email,Phone,Course,Gender,DOB,Address\n"

    for student in students:
        csv_data += f"{student[0]},{student[1]},{student[2]},{student[3]},{student[4]},{student[5]},{student[6]},{student[7]}\n"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition":"attachment; filename=students.csv"}
    )


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get("PORT", 5000))
    )