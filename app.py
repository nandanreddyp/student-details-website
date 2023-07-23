from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

## hide while submitting
import os
current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ os.path.join(current_dir, 'database.sqlite3')
db = SQLAlchemy(app)
app.app_context().push()
class Student(db.Model):
    student_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    roll_number=db.Column(db.String(100), nullable=False, unique=True)
    first_name=db.Column(db.String(100), nullable=False)
    last_name=db.Column(db.String(100))
class Course(db.Model):
    courses = {'course_1':1, 'course_2':2, 'course_3':3, 'course_4':4}
    course_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    course_code=db.Column(db.String(100), nullable=False, unique=True)
    course_name=db.Column(db.String(100), nullable=False)
    course_description=db.Column(db.String(100))
class Enrollments(db.Model):
    enrollment_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    estudent_id=db.Column(db.Integer, db.ForeignKey('student.student_id'),nullable=False)
    ecourse_id=db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)

## run once to create database
# db.create_all()

@app.route('/',methods=['GET','POST'])
def home():
    students = Student.query.all()
    return render_template('home.html', students=students)
@app.route('/student/create',methods=['GET','POST'])
def add():
    if request.method=='GET':
        return render_template('add.html')
    elif request.method=='POST':
        print(request.form['roll'])
        stud = Student.query.filter_by(roll_number=request.form['roll']).first()
        print(request.form['roll'])
        if stud is None:
            db.session.add(Student(roll_number=request.form['roll'], first_name=request.form['f_name'], last_name=request.form['l_name']))
            db.session.commit()
            courses = request.form.getlist('courses')
            for course in courses:
                db.session.add(Enrollments(estudent_id=Student.query.filter_by(roll_number=request.form['roll']).first().student_id,ecourse_id=Course.courses[course]))
                db.session.commit()
            return redirect('/')
        return render_template('exists.html')
@app.route('/student/<int:student_id>/delete', methods=['GET'])
def delete(student_id):
    Student.query.filter_by(student_id=student_id).delete()
    Enrollments.query.filter_by(estudent_id=student_id).delete()
    db.session.commit()
    return redirect('/')
@app.route('/student/<int:student_id>/update', methods=['GET','POST'])
def update(student_id):
    if request.method == 'GET':
        row = Student.query.filter_by(student_id=student_id).first()
        enrolls = Enrollments.query.filter_by(estudent_id=student_id).all()
        cid = [enroll.ecourse_id for enroll in enrolls]
        print(cid)
        return render_template('update.html', row=row, cid=cid)
    elif request.method == 'POST':
        stud = Student.query.filter_by(student_id=student_id).first()
        stud.first_name = request.form['f_name']
        stud.last_name = request.form['l_name']
        Enrollments.query.filter_by(estudent_id=student_id).delete()
        for course in request.form.getlist('courses'):
            db.session.add(Enrollments(estudent_id=student_id,ecourse_id=Course.courses[course]))
        db.session.commit()
        return redirect('/')
@app.route('/student/<int:student_id>/', methods=['GET'])
def about(student_id):
    row=Student.query.filter_by(student_id=student_id).first()
    enrolls=Enrollments.query.with_entities(Enrollments.ecourse_id).filter_by(estudent_id=student_id).all()
    cid=[]
    for enroll in enrolls:
        cid.append(enroll[0])
    courses=Course.query.filter(Course.course_id.in_(cid)).all()
    return render_template('about.html',row=row,courses=courses)

if __name__ == '__main__' :
    app.run()