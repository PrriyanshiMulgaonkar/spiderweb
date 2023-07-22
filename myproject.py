from flask import Flask, redirect, url_for, render_template, request, session, Response
from database import *
from views import *
import threading

app = Flask(__name__)
app.secret_key = "2iB^2*UB4bntjQnG#kcDGSkNEPNU"
app.config["MONGO_URI"] = "mongodb://localhost:27017/Exam_portal"


def auto_delete_docs():
    # Wait for one day
    time.sleep(24 * 60 * 60)
    # Delete all documents in the collection
    visitor.delete_many({})

def start_background_task():
    thread = threading.Thread(target=auto_delete_docs)
    thread.start()

@app.before_first_request
def before_first_request():
    start_background_task()

app.add_url_rule('/timer', view_func=timer, methods = ["GET", "POST"])
app.add_url_rule('/', view_func=home, methods = ["GET", "POST"])
app.add_url_rule('/home', view_func=home, methods = ["GET", "POST"])
app.add_url_rule('/student_login', view_func=student_login, methods = ["GET", "POST"])
app.add_url_rule('/franchise_login', view_func=franch_login, methods = ["GET", "POST"])
app.add_url_rule('/admin_login', view_func=admin_login, methods = ["GET", "POST"])
app.add_url_rule('/show_home', view_func=show_home, methods = ["GET", "POST"])
app.add_url_rule('/view_tests', view_func=view_tests, methods = ["GET", "POST"])
app.add_url_rule('/choose_era', view_func=choose_era, methods = ["GET", "POST"])
app.add_url_rule('/take_quiz', view_func=take_quiz, methods = ["GET", "POST"])
app.add_url_rule('/choose_exam', view_func=choose_exam, methods = ["GET", "POST"])
app.add_url_rule('/take_exam', view_func=take_exam, methods = ["GET", "POST"])
app.add_url_rule('/submit_exam', view_func=submit_exam, methods = ["GET", "POST"])
app.add_url_rule('/submit_quiz', view_func=submit_quiz, methods = ["GET", "POST"])
app.add_url_rule('/era_status', view_func=era_status, methods = ["GET", "POST"])
app.add_url_rule('/exam_result', view_func=exam_result, methods = ["GET", "POST"])
app.add_url_rule('/student_results', view_func=student_results, methods = ["GET", "POST"])
app.add_url_rule('/student_results_era', view_func=student_results_era, methods = ["GET", "POST"])
app.add_url_rule('/student_result', view_func=student_result, methods = ["GET", "POST"])
app.add_url_rule('/edit_test', view_func=edit_test, methods = ["GET", "POST"])
app.add_url_rule('/view_test_questions', view_func=view_test_questions, methods = ["GET", "POST"])
app.add_url_rule('/view_subjects', view_func=view_subjects, methods = ["GET", "POST"])
app.add_url_rule('/edit_subject', view_func=edit_subject, methods = ["GET", "POST"])
app.add_url_rule('/add_test', view_func=add_test, methods = ["GET", "POST"])
app.add_url_rule('/add_test_question', view_func=add_test_question, methods = ["GET", "POST"])
app.add_url_rule('/add_subject', view_func=add_subject, methods = ["GET", "POST"])
app.add_url_rule('/view_era', view_func=view_era, methods = ["GET", "POST"])
app.add_url_rule('/view_era_questions', view_func=view_era_question, methods = ["GET", "POST"])
app.add_url_rule('/edit_era_question', view_func=edit_era_question, methods = ["GET", "POST"])
app.add_url_rule('/add_era_question', view_func=add_era_question, methods = ["GET", "POST"])
app.add_url_rule('/add_era', view_func=add_era, methods = ["GET", "POST"])
app.add_url_rule('/edit_era', view_func=edit_era, methods = ["GET", "POST"])
app.add_url_rule('/era_result', view_func=era_result, methods = ["GET", "POST"])
app.add_url_rule('/student_home', view_func=student_home, methods = ["GET", "POST"])
app.add_url_rule('/get_hallticket', view_func=get_hallticket, methods = ["GET", "POST"])
app.add_url_rule('/franch_home', view_func=franch_home, methods = ["GET", "POST"])
app.add_url_rule('/franch_view_students', view_func=franch_view_students, methods = ["GET", "POST"])
app.add_url_rule('/edit_franch_student', view_func=edit_franch_student, methods = ["GET", "POST"])
app.add_url_rule('/franch_profile', view_func=franch_profile, methods = ["GET", "POST"])
app.add_url_rule('/admin_home', view_func=admin_home, methods = ["GET", "POST"])
app.add_url_rule('/view_students', view_func=view_students, methods = ["GET", "POST"])
app.add_url_rule('/add_student', view_func=add_student, methods = ["GET", "POST"])
app.add_url_rule('/franch_add_student', view_func=franch_add_student, methods = ["GET", "POST"])
app.add_url_rule('/admin_profile', view_func=admin_profile, methods = ["GET", "POST"])
app.add_url_rule('/edit_student', view_func=edit_student, methods = ["GET", "POST"])
app.add_url_rule('/student_profile', view_func=student_profile, methods = ["GET", "POST"])
app.add_url_rule('/change_password', view_func=change_password, methods = ["GET", "POST"])
app.add_url_rule('/view_franchises', view_func=view_franchises, methods = ["GET", "POST"])
app.add_url_rule('/add_franchise', view_func=add_franchise, methods = ["GET", "POST"])
app.add_url_rule('/edit_franchise', view_func=edit_franchise, methods = ["GET", "POST"])
app.add_url_rule('/logout', view_func=logout, methods = ["GET", "POST"])



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
