import views
from flask import Flask

app = Flask(__name__)

app.add_url_rule('/', view_func=views.home)
app.add_url_rule('/student_login', view_func=views.student_login)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)