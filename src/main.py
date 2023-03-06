from flask import Flask, render_template, request, abort, make_response, redirect
from hmac import compare_digest
from random import randint
import sqlite3
import hashlib
import jwt
import os
from datetime import datetime

import classroom_models
import open_models

JWT_SECRET = os.environ['JWT_SECRET']

app = Flask(__name__)

def is_student(name, birthdate):
    print(name)
    date = int(datetime.strptime(birthdate, '%Y-%m-%d').timestamp())

    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()

    print(name[-2:])

    cursor.execute('SELECT hash, salt FROM STUDENT_NAMES WHERE suffix=?', [name[-2:]])
    response = cursor.fetchall()

    for line in response:
        hash_to_match = line[0]
        salt = line[1]
        print('sa,t', salt)
        

        print('curr tn date', date)
        current_hash = hashlib.sha256(f'{name};{date};{salt}'.encode('utf-8')).hexdigest()
        print(current_hash)
        print(hash_to_match)
        if compare_digest(current_hash, hash_to_match):
            return True
    
    return False

def check_password(hash, salt, plaintext) -> bool:
    input_hash = hashlib.sha256(f'{plaintext};{salt}'.encode('utf-8')).hexdigest()
    return compare_digest(hash, input_hash)


def generate_token(id: int, is_open: bool):
    return jwt.encode({'id': id, 'is_open': is_open}, JWT_SECRET, algorithm='HS256')

def get_id_from_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])['id']
    except:
        return None

def is_open_from_token(token):
    try:
        print(jwt.decode(token, JWT_SECRET, algorithms=['HS256'])['is_open'])
        return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])['is_open']
    except:
        return None

def get_user_from_token(token):
    if token is None:
        return None

    id = get_id_from_token(token)
    is_open = is_open_from_token(token)
    if id is None or is_open is None:
        return None
    
    if is_open:
        return open_models.OpenUser.get_user_by_id(id)
    else:
        return classroom_models.ClassroomUser.get_user_by_id(id)

@app.route('/')
def index():
    user = get_user_from_token(request.cookies.get('token'))

    if user is not None:
        return redirect('/home')

    return render_template('index.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        user = get_user_from_token(request.cookies.get('token'))
        print(user.name, type(user))
        if user is None:
            return redirect('/')    
        
        if type(user) == classroom_models.ClassroomUser:
            classroom_names = {}
            classroom_objects = user.get_classrooms()
            
            
            if classroom_objects is not None:
                for classroom in classroom_objects:
                    classroom_names[classroom.name] = classroom.id
            
            if len(classroom_names) == 0:
                classroom_names = None
            print('100 main', classroom_names)
            return render_template('home.html', is_open=False, is_teacher=user.is_teacher, classroom_names=classroom_names)
        
        elif type(user) == open_models.OpenUser:
            chat_session_names = {}
            chat_session_objects = user.get_chat_sessions()
            
            if chat_session_objects is not None:
                for chat_session in chat_session_objects:
                    chat_session_names[chat_session.name] = chat_session.id
            
            if len(chat_session_names) == 0:
                chat_session_names = None
            
            return render_template('home.html', is_open=True, chat_session_names=chat_session_names)
    elif request.method == 'POST':
        user = get_user_from_token(request.cookies.get('token'))

        if user is None:
            return redirect('/')
        
        if type(user) == classroom_models.ClassroomUser:
            if user.is_teacher:
                name = request.form['classroom_name']

                new_classroom = classroom_models.Classroom.create_classroom(user, name, user.school_system)

                return redirect(f'/classroom/{new_classroom.id}')
            
            else:
                join_code = request.form['join_code']

                classroom = classroom_models.Classroom.get_classroom_by_join_code(join_code)

                classroom.add_student(user)

                return redirect(f'/classroom/{classroom.id}')
            
        elif type(user) == open_models.OpenUser:
            session_name = request.form['name']

            new_session = user.create_chat_session(session_name)

            return redirect(f'/chat/{new_session.id}')

@app.route('/signup', methods=['GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

@app.route('/signup/open', methods=['GET', 'POST'])
def signup_open():
    if request.method == 'GET':
        return render_template('signup_open.html')
    
    elif request.method == 'POST':
        if request.form['fname'] == '' or request.form['lname'] == '':
            return render_template('signup_open.html', error='First name and last name must be filled in'), 400
        
        if request.form['email'] == '':
            return render_template('signup_open.html', error='Please enter an email.'), 400
        
        if request.form['bday'] == '':
            return render_template('signup_open.html', error='Please enter a birthdate.'), 400
        
        if len(request.form['password']) < 8:
            return render_template('signup_open.html', error='Please enter a password that is at least 8 characters long.'), 400
        
        if request.form['id'] == '':
            return render_template('signup_open.html', error='Please submit an image of an ID.'), 400
        
        fname = request.form['fname']
        mname = request.form['mname']
        lname = request.form['lname']

        if request.form['mname'] != '':
            if is_student(f'{fname} {mname} {lname}', request.form['bday']):
                return render_template('signup_outcome.html', signup_sucess=False)
        else:
            if is_student(f'{fname} {lname}', request.form['bday']):
                return render_template('signup_outcome.html', signup_sucess=False)
        
        full_name = None
        if mname is not None:
            full_name = f'{fname} {mname} {lname}'
        else:
            full_name = f'{fname} {lname}'

        open_models.OpenUser.create_user(request.form['email'], full_name, request.form['password'])        
        return render_template('signup_outcome.html', signup_sucess=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == '':
            return render_template('login.html', error='Please enter an email'), 400
    
        if password == '':
            return render_template('login.html', error='Please enter your password'), 400

        user = open_models.OpenUser.get_user_by_email(email)

        if user is None:
            return render_template('login.html', error='Please check your username and password and try again'), 400
        
        if not check_password(user.password, user.salt, password):
            return render_template('login.html', error='Please check your username and password and try again'), 400
        
        response = make_response(redirect('/home'))
        response.set_cookie('token', generate_token(user.id, True))

        return response

@app.route('/login/classroom')
def login_classroom():
    return render_template('login_classroom.html')

@app.route('/login/classroom/api')
def login_api():
    query = request.args.get('search')

    possible_school_systems = classroom_models.SchoolSystem.search_school_systems(query)
    response_dict = {}

    for school_system in possible_school_systems:
        response_dict[school_system.name] = school_system.id

    return response_dict

@app.route('/login/classroom/<classroom_public_id>', methods=['GET', 'POST'])
def login_to_classroom(classroom_public_id):
    if request.method == 'GET':
        school_system = classroom_models.SchoolSystem.get_school_system_by_id(classroom_public_id)

        if school_system is None:
            abort(404, 'Classroom not found')

        return render_template('login_to_classroom.html', school_system=school_system.name)


    elif request.method == 'POST':
        school_system = classroom_models.SchoolSystem.get_school_system_by_id(classroom_public_id)
        email = request.form['email']
        password = request.form['password']

        if school_system is None:
            abort(404, 'Classroom not found')

        if email == '':
            return render_template('login_to_classroom.html', school_system=school_system.name, error='Please enter an email'), 400
    
        if password == '':
            return render_template('login_to_classroom.html', school_system=school_system.name, error='Please enter your password'), 400

        user = classroom_models.ClassroomUser.get_user_by_email(email)

        if user is None:
            return render_template('login_to_classroom.html', school_system=school_system.name, error='Please check your username and password and try again'), 400

        if user.school_system.id != school_system.id:
            return render_template('login_to_classroom.html', school_system=school_system.name, error='Please check your username and password and try again'), 400
        
        if not check_password(user.password, user.salt, password):
            return render_template('login_to_classroom.html', school_system=school_system.name, error='Please check your username and password and try again'), 400
        
        response = make_response(redirect('/home'))
        response.set_cookie('token', generate_token(user.id, False))

        return response
    
@app.route('/classroom/<classroom_id>')
def classroom(classroom_id):
    classroom = classroom_models.Classroom.get_classroom_by_id(classroom_id)
    user = get_user_from_token(request.cookies.get('token'))

    if user is None:
        return redirect('/')

    if classroom is None:
        abort(404)
    
    if user.is_teacher and classroom.teacher.id == user.id:
        student_names = {}
        for student in classroom.get_students():
            student_names[student.name] = student.id
        
        if len(student_names) == 0:
            student_names = None

        return render_template('classroom_teacher.html', join_code=classroom.join_code, student_names=student_names, classroom_name=classroom.name, chat_allowed=classroom.is_chat_allowed(), logs_allowed=classroom.is_logs_allowed(), classroom_id=classroom_id)

    elif classroom.is_student_in_classroom(user):
        logs = {}
        
        if classroom.is_logs_allowed():
            students_chat_session = user.get_chat_sessions_by_classroom(classroom)
            if students_chat_session is not None:
                for entry in students_chat_session.get_logs():
                    logs[entry.prompt] = entry.response

            return render_template('classroom_student.html', classroom_name=classroom.name, logs_allowed=True, chat_allowed=classroom.is_chat_allowed(), logs=logs)
        else:
            return render_template('classroom_student.html', classroom_name=classroom.name, logs_allowed=False, chat_allowed=classroom.is_chat_allowed())
    
    else:
        abort(403)

@app.route('/classroom/<classroom_id>/api', methods=['POST'])
def classroom_say(classroom_id):
    classroom = classroom_models.Classroom.get_classroom_by_id(classroom_id)
    user = get_user_from_token(request.cookies.get('token'))

    if user is None:
        return redirect('/')

    if classroom is None:
        abort(404)
    
    if classroom.is_student_in_classroom(user) == False:
        abort(403)
    
    if classroom.is_chat_allowed() == False:
        abort(400)

    entry = user.get_chat_sessions_by_classroom(classroom).say(request.data.decode('utf-8'))

    return entry.response

@app.route('/classroom/<classroom_id>/settings', methods=['POST'])
def classroom_settings(classroom_id):
    classroom = classroom_models.Classroom.get_classroom_by_id(classroom_id)
    user = get_user_from_token(request.cookies.get('token'))

    if user is None:
        return redirect('/')

    if classroom is None:
        abort(404)
    
    if classroom.teacher.id != user.id:
        abort(403)
    
    json = request.get_json()
    print(json)

    allow_chat = json['chat']
    allow_logs = json['logs']

    classroom.set_chat_allowed(allow_chat)
    classroom.set_logs_allowed(allow_logs)

    return 'OK', 200

@app.route('/classroom/<classroom_id>/view/<student_id>')
def view_student(classroom_id, student_id):
    classroom = classroom_models.Classroom.get_classroom_by_id(classroom_id)
    user = get_user_from_token(request.cookies.get('token'))
    student = classroom_models.ClassroomUser.get_user_by_id(student_id)

    if user is None:
        return redirect('/')

    if classroom is None:
        abort(404)
    
    if classroom.teacher.id != user.id:
        abort(403)
    
    if student is None or classroom.is_student_in_classroom(student) == False:
        abort(404)
    
    logs = {}

    for entry in student.get_chat_sessions_by_classroom(classroom).get_logs():
        logs[entry.prompt] = entry.response
    
    return render_template('view.html', logs=logs, classroom_name=classroom.name, student_name=student.name, )

@app.route('/logout')
def logout():
    response = make_response(redirect('/'))
    response.set_cookie('token', '', expires=0)

    return response

@app.route('/chat/<chat_id>')
def chat(chat_id):
    chat_id = int(chat_id)
    user = get_user_from_token(request.cookies.get('token'))

    if user is None:
        return redirect('/')
    
    chat_sessions = user.get_chat_sessions()

    correct_chat_session = None

    for chat_session in chat_sessions:
        if chat_session.id == chat_id:
            correct_chat_session = chat_session
            break

    if correct_chat_session is None:
        abort(404)
    
    logs = {}
    
    for entry in correct_chat_session.get_logs():
        logs[entry.prompt] = entry.response

    return render_template('open_chat.html', chat_session_name=correct_chat_session.name, logs=logs)

@app.route('/chat/<chat_session_id>/api', methods=['POST'])
def chat_say(chat_session_id):
    chat_session_id = int(chat_session_id)

    user = get_user_from_token(request.cookies.get('token'))

    if user is None:
        return redirect('/')
    
    chat_sessions = user.get_chat_sessions()

    correct_chat_session = None

    for chat_session in chat_sessions:
        if chat_session.id == chat_session_id:
            correct_chat_session = chat_session
            break

    if correct_chat_session is None:
        abort(404)

    entry = correct_chat_session.say(request.data.decode('utf-8'))

    return entry.response

if __name__ == '__main__':
    app.run()