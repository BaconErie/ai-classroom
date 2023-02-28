from flask import Flask, render_template, request, abort
from hmac import compare_digest
from random import randint
import sqlite3
import hashlib
from datetime import datetime

import classroom_models

app = Flask(__name__)

def is_student(name, birthdate):
    date = int(datetime.strptime(birthdate, '%Y-%m-%d').timestamp())

    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()

    cursor.execute('SELECT hash, salt FROM STUDENT_NAMES WHERE suffix=?', [name[-2:]])
    response = cursor.fetchall()

    for line in response:
        hash_to_match = line[0]
        salt = line[1]

        current_hash = hashlib.sha256(f'{name};{date};{salt}'.encode('utf-8')).hexdigest()

        if hash_to_match == current_hash:
            return True
    
    return False

def check_password(hash, salt, plaintext) -> bool:
    input_hash = hashlib.sha256(f'{plaintext};{salt}'.encode('utf-8')).hexdigest()
    return compare_digest(hash, input_hash)


@app.route('/')
def index():
    return render_template('index.html')

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
        
        if len(request.form['password']) <= 8:
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
        
        return render_template('signup_outcome.html', signup_sucess=True)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login/classroom')
def login_classroom():
    return render_template('login_classroom.html')

@app.route('/login/classroom/api')
def login_api():
    query = request.args.get('search')

    possible_school_systems = classroom_models.SchoolSystem.search_school_systems(query)
    print(possible_school_systems)
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
        
        if not check_password(user.password, user.salt, password):
            return render_template('login_to_classroom.html', school_system=school_system.name, error='Please check your username and password and try again'), 400
        
        return 'signed in [ no token yet :(  ]'

        

if __name__ == '__main__':
    app.run()