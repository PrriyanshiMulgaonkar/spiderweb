import sys
import os
# from flask import Flask, redirect, url_for, render_template, request, session
from pymongo import MongoClient
# import json
# import bson.json_util as json_util
# import bcrypt
# import string
from database import *

client = MongoClient('localhost', 27017)
db = client.Exam_portal
student = db.Students
admin = db.Admins
test = db.Tests
subject = db.Subject
franchise = db.Franchise
era = db.ERA
era_q = db.ERA_Questions
question = db.Question
visitor = db.Visitors

def hash_pass(passwd):
    bytes = passwd.encode('utf-8')
    # generating the salt
    salt = bcrypt.gensalt()
    # Hashing the password
    hash = bcrypt.hashpw(bytes, salt)
    return hash


# def chech_hash(passwd, hash):
#     userBytes = passwd.encode('utf-8')
#     # checking password
#     result = bcrypt.checkpw(userBytes, hash)
#     return result

dict = {
    "_id": (student.count_documents({}) + 1),
    "email": "p@gmail.com",
    "name": "Pratik Gajanan Sarkate", 
    "password": hash_pass("stud@123"),
    "aadhar": "456123456489",
    "dob": "28/03/2003",
    "joining_date": "15/09/2020",
    "phone" : "7894561235",
    "franchise" : "Washim Urban",
    "level": "abacus level 1",
    "subject": "Abacus",
    "school": "Noel",
    "address": "Washim"
}
# new_values = { "$set": {
#                         "email": "vaishnavi@gmail.com",
#                         }
#                     }
# dict1 = {
#     "username": "admin", 
#     "password": hash_pass("admin@123")
# }

# edit_stud("7894561235", new_values)

# student.update_one({'phone': "7894561235"}, new_values)

# row = student.find_one({'phone': "7894561235"})
# print(row)
# student.insert_one(dict)
# admin.insert_one(dict1)

# res = student.find_one({'username' : "himanshu"})
# result = chech_hash("him@123", res['password'])
# print(result)

# my = {}
# student_info = {}

# my['UPLOAD_FOLDER'] = "static/uploads/"
# student_info['filename'] = "Diploma_Final_Marksheet.jpeg"
# path = (my["UPLOAD_FOLDER"] + student_info['filename'])
# os.remove(path)
# l = []
# for x in student.find():
#     l.append(x)

# print(l)
count = question.count_documents({'test' : "test 3"})
print(count)
