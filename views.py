import os
import sys
import time
from flask import Flask, redirect, url_for, render_template, request, session, Response
from pymongo import MongoClient
import json
import bson.json_util as json_util
import bcrypt
import string
from werkzeug.utils import secure_filename
import threading



from database import *
config = {}
config["UPLOAD_FOLDER"] = "static/uploads/"
ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg"]

# To parse the responsse from MongoDB
def parse_json(data):
    return json.loads(json_util.dumps(data))

# To obtain hash of the password
def hash_pass(passwd):
    bytes = passwd.encode('utf-8')
    # generating the salt
    salt = bcrypt.gensalt()
    # Hashing the password
    hash = bcrypt.hashpw(bytes, salt)
    return hash

# To check password against stored password
def chech_hash(passwd, hash):
    userBytes = passwd.encode('utf-8')
    # checking password
    result = bcrypt.checkpw(userBytes, hash)
    return result

# TO AUTHENTICATE USER CREDENTIALS
def user_auth(type, user, passwd):
    userdata = type.find_one({'email' : user })
    if userdata:
        passwd_match = chech_hash(passwd, userdata['password'])
        if userdata['email'] == user and passwd_match:
            #login sucessful
            return parse_json(userdata)
        else:
            # Wrong credentials
            return 0
    else:
        # User doesnt exist 
        return -1

# TO AUTHENTICATE USER CREDENTIALS
def admin_auth(type, user, passwd):
    admindata = type.find_one({'email' : user })
    if admindata:
        if admindata['email'] == user and admindata['password']:
            #login sucessful
            return parse_json(admindata)
        else:
            # Wrong credentials
            return 0
    else:
        # User doesnt exist 
        return -1

def check_ip(type, ip):
    v = type.find_one({'ip' : ip })
    if v is None:
        values = {
            'ip': ip
        }
        add_one(visitor, values)
        



def timer():
    def countdown(seconds):
        i = seconds
        while i > 0:
            time.sleep(1) #put 60 here if you want to have seconds
            i -= 1
            return str(i)
    return Response(countdown(50), mimetype='text/html') #at the moment the time value is hardcoded in the function just for simplicity






def home():
    if request.method == "POST":
        if request.form['action'] == "login":
            return render_template(url_for("student_login"))
    else:
        ip = request.remote_addr
        check_ip(visitor, ip)
        return render_template("index.html")


def student_login():
    if request.method == "POST":
        # Checking the role of login
        user = request.form['username']
        passwd = request.form['password']
        check = user_auth(student, user, passwd)
        if(check == -1):
            # User does not exist 
            return render_template("student_login.html", msg="User does not exist!")
        elif(check == 0):
            # Wrong password 
            return render_template("student_login.html", msg="Wrong Password! Please try again.....")
        else:
            session['user_data'] = check['email']
            session['user_type'] = "student"
            ip = request.remote_addr
            return redirect(url_for('student_home'))
    else:
        if 'user_type' in session:
            if session['user_type'] == 'student':
                return redirect(url_for('student_home'))
            if session['user_type'] == 'franchise':
                return redirect(url_for('franch_home'))
            if session['user_type'] == 'admin':
                return redirect(url_for('admin_home'))
        return render_template("student_login.html")


def franch_login():
    if request.method == "POST":
        # Checking the role of login
        user = request.form['username']
        passwd = request.form['password']
        check = user_auth(franchise, user, passwd)
        if(check == -1):
            # User does not exist 
            return render_template("franch_login.html", msg="User does not exist!")
        elif(check == 0):
            # Wrong password 
            return render_template("franch_login.html", msg="Wrong Password! Please try again.....")
        else:
            session['user_data'] = check['name']
            session['user_type'] = 'franchise'
            return render_template('franch_home.html')

    else:
        if 'user_type' in session:
            if session['user_type'] == 'student':
                return redirect(url_for('student_home'))
            if session['user_type'] == 'franchise':
                return redirect(url_for('franch_home'))
            if session['user_type'] == 'admin':
                return redirect(url_for('admin_home'))
        return render_template("franch_login.html")


def admin_login():
    if request.method == "POST":
        # Checking the role of login
        user = request.form['username']
        passwd = request.form['password']
        check = admin_auth(admin, user, passwd)
        if(check == -1):
            # User does not exist 
            return render_template("admin_login.html", msg="User does not exist!")
        elif(check == 0):
            # Wrong password 
            return render_template("admin_login.html", msg="Wrong Password! Please try again.....")
        else:
            session['user_data'] = check['email']
            session['user_type'] = 'admin'
            return redirect(url_for('admin_home'))

    else:
        if 'user_type' in session:
            if session['user_type'] == 'student':
                return redirect(url_for('student_home'))
            if session['user_type'] == 'franchise':
                return redirect(url_for('franch_home'))
            if session['user_type'] == 'admin':
                return redirect(url_for('admin_home'))
        return render_template("admin_login.html")



def show_home():
    if 'user_type' in session:
        if session['user_type'] == 'student':
            return redirect(url_for('student_home'))
        if session['user_type'] == 'franchise':
            return redirect(url_for('franch_home'))
        if session['user_type'] == 'admin':
            return redirect(url_for('admin_home'))
    else:
        return redirect(url_for('student_login'))




def view_tests():
    if 'user_type' in session:        
        if request.method == "POST":
            if 'test_delete' in request.form:
                delete_one(test, 'name', request.form['test_delete'])
                tests = get_many(test)
                return render_template('view_tests.html', tests = tests)
            if 'test_edit' in request.form:
                session['test'] = request.form['test_edit']
                return redirect(url_for('edit_test'))
                # return render_template('s.html', var = request.form['student_edit'])
        else:
            tests = get_tests()
            return render_template('view_tests.html', tests = tests, msg = session.pop('msg', None))
    else:
        return redirect(url_for('admin_login'))






def choose_era():
    if 'user_type' in session:
        if request.method == "POST":
            exist = check_quiz(session['user_data'], 'era', request.form['era'])
            if exist == 1:
                msg = "You have already attempted the quiz!"
                stud = get_one(student, 'email', session['user_data'])
                test = stud['level']
                eras = get_many(era, 'test', test)
                return render_template('choose_era.html', eras = eras, msg = msg)
            else:
                session['era'] = request.form['era']
                return redirect(url_for('take_quiz'))
        else:
            # pass
            stud = get_one(student, 'email', session['user_data'])
            test = stud['level']
            eras = get_many(era, 'test', test)
            return render_template('choose_era.html', eras = eras)
    else:
        return redirect(url_for('student_login'))


def take_quiz():
    if request.method == "GET":
        students = get_one(student, 'email', session['user_data'])
        questions = get_many(era_q, 'era', session['era'])
        tests = get_one(era, 'name', session['era'])
        l = []
        for q in questions:
            l.append(q)
        return render_template('quiz.html', questions = questions, era = tests, student = students, data = l)


def choose_exam():
    if 'user_type' in session:
        if request.method == "POST":
            exist = check_quiz(session['user_data'], 'test', request.form['test'])
            if exist == 1:
                msg = "You have already attempted the quiz!"
                stud = get_one(student, 'email', session['user_data'])
                tests = stud['level']
                return render_template('choose_exam.html', test = tests, msg = msg)
            else:
                session['test'] = request.form['test']
                return redirect(url_for('take_exam'))
        else:
            # pass
            stud = get_one(student, 'email', session['user_data'])
            tests = stud['level']
            return render_template('choose_exam.html',test = tests)
    else:
        return redirect(url_for('student_login'))

def submit_exam():
    if request.method == "POST":
        user_answers = request.get_json()
        correct_answer = []
        marks = 0
        questions = get_many(question, 'test', session['test'])
        for q in questions:
            correct_answer.append(q['answer'])
        
        total = len(correct_answer)
        for i in range(total):
            if str(correct_answer[i]) == str(user_answers[i]):
                marks = marks + 1
        final_score = [marks, total]
        print(marks)
        store_quiz(session['user_data'],  'test', final_score)
        # store_quiz(session['user_data'], 'test', session['test'], final_score)
        return redirect(url_for('student_home'))
    

def submit_quiz():
    if request.method == "POST":
        marks = request.get_json()
        # questions = get_many(era_q, 'era', session['era'])
        # for q in questions:
        #     correct_answer.append(q['answer'])
        
        # total = len(correct_answer)
        # for i in range(total):
        #     if str(correct_answer[i]) == str(user_answers[i]):
        #         marks = marks + 1
        new_data = {}
        new_data[session['era']] = 1
        stud = get_one(student, 'email', session['user_data'])
        # if 'era' in stud:
        eras = stud['era']
        for e in eras:
            new_data[e] = 1

        student.update_one({"email": session['user_data']}, {"$set": {"era": new_data}})
        print(new_data)
        # student.update_one({"email": session['email']}, {"$push": {"era": {"$each": [new_data]}}})1
        # edit_one(student, 'email', session['email'], new_data)
        return redirect(url_for('student_home'))


def take_exam():
    if request.method == "GET":
        students = get_one(student, 'email', session['user_data'])
        if students['allow'] == "Allowed":
            questions = get_many(question, 'test', session['test'])
            tests = get_one(test, 'name', session['test'])
            l = []
            for q in questions:
                l.append(q)
            return render_template('exam.html', questions = questions, era = tests, student = students, data = l)
        else:
            session['msg'] = "Not allowed to give exam!"
            return redirect(url_for('student_home'))






def era_status():
    stud = get_one(student, 'email', session['user_data'])
    if 'era' in stud:
        s = stud['era']
    else:
        s = ''
    return render_template('era_status.html', result = s)
    




def exam_result():
    stud = get_one(student, 'email', session['user_data'])
    if 'test' in stud:
        s = stud['test']
    else:
        s = ''
    stud = get_one(student, 'email', session['user_data'])
    
    return render_template('result.html', result = s, student = stud)


def student_results():
    if 'user_type' in session:
        if request.method == 'POST':
            score = request.form['score']
            stud = get_one(student, 'email', request.form['print'])
            if stud['filename'] != "":
                return render_template('admin_certificate.html', score = score, stud = stud)
            else:
                s = get_many(student)
                session['msg'] = 'Please add Passport image first!'
                return render_template('admin_students_result.html', students = s, name = 'test', msg = session.pop('msg', None))
        else:
            s = get_many(student)
            return render_template('admin_students_result.html', students = s, name = 'test')
    else:
        return redirect(url_for('admin_login'))


def student_results_era():
    if 'user_type' in session:
        if session['user_type'] == 'admin':
            students = get_many(student)
            return render_template('admin_students_result_era.html', students = students, name = 'era')
        if session['user_type'] == 'franchise':
            students = get_many(student, 'franchise', session['user_data'])
            return render_template('franch_students_result_era.html', students = students, name = 'era')
    else:
        return redirect(url_for('admin_login'))



def student_result():
    if 'user_type' in session:
        if request.method == 'POST':
            score = request.form['score']
            stud = get_one(student, 'email', request.form['print'])
            if stud['filename'] != "":
                return render_template('franch_certificate.html', score = score, stud = stud)
            else:
                students = get_many(student, 'franchise', session['user_data'])
                session['msg'] = 'Please add Passport image first!'
                return render_template('view_students_result.html', students = students, name = 'test', msg = session.pop('msg', None))
        else:
            students = get_many(student, 'franchise', session['user_data'])
            return render_template('view_students_result.html', students = students, name = 'test')
    else:
        return redirect(url_for('admin_login'))



def student_result_era():
    if 'user_type' in session:
        students = get_many(student, 'franchise', session['user_data'])
        return render_template('admin_students_result_era.html', students = students, name = 'era')
    else:
        return redirect(url_for('admin_login'))



























def edit_test():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'update' in request.form:
                new_values = { "$set": {
                        "name": request.form['name'],
                        "duration": request.form['duration']
                        }}
                # add_student(new_values)
                edit_one(test, 'name', session['test'], new_values)
                # return render_template('s.html', var = session['phone'])

                session['test'] = request.form['name']
                data = get_one(test, 'name', session['test'])
                return render_template('edit_test.html', test = data)
            else:
                data = get_one(test, 'name', session['test'])
                return render_template('edit_test.html', test = data)

        else:
            data = get_one(test, 'name', session['test'])
            return render_template('edit_test.html', test = data)
        # else:
        #     if stud_phone:
        #         student_info = get_student(stud_phone)
        #         return render_template('edit_student.html', student = student_info)
    else:
        return redirect(url_for('admin_login'))




def view_test_questions():
    if 'user_type' in session:        
        if request.method == "POST":
            if 'delete' in request.form:
                delete_one(question, 'name', request.form['delete'])
                data = get_many(question)
                return render_template('view_questions.html', questions = data)
                
            if 'edit' in request.form:
                session['question'] = request.form['edit']
                return redirect(url_for('edit_test_question'))
                # return render_template('s.html', var = request.form['student_edit'])
        else:
            data = get_many(question)
            return render_template('view_questions.html', questions = data, msg = session.pop('msg', None))
    else:
        return redirect(url_for('admin_login'))




def edit_test_question():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'update' in request.form:
                new_values = { "$set": {
                        "name": request.form['name'],
                        "options": request.form['options'],
                        "answer": request.form['answer']
                        }}
                # add_student(new_values)
                edit_one(question, 'name', session['question'], new_values)
                # return render_template('s.html', var = session['phone'])

                session['question'] = request.form['name']
                data = get_one(question, 'name', session['question'])
                return render_template('edit_question.html', question = data)
            else:
                data = get_one(question, 'name', session['question'])
                return render_template('edit_question.html', question = data)

        else:
            data = get_one(question, 'name', session['question'])
            return render_template('edit_question.html', question = data)
        # else:
        #     if stud_phone:
        #         student_info = get_student(stud_phone)
        #         return render_template('edit_student.html', student = student_info)
    else:
        return redirect(url_for('admin_login'))





def view_subjects():
    if 'user_type' in session:        
        if request.method == "POST":
            if 'subject_delete' in request.form:
                delete_one(subject, 'name', request.form['subject_delete'])
                data = get_many(subject)
                return render_template('view_subjects.html', subjects = data)
                
            if 'subject_edit' in request.form:
                session['subject'] = request.form['subject_edit']
                return redirect(url_for('edit_subject'))
                # return render_template('s.html', var = request.form['student_edit'])
        else:
            tests = get_many(subject)
            return render_template('view_subjects.html', subjects = tests, msg = session.pop('msg', None))
    else:
        return redirect(url_for('admin_login'))



def edit_subject():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'update' in request.form:
                new_values = { "$set": {
                        "name": request.form['name']
                        }}
                # add_student(new_values)
                check = check_data(subject, 'name', request.form['name'])
                if check == 0:
                    edit_one(subject, 'name', session['subject'], new_values)
                    session['subject'] = request.form['name']
                    data = get_one(subject, 'name', session['subject'])
                    return render_template('edit_subject.html', subject = data)
                else:
                    session['msg'] = "This Subject already exists"
                    return redirect(url_for('view_subjects'))

            else:
                data = get_one(subject, 'name', session['subject'])
                return render_template('edit_subject.html', subject = data)

        else:
            data = get_one(subject, 'name', session['subject'])
            return render_template('edit_subject.html', subject = data)
        # else:
        #     if stud_phone:
        #         student_info = get_student(stud_phone)
        #         return render_template('edit_student.html', student = student_info)
    else:
        return redirect(url_for('admin_login'))



def add_test():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'add' in request.form:
                values = {
                        "name": request.form['name'],
                        "subject": request.form['subject'],
                        "duration": request.form['duration'],
                        "total_question": request.form['total_q']
                }
                check = check_data(test, 'name', request.form['name'])
                if check == 0:
                    add_one(test, values)
                    return redirect(url_for('view_tests'))
                else:
                    session['msg'] = "This Test already exists"
                    return redirect(url_for('view_tests'))
                    
            else:
                return render_template('add_test.html')

        else:
            subjects = get_many(subject)
            return render_template('add_test.html', subjects = subjects)

    else:
        return render_template('admin_login.html')




def add_test_question():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'add' in request.form:
                count = question.count_documents({'test' : request.form['test']})
                # if count != None:
                data = get_one(test, 'name', request.form['test'])
                if count >= int(data['total_question']):
                    session['msg'] = "Maximum number of Questions reached!"
                    return redirect(url_for('view_test_questions'))
                values = {
                        "_id": (question.count_documents({}) + 1),
                        "name": request.form['name'],
                        "test": request.form['test'],
                        "type": request.form['type'],
                        "options": request.form['options'],
                        "answer": request.form['answer']
                }
                check = check_data(question, 'name', request.form['name'])
                if check == 0:
                    add_one(question, values)
                    return redirect(url_for('view_test_questions'))
                else:
                    session['msg'] = "This Question already exists"
                    return redirect(url_for('view_test_questions'))
                    
            else:
                return render_template('add_question.html')

        else:
            tests = get_many(test)
            return render_template('add_question.html', tests = tests)

    else:
        return render_template('admin_login.html')




def add_subject():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'add' in request.form:
                values = {
                        "name": request.form['name']
                }
                check = check_data(subject, 'name', request.form['name'])
                if check == 0:
                    add_one(subject, values)
                    return redirect(url_for('view_subjects'))
                else:
                    session['msg'] = "This Subject already exists"
                    return redirect(url_for('view_subjects'))
                    
            else:
                return render_template('add_subject.html')

        else:
            franchises = get_many(franchise)
            subjects = get_many(subject)
            return render_template('add_subject.html', franchises = franchises, subjects = subjects)

    else:
        return render_template('admin_login.html')







def view_era():
    if 'user_type' in session:        
        if request.method == "POST":
            if 'delete' in request.form:
                delete_one(era, 'name', request.form['delete'])
                data = get_many(era)
                return render_template('view_era.html', eras = data)
                
            if 'edit' in request.form:
                session['era'] = request.form['edit']
                return redirect(url_for('edit_era'))
                # return render_template('s.html', var = request.form['student_edit'])
        else:
            data = get_many(era)
            return render_template('view_era.html', eras = data, msg = session.pop('msg', None))
    else:
        return redirect(url_for('admin_login'))




def view_era_question():
    if 'user_type' in session:        
        if request.method == "POST":
            if 'delete' in request.form:
                delete_one(era_q, 'name', request.form['delete'])
                data = get_many(era_q)
                return render_template('view_era_questions.html', questions = data)
                
            if 'edit' in request.form:
                session['era_question'] = request.form['edit']
                return redirect(url_for('edit_era_question'))
                # return render_template('s.html', var = request.form['student_edit'])
        else:
            data = get_many(era_q)
            return render_template('view_era_questions.html', questions = data, msg = session.pop('msg', None))
    else:
        return redirect(url_for('admin_login'))




def edit_era_question():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'update' in request.form:
                new_values = { "$set": {
                        "name": request.form['name'],
                        "type": request.form['type'],
                        "options": request.form['options'],
                        "answer": request.form['answer']
                        }}
                # add_student(new_values)
                
                edit_one(era_q, 'name', session['era_question'], new_values)
                session['era_question'] = request.form['name']
                data = get_one(era_q, 'name', session['era_question'])
                return render_template('edit_era_question.html', question = data)
                
            else:
                data = get_one(era_q, 'name', session['era_question'])
                return render_template('edit_era_question.html', question = data)

        else:
            data = get_one(era_q, 'name', session['era_question'])
            return render_template('edit_era_question.html', question = data)
        # else:
        #     if stud_phone:
        #         student_info = get_student(stud_phone)
        #         return render_template('edit_student.html', student = student_info)
    else:
        return redirect(url_for('admin_login'))



def add_era_question():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'add' in request.form:
                count = era_q.count_documents({'era' : request.form['era']})
                # if count != None:
                data = get_one(era, 'name', request.form['era'])
                if count >= int(data['total_question']):
                    session['msg'] = "Maximum number of Questions reached!"
                    return redirect(url_for('view_era_question'))
                values = {
                        "_id": (era_q.count_documents({}) + 1),
                        "test": request.form['test'],
                        "era": request.form['era'],
                        "name": request.form['name'],
                        "type": request.form['type'],
                        "options": request.form['options'],
                        "answer": request.form['answer']
                }
                check = check_data(era_q, 'name', request.form['name'])
                if check == 0:
                    add_one(era_q, values)
                    return redirect(url_for('view_era_question'))
                else:
                    session['msg'] = "This Question already exists"
                    return redirect(url_for('view_era_question'))
                    
            else:
                tests = get_many(test)
                eras = get_many(era)
                return render_template('add_era_question.html', tests = tests, eras = eras)

        else:
            tests = get_many(test)
            eras = get_many(era)
            return render_template('add_era_question.html', tests = tests, eras = eras)

    else:
        return render_template('admin_login.html')




def add_era():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'add' in request.form:
                values = {
                        "name": request.form['name'],
                        "test": request.form['test'],
                        "duration": request.form['duration'],
                        "subject": request.form['subject'],
                        "total_question": request.form['total_q']
                }
                check = check_data(era, 'name', request.form['name'])
                if check == 0:
                    add_one(era, values)
                    return redirect(url_for('view_era'))
                else:
                    session['msg'] = "This ERA already exists"
                    return redirect(url_for('view_era'))
                    
            else:
                return render_template('add_era.html')

        else:
            tests = get_many(test)
            sub = get_many(subject)
            return render_template('add_era.html', tests = tests, subjects = sub)

    else:
        return render_template('admin_login.html')




def edit_era():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'update' in request.form:
                new_values = { "$set": {
                        "name": request.form['name'],
                        "test": request.form['test'],
                        "subject": request.form['subject'],
                        "duration": request.form['duration'],
                        "total_q": request.form['total_q']
                        }}

                # check = check_data(era, 'name', request.form['name'])
                # if check == 0:
                edit_one(era, 'name', session['era'], new_values)
                session['era'] = request.form['name']
                data = get_one(era, 'name', session['era'])
                tests = get_many(test)
                return render_template('edit_era.html', era = data, tests = tests)
                # else:
                #     session['msg'] = "This ERA already exists"
                #     return redirect(url_for('view_era'))
            else:
                data = get_one(era, 'name', session['era'])
                tests = get_many(test)
                sub = get_many(subject)
                return render_template('edit_era.html', era = data, tests = tests, subjects = sub)
        else:
            data = get_one(era, 'name', session['era'])
            tests = get_many(test)
            sub = get_many(subject)
            return render_template('edit_era.html', era = data, tests = tests, subjects = sub)
        # else:
        #     if stud_phone:
        #         student_info = get_student(stud_phone)
        #         return render_template('edit_student.html', student = student_info)
    else:
        return redirect(url_for('admin_login'))





def era_result():
    pass



def student_home():
    background = "{{ url_for('static', filename='images/banner/b4.jpg' )}}"
    if 'user_type' in session:
        if request.method == "POST":
            pass
        else:
            return render_template('student_home.html', bg = background, msg = session.pop('msg', None))
    else:
        return redirect(url_for('student_login'))




def get_hallticket():
    if 'user_type' in session:        
        if request.method == "POST":
            pass
        else:
            data = get_one(student, 'email', session['user_data'])
            return render_template('hallticket.html', student = data)
    else:
        return redirect(url_for('admin_login'))



def franch_home():
    if 'user_type' in session:
        if request.method == "POST":
            pass
        else:
            return render_template('franch_home.html', v = visitor.count_documents({}))
    else:
        return redirect(url_for('student_login'))




def franch_view_students():
    if 'user_type' in session:        
        if request.method == "POST":
            if 'student_delete' in request.form:
                delete_one(student, 'email', request.form['student_delete'])
                students = get_many(student, 'franchise', session['user_data'])
                return render_template('view_franch_students.html', students = students)
            if 'student_edit' in request.form:
                session['email'] = request.form['student_edit']
                return redirect(url_for('edit_franch_student'))
                # return render_template('s.html', var = request.form['student_edit'])
        else:
            students = get_many(student, 'franchise', session['user_data'])
            return render_template('view_franch_students.html', students = students, msg = session.pop('msg', None))
    else:
        return redirect(url_for('admin_login'))




def edit_franch_student():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'update' in request.form:
                student_info = get_one(student, 'email', session['email'])
                filename = student_info['filename']
                if 'photo' in request.files:
                    file_path = (config["UPLOAD_FOLDER"] + student_info['filename'])
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    image = request.files['photo']
                    if image and image.filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS:
                        filename = secure_filename(image.filename)
                        image.save(os.path.join(config["UPLOAD_FOLDER"], filename))
                new_values = { "$set": {
                        "email": request.form['email'],
                        "name": request.form['full_name'], 
                        "aadhar": request.form['aadhar'],
                        "dob": request.form['dob'],
                        "joining_date": request.form['doj'],
                        "phone" : request.form['phone'],
                        "level": request.form['level'],
                        "school": request.form['school'],
                        "address": request.form['address'],
                        "filename": filename
                        }}
                # add_student(new_values)
                # check = check_data(student, 'email', request.form['email'])
                # if check == 0:
                edit_one(student, 'email', session['email'], new_values)
            # return render_template('s.html', var = session['phone'])
                session['email'] = request.form['email']
                student_info = get_one(student, 'email', session['email'])
                return render_template('edit_franch_student.html', student = student_info)

                # else:
                #     session['msg'] = "This User already exists"
                #     return redirect(url_for('view_students'))


                    # return render_template('s.html', var = session['phone'])

            else:
                student_info = get_one(student, 'email', session['email'])
                return render_template('edit_franch_student.html', student = student_info)
                # return render_template('s.html', var = request.form['dob'])
                # student_info = get_student(stud_phone)
                # return render_template('edit_student.html', student = student_info)

        # return render_template('s.html', var = request.form['email'])
        else:
            student_info = get_one(student, 'email', session['email'])
            return render_template('edit_franch_student.html', student = student_info)
        # else:
        #     if stud_phone:
        #         student_info = get_student(stud_phone)
        #         return render_template('edit_student.html', student = student_info)
    else:
        return redirect(url_for('admin_login'))







def franch_profile():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'update' in request.form:
                new_values = { "$set": {
                        "email": request.form['email'],
                        "name": request.form['full_name'], 
                        "dir_name": request.form['dir_name'], 
                        "aadhar": request.form['aadhar'],
                        "phone" : request.form['phone'],
                        "address": request.form['address']
                        }}
                # check = check_data(franchise, 'email', request.form['email'])
                # if check == 0:
                # edit_franch(session['email'], new_values)
                edit_one(franchise, 'name', session['user_data'], new_values)
            # return render_template('s.html', var = session['phone'])
                
                session['user_data'] = request.form['full_name']
                franchise_info = get_one(franchise, 'name', session['user_data'])
                return render_template('franch_profile.html', franchise = franchise_info)
                # else:
                #     session['msg'] = "This Franchise already exists"
                #     return redirect(url_for('view_franchises'))


                # add_student(new_values)
                
            else:
                franchise_info = get_one(franchise, 'name', session['user_data'])
                return render_template('franch_profile.html', franchise = franchise_info)
                # return render_template('s.html', var = request.form['dob'])
                # student_info = get_student(stud_phone)
                # return render_template('edit_student.html', student = student_info)

        # return render_template('s.html', var = request.form['email'])
        else:
            franchise_info = get_one(franchise, 'name', session['user_data'])
            return render_template('franch_profile.html', franchise = franchise_info)
        # else:
        #     if stud_phone:
        #         student_info = get_student(stud_phone)
        #         return render_template('edit_student.html', student = student_info)
    else:
        return redirect(url_for('franch_login'))




def admin_home():
    if session['user_type'] == 'admin':
        if request.method == "POST":
            # if 'view_students' in request.form:
            #     redirect(url_for('view_students'))
            pass
        else:
            return render_template('admin_home.html', v = visitor.count_documents({}))
    else:
        return redirect(url_for('admin_login'))




def view_students():
    if 'user_type' in session:        
        if request.method == "POST":
            if 'student_delete' in request.form:
                delete_one(student, 'email', request.form['student_delete'])
                students = get_many(student)
                return render_template('view_students.html', students = students)
            if 'student_edit' in request.form:
                session['email'] = request.form['student_edit']
                return redirect(url_for('edit_student'))
                # return render_template('s.html', var = request.form['student_edit'])
            if 'student_allow' in request.form:
                session['email'] = request.form['student_allow']
                set_allow(session['email'])
                return redirect(url_for('view_students'))
        else:
            students = get_many(student)
            return render_template('view_students.html', students = students, msg = session.pop('msg', None))
    else:
        return redirect(url_for('admin_login'))




def add_student():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'add' in request.form:
                filename = ""
                if 'photo' in request.files:
                    image = request.files['photo']
                    if image and image.filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS:
                        filename = secure_filename(image.filename)
                        image.save(os.path.join(config["UPLOAD_FOLDER"], filename))

                values = {
                        "_id": (student.count_documents({}) + 1),
                        "email": request.form['email'],
                        "password": hash_pass(request.form['password']),
                        "name": request.form['full_name'], 
                        "aadhar": request.form['aadhar'],
                        "dob": request.form['dob'],
                        "joining_date": request.form['doj'],
                        "phone" : request.form['phone'],
                        "franchise" : request.form['franchise'],
                        "subject" : request.form['subject'],
                        "level": request.form['level'],
                        "allow": "Not Allowed",
                        "school": request.form['school'],
                        "address": request.form['address'],
                        "era": "",
                        "test": "",
                        "filename": filename
                }
                check = check_stud(request.form['email'])
                if check == 0:
                    add_stud(values)
                    return redirect(url_for('view_students'))
                else:
                    session['msg'] = "This Student Already exists!"
                    return redirect(url_for('view_students'))
                    
            else:
                return render_template('add_student.html')
        else:
            franchises = get_franchs()
            subjects = get_subjects()
            tests = get_many(test)
            return render_template('add_student.html', franchises = franchises, subjects = subjects, tests = tests)

    else:
        return render_template('admin_login.html')



def franch_add_student():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'add' in request.form:
                filename = ""
                if 'photo' in request.files:
                    franch_info = get_one(franchise, 'name', session['user_data'])
                    image = request.files['photo']
                    if image and image.filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS:
                        filename = secure_filename(image.filename)
                        image.save(os.path.join(config["UPLOAD_FOLDER"], filename))
                        
                values = {
                        "_id": (student.count_documents({}) + 1),
                        "email": request.form['email'],
                        "password": hash_pass(request.form['password']),
                        "name": request.form['full_name'], 
                        "aadhar": request.form['aadhar'],
                        "dob": request.form['dob'],
                        "joining_date": request.form['doj'],
                        "phone" : request.form['phone'],
                        "franchise" : franch_info['name'],
                        "subject" : request.form['subject'],
                        "level": request.form['level'],
                        "allow": "Not Allowed",
                        "school": request.form['school'],
                        "address": request.form['address'],
                        "filename": filename
                }
                check = check_stud(request.form['email'])
                if check == 0:
                    add_stud(values)
                    return redirect(url_for('franch_view_students'))
                else:
                    session['msg'] = "This Student Already exists!"
                    return redirect(url_for('franch_view_students'))
                    
            else:
                return render_template('add_franch_student.html')
        else:
            franchises = get_one(franchise, 'name', session['user_type'])
            tests = get_many(test)
            subjects = get_many(subject)
            return render_template('add_franch_student.html', franchises = franchises, tests = tests, subjects = subjects)

    else:
        return render_template('admin_login.html')


def admin_profile():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'update' in request.form:
                new_values = { "$set": {
                        "email": request.form['email'],
                        "name": request.form['full_name'],
                        "password": request.form['password']
                        }}
            # add_student(new_values)
                edit_stud(session['user_data'], new_values)
                # return render_template('s.html', var = session['phone'])

                admin_info = get_one(admin, 'email', request.form['email'])
                session['user_data'] = admin_info['email']
                return render_template('admin_profile.html', admin = admin_info)
            else:
                admin_info = get_one(admin, 'email', session['user_data'])
                return render_template('admin_profile.html', admin = admin_info)
                # return render_template('s.html', var = request.form['dob'])
                # admin_info = get_student(stud_phone)
                # return render_template('edit_student.html', student = admin_info)

        # return render_template('s.html', var = request.form['email'])
        else:
            admin_info = get_one(admin, 'email', session['user_data'])
            return render_template('admin_profile.html', admin = admin_info)
        # else:
        #     if stud_phone:
        #         admin_info = get_student(stud_phone)
        #         return render_template('edit_student.html', student = admin_info)
    else:
        return redirect(url_for('admin_login'))









def edit_student():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'update' in request.form:
                student_info = get_one(student, 'email', session['email'])
                filename = student_info['filename']
                if 'photo' in request.files:
                    file_path = (config["UPLOAD_FOLDER"] + student_info['filename'])
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    image = request.files['photo']
                    if image and image.filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS:
                        filename = secure_filename(image.filename)
                        image.save(os.path.join(config["UPLOAD_FOLDER"], filename))
                new_values = { "$set": {
                        "email": request.form['email'],
                        "name": request.form['full_name'], 
                        "aadhar": request.form['aadhar'],
                        "dob": request.form['dob'],
                        "joining_date": request.form['doj'],
                        "phone" : request.form['phone'],
                        "level": request.form['level'],
                        "school": request.form['school'],
                        "address": request.form['address'],
                        "filename": filename
                        }}
            # add_student(new_values)
            # check = check_data(student, 'email', request.form['email'])
            # if check == 0:
                edit_one(student, 'email', session['email'], new_values)
            # return render_template('s.html', var = session['phone'])
                session['email'] = request.form['email']
                student_info = get_one(student, 'email', session['email'])
                return render_template('edit_student.html', student = student_info)

                # else:
                #     new_values = { "$set": {
                #             "email": request.form['email'],
                #             "name": request.form['full_name'], 
                #             "aadhar": request.form['aadhar'],
                #             "dob": request.form['dob'],
                #             "joining_date": request.form['doj'],
                #             "phone" : request.form['phone'],
                #             "level": request.form['level'],
                #             "school": request.form['school'],
                #             "address": request.form['address']
                #             }}
                # # add_student(new_values)
                # # check = check_data(student, 'email', request.form['email'])
                # # if check == 0:
                #     edit_one(student, 'email', session['email'], new_values)
                # # return render_template('s.html', var = session['phone'])
                #     session['email'] = request.form['email']
                #     student_info = get_one(student, 'email', session['email'])
                #     return render_template('edit_student.html', student = student_info)

            else:
                student_info = get_one(student, 'email', session['email'])
                return render_template('edit_student.html', student = student_info)
                # return render_template('s.html', var = request.form['dob'])
                # student_info = get_student(stud_phone)
                # return render_template('edit_student.html', student = student_info)

        # return render_template('s.html', var = request.form['email'])
        else:
            student_info = get_one(student, 'email', session['email'])
            return render_template('edit_student.html', student = student_info)
        # else:
        #     if stud_phone:
        #         student_info = get_student(stud_phone)
        #         return render_template('edit_student.html', student = student_info)
    else:
        return redirect(url_for('admin_login'))




def student_profile():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'update' in request.form:
                new_values = { "$set": {
                        "email": request.form['email'],
                        "name": request.form['full_name'], 
                        "aadhar": request.form['aadhar'],
                        "dob": request.form['dob'],
                        "joining_date": request.form['doj'],
                        "phone" : request.form['phone'],
                        "level": request.form['level'],
                        "school": request.form['school'],
                        "address": request.form['address']
                        }}
            # add_student(new_values)
                edit_stud(session['user_data'], new_values)
                # return render_template('s.html', var = session['phone'])

                student_info = get_one(student, 'email', request.form['email'])
                session['user_data'] = student_info['email']
                return render_template('student_profile.html', student = student_info)
            else:
                student_info = get_one(student, 'email', session['user_data'])
                return render_template('student_profile.html', student = student_info)
                # return render_template('s.html', var = request.form['dob'])
                # student_info = get_student(stud_phone)
                # return render_template('edit_student.html', student = student_info)

        # return render_template('s.html', var = request.form['email'])
        else:
            student_info = get_one(student, 'email', session['user_data'])
            return render_template('student_profile.html', student = student_info)
        # else:
        #     if stud_phone:
        #         student_info = get_student(stud_phone)
        #         return render_template('edit_student.html', student = student_info)
    else:
        return redirect(url_for('admin_login'))



def change_password():
    if 'user_type' in session:   
        if request.method == "POST":
            if 'change_password' in  request.form:
                match = user_auth(student, session['user_data'], request.form['old_pass'])
                if match == 0:
                    return render_template('change_password.html', msg = "Incorrect Old Password. Try again!")
                elif request.form['new_pass1'] != request.form['new_pass2']:
                    return render_template('change_password.html', msg = "New Passwords do not match. Try again!")
                else:
                    new_values = { "$set": {
                            "password": hash_pass(request.form['new_pass1'])
                            }}

                    edit_stud(session['user_data'], new_values)
                    # return render_template('s.html', var = session['phone'])
                    return render_template('change_password.html', msg = "Password changes Successfully!")
            else:
                return render_template('change_password.html', msg = "")
        else:
            return render_template('change_password.html')
    else:
        return redirect(url_for('student_login'))



def view_franchises():
    if 'user_type' in session:        
        if request.method == "POST":
            if 'franchise_delete' in request.form:
                delete_one(franchise, 'email', request.form['franchise_delete'])
                franchises = get_many(franchise)
                return render_template('view_franch.html', franchises = franchises)
            if 'franchise_edit' in request.form:
                session['email'] = request.form['franchise_edit']
                return redirect(url_for('edit_franchise'))
                # return render_template('s.html', var = request.form['student_edit'])
        else:
            franchises = get_franchs()
            return render_template('view_franch.html', franchises = franchises, msg = session.pop('msg', None))
    else:
        return redirect(url_for('admin_login'))





def add_franchise():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'add' in request.form:
                values = {
                        "_id": (franchise.count_documents({}) + 1),
                        "email": request.form['email'],
                        "allow": True,
                        "password": hash_pass(request.form['password']),
                        "name": request.form['full_name'], 
                        "dir_name": request.form['dir_name'], 
                        "aadhar": request.form['aadhar'],
                        "joining_date": request.form['doj'],
                        "phone" : request.form['phone'],
                        "subject" : request.form['subject'],
                        "address": request.form['address']
                }
                check = check_franch(request.form['email'])
                if check == 0:
                    add_franch(values)
                    return redirect(url_for('view_franchises'))
                else:
                    session['msg'] = "This franchise already exists!"
                    return redirect(url_for('view_franchises'))
                    
            else:
                pass
        else:
            franchises = get_franchs()
            subjects = get_subjects()
            return render_template('add_franch.html', franchises = franchises, subjects = subjects)

    else:
        return render_template('admin_login.html')




def edit_franchise():
    if 'user_type' in session:  
        if request.method == "POST":
            if 'update' in request.form:
                new_values = { "$set": {
                        "email": request.form['email'],
                        "name": request.form['full_name'], 
                        "dir_name": request.form['dir_name'], 
                        "aadhar": request.form['aadhar'],
                        "phone" : request.form['phone'],
                        "address": request.form['address']
                        }}
                # check = check_data(franchise, 'email', request.form['email'])
                # if check == 0:
                edit_franch(session['email'], new_values)
            # return render_template('s.html', var = session['phone'])

                session['email'] = request.form['email']
                franchise_info = get_franch(session['email'])
                return render_template('edit_franch.html', franchise = franchise_info)
                # else:
                #     session['msg'] = "This Franchise already exists"
                #     return redirect(url_for('view_franchises'))


                # add_student(new_values)
                
            else:
                franchise_info = get_franch(session['email'])
                return render_template('edit_franch.html', franchise = franchise_info)
                # return render_template('s.html', var = request.form['dob'])
                # student_info = get_student(stud_phone)
                # return render_template('edit_student.html', student = student_info)

        # return render_template('s.html', var = request.form['email'])
        else:
            franchise_info = get_franch(session['email'])
            return render_template('edit_franch.html', franchise = franchise_info)
        # else:
        #     if stud_phone:
        #         student_info = get_student(stud_phone)
        #         return render_template('edit_student.html', student = student_info)
    else:
        return redirect(url_for('admin_login'))




def logout():
    session.pop('user_type', None)
    session.pop('user_data', None)
    return redirect(url_for('student_login'))
