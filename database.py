import sys
from flask import Flask, redirect, url_for, render_template, request, session
from pymongo import MongoClient
import json
import bson.json_util as json_util
import bcrypt
import string
import time

client = MongoClient('mongodb://localhost:27017/Exam_portal')
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

def delete_visitors():
    visitor.delete_many({})


def get_student(email):
    myquery = { "email": email }
    stud = student.find_one(myquery)
    return stud

def edit_stud(email, new_values):
    myquery = { "email": email }
    student.update_one(myquery, new_values)


def add_stud(values):
    res = student.insert_one(values)
    return res

def check_stud(email):
    user = get_student(email)
    if user:
        return 1
    else:
        return 0


def get_franchs():
    franchise_list = []
    for franch in franchise.find():
        franchise_list.append(franch)
    return franchise_list


def get_franch(email):
    myquery = { "email": email }
    stud = franchise.find_one(myquery)
    return stud


def add_franch(values):
    res = franchise.insert_one(values)
    return res


def edit_franch(email, new_values):
    myquery = { "email": email }
    franchise.update_one(myquery, new_values)


def check_franch(email):
    user = get_franch(email)
    if user:
        return 1
    else:
        return 0



def get_subjects():
    subject_list = []
    for sub in subject.find():
        subject_list.append(sub)
    return subject_list


def get_tests():
    test_list = []
    for tst in test.find():
        test_list.append(tst)
    return test_list


def get_subjects():
    subject_list = []
    for sub in subject.find():
        subject_list.append(sub)
    return subject_list



def delete_subject(name):
    myquery = { "name": name }
    subject.delete_one(myquery)

def get_many(type, id=None, name=None):
    data_list = []
    if id == None or name == None:
        for row in type.find():
            data_list.append(row)
        return data_list
    else:
        for row in type.find({id : name}):
            data_list.append(row)
        return data_list
    

def delete_one(type, id, name):
    myquery = { id : name }
    if type == franchise:
        student.delete_many({'franchise': name})
    if type == era:
        era_q.delete_many({'era': name})
    if type == test:
        question.delete_many({'test': name})
        era.delete_many({'test': name})
        era_q.delete_many({'test': name})
    if type == subject:
        tests = get_many(test, 'subject', name)
        for t in tests:
            question.delete_many({'test': t['name']})
            era.delete_many({'test': t['name']})
            era_q.delete_many({'test': t['name']})
        test.delete_many({'subject' : name})
    # if type == question:
    #         t = get_one(question,'name', name)
    #         e = get_one(test, 'name', t['test'])
    #         total = e['total_question'] - 1
    #         new_data = { "$set": {
    #                             "total_question" : total
    #                     }}
    #         edit_one(test, 'name', t['test'], new_data)
    # if type == era_q:
    #     t = get_one(era_q,'name', name)
    #     e = get_one(era, 'name', t['era'])
    #     total = e['total_question'] - 1
    #     new_data = { "$set": {
    #                         "total_question" : total
    #                 }}
    #     edit_one(era, 'name', t['era'], new_data)

    type.delete_one(myquery)



def get_one(type, id, name):
    myquery = { id: name }
    data = type.find_one(myquery)
    return data

def edit_one(type, id, name, new_values):
    myquery = { id: name }
    type.update_one(myquery, new_values)


def add_one(type, values):
    type.insert_one(values)
    # if type == question:
    #     t = get_one(test,'name', values['test'])
    #     total = int(t['total_question']) + 1
    #     new_data = { "$set": {
    #                         "total_question" : total
    #                 }}
    #     edit_one(test, 'name', values['test'], new_data)
    # if type == era_q:
    #     t = get_one(era,'name', values['era'])
    #     total = int(t['total_question']) + 1
    #     new_data = { "$set": {
    #                         "total_question" : total
    #                 }}
    #     edit_one(era, 'name', values['era'], new_data)


def check_data(type, id, name):
    data = get_one(type, id, name)
    if data:
        # Data exists
        return 1
    else:
        # Data does not exists
        return 0


def check_quiz(email, id ,name):
    data = get_one(student, 'email', email)
    if id in data:
        q = data[id]
        if name in q:
            return 1
        else:
            return 0
    else:
        return 0

def store_quiz(email, id, score):
    data = get_one(student, 'email', email)
    if id in data:
        # Updating Dict
        new_data = { "$set": {
                            id: score
                            # test: score
                    }}
    else:
        new_data = { "$set": {
                        id: score
                        # test: score
                }}
    edit_one(student, 'email',email, new_data)


def check_answers(type ,name, answer):
    q = get_one(type, 'name', name)
    if q['answer'] == answer:
        return 1
    else:
        return 0

def set_allow(email):
    stud = get_one(student, 'email', email)
    if stud['allow'] == 'Allowed':
        arg = 'Not Allowed'
    else:
        arg = 'Allowed'
    new_data = { "$set": {
                            'allow': arg
                    }}
    edit_one(student, 'email', email, new_data)



# d = {
#     "quiz15" : "12"
# }
# data1 = { "$set": {
#                     "quiz": d
#                 }}

# edit_one(student, 'email','himanshu@gmail.com', data1)

# data = get_one(student, 'email', 'himanshu@gmail.com')
# q = data['quiz']
# for i in q:
#     print(i)
#     print(q[i])
