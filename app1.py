import sys
from flask import Flask, redirect, url_for, render_template, request, session
from pymongo import MongoClient
import pyqrcode
import string
import random

app = Flask(__name__)
app.secret_key = "2iB^2*UB4bntjQnG#kcDGSkNEPNU"

client = MongoClient('localhost', 27017)
db = client.Exam_portal
hc = db.heritage
uc = db.visitors

pi = db.payment_info

# def db_entry(request, month, date, people):
#     heritage = hc.find_one({'name' : request.form['heritage']})
#     exisiting_count = heritage[month][date]
#     uc.insert_one(dict)

#     hc.update_one(
#     { "name": request.form['heritage']  },
#     { "$set": { month + '.'+ str(date) : (exisiting_count + people) }}
#     )
    

# def check_book(request):
#     YMD = request.form['v_date'].split("-")
#     date = int(YMD[2])
#     month = YMD[1]
#     people = int(request.form['v_count'])
#     heritage = hc.find_one({'name' : request.form['heritage']})
#     exisiting_count = heritage[month][date]

#     if (exisiting_count > 300) or ((exisiting_count + people) > 300):
#         return True
#     else:
#         dict = {
#                 "name" : request.form['v_name'],
#                 "email": request.form['v_email'],
#                 "phone": request.form['v_phone'],
#                 "heritage": request.form['heritage'],
#                 "visitors": request.form['v_count'],
#                 "date": request.form['v_date']
#             }
#         db_entry(request, month, date, people)
#         return False



@app.route("/home", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        if request.form['action'] == "book":
    
            # print(dict, file=sys.stderr)


            return redirect(url_for("bookingForm"))

        if request.form['action'] == "search":
            # p_no = request.form.get('no', "08766436534")
           return redirect(url_for("search"))
    else:
        return render_template("index.html")


@app.route("/about", methods=["POST", "GET"])
def about():
    return render_template("about.html")
    

@app.route("/sites", methods=["POST", "GET"])
def sites():
    return render_template("tours.html")


@app.route("/contact", methods=["POST", "GET"])
def contact():
    return render_template("contact.html")


@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "POST":
        p_no    = request.form['v_email']
        history = uc.find({ 'email' : p_no})
        date = session["date"]
        return render_template("history.html", data = history, dt = date)
    else:
        return render_template("search.html", )



@app.route("/payment", methods=["POST", "GET"])
def payment():
    userDict    = session["userDict"]
    month       = session["month"]
    date        = session["date"]
    cost        = session["cost"]
    monument    = session["heritage"]
    totalCount  = session["totalCount"]
    if request.method == "POST":
        res = ''.join(random.choices(string.ascii_letters, k=10))
        dict = {
                "name"      : session["name"],
                "email"     : session["email"],
                "phone"     : session["phone"],
                "heritage"  : session["heritage"],
                "visitors"  : session["visitors"],
                "date"      : session["fullDate"],
                "transactionId"   : res,
                "cost"      : cost
        }

        pi.insert_one(dict)

        # USER ENTRY IN DB 
        uc.insert_one(userDict)

        # UPDATING HERITAGE COLLECTION
        hc.update_one(
        { "name": monument  },
        { "$set": { month + '.'+ str(date) : totalCount }}
        )
        return  redirect(url_for("home"))
    else:
        upi_string = "upi://pay?pa=himanshusangale-1@okicici&pn=HimanshuSangale&am=" + str(cost) + "&tn=Booking_For_" + monument + ""
        qr_url = pyqrcode.create(upi_string)
        qr_url.png("./static/img/pay.png", scale=8)
        return render_template('payment.html')

        

@app.route("/bookingForm", methods=["POST", "GET"])
def bookingForm():
    if request.method == "POST":
        YMD = request.form['v_date'].split("-")
        session["date"]     = int(YMD[2])
        if session["date"] > 25:
            message = "Booking not available for this date!"
            return render_template("booking.html", msg = message)
        session["month"]    = YMD[1]
        monument            = request.form['heritage']
        people              = int(request.form['v_count'])
        h_info              = hc.find_one({'name' : monument})
        exisiting_count     = h_info[session["month"]][session["date"]]
        rate                = h_info['rate']

        session["totalCount"] = exisiting_count + people

        # CALCULATING COST OF VISIT
        session["cost"]     = rate * people

        session["name" ]    = request.form['v_name']
        session["email"]    = request.form['v_email']
        session["phone"]    = request.form['v_phone']
        session["heritage"] = request.form['heritage']
        session["visitors"] = request.form['v_count']
        session["fullDate"] = request.form['v_date']

        if (exisiting_count > 300) or ((exisiting_count + people) > 300):
            message = "Booking full for the Date!"
            return render_template("booking.html", msg = message)
        else:
            dict = {
                "name"      : session["name"],
                "email"     : session["email"],
                "phone"     : session["phone"],
                "heritage"  : session["heritage"],
                "visitors"  : session["visitors"],
                "date"      : session["fullDate"]
            }
            session["userDict"] = dict
            print(session["date"], file=sys.stderr)
            

            return redirect(url_for("payment"))
            # , userDict = dict, month = month, date = date, count = (exisiting_count + people), rate = rate, monument = monument)

        # uc.insert_one(dict)

        # hc.update_one(
        # { "name": request.form['heritage']  },
        # { "$set": { month + '.'+ str(date) : (exisiting_count + people) }}
        # )

        # dict = {
        #     "name" : "Taj Mahal",
        #     "01": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        #     "02": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        #     "03": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        #     "04": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        #     "05": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        #     "06": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        #     "07": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        #     "08": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        #     "09": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        #     "10": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        #     "11": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        #     "12": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        # }
        # hc.insert_one(dict)

        # f = hc.find_one()

        # DEBUG-----------------------
        # print(month, file=sys.stderr)
        # ----------------------------
       
        # return "Successful" 
    else:
        return render_template('booking.html')


if __name__ == "__main__":
    app.run(debug=True)
