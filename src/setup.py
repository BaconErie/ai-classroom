import sqlite3
import classroom_models
import secrets
import hashlib

DEFAULT_LIST = [
]

# Setup

connection = sqlite3.connect('data.db')
cursor = connection.cursor()

# Create table for Open accounts

response = cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'open_users\';')

if response.fetchone() is None:
    cursor.execute('CREATE TABLE open_users (id INTEGER PRIMARY KEY, email TEXT, name TEXT, password TEXT, salt TEXT);')

# Create table for Classroom accounts

response = cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'classroom_users\';')

if response.fetchone() is None:
    cursor.execute('CREATE TABLE classroom_users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, name TEXT, password TEXT, salt TEXT, school_system_id INTEGER, teacher BOOLEAN);')

# Create table for chat logs

response = cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'chat_logs\';')

if response.fetchone() is None:
    cursor.execute('CREATE TABLE chat_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, prompt TEXT, response TEXT, date INTEGER, session_id INTEGER)')

# Create table for open_chat_sessions

response = cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'open_chat_sessions\';')

if response.fetchone() is None:
    cursor.execute('CREATE TABLE open_chat_sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, user_id INTEGER)')




####################
# CLASSROOM TABLES #
####################

# school_systems #
# Keeps track of: id of school system, name

response = cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'school_systems\';')

if response.fetchone() is None:
    cursor.execute('CREATE TABLE school_systems (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)')

# main_classroom_table #
# Keeps id of classroom, teacher_id, name, join_code, school_system_id, is_chat_allowed, is_logs_allowed

response = cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'main_classroom_table\';')

if response.fetchone() is None:
    cursor.execute('CREATE TABLE main_classroom_table (id INTEGER PRIMARY KEY AUTOINCREMENT, teacher_id INTEGER, name TEXT, join_code INTEGER, school_system_id INTEGER, is_chat_allowed BOOLEAN, is_logs_allowed BOOLEAN)')

# classroom_students #
# Links student_ids to classroom_ids

response = cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'classroom_students\';')

if response.fetchone() is None:
    cursor.execute('CREATE TABLE classroom_students (classroom_id INTEGER, student_id INTEGER);')

# Create table for classroom_chat_sessions

response = cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'classroom_chat_sessions\';')

if response.fetchone() is None:
    cursor.execute('CREATE TABLE classroom_chat_sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, user_id INTEGER, classroom_id INTEGER)')





response = cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'STUDENT_NAMES\';')

if response.fetchone() is None:
    cursor.execute('CREATE TABLE STUDENT_NAMES (id INTEGER PRIMARY KEY AUTOINCREMENT, hash TEXT, suffix TEXT, salt TEXT);') # Hash will be: Name;Date;Salt in unix time
    
    salt = secrets.token_hex(256)

    string = f'Demo Name;946702800;{salt}'

    hash = hashlib.sha256(string.encode('utf-8')).hexdigest()

    cursor.execute('INSERT INTO STUDENT_NAMES (hash, suffix, salt) VALUES (?, ?, ?)', (hash, 'me', salt))
    connection.commit()

connection.close()





#####################
# SETUP THE CLASSES #
#####################

if __name__ == '__main__':
    # Create two demo school systems
    demo_schools = classroom_models.SchoolSystem.create_school_system('Demo County Public Schools')
    classroom_models.SchoolSystem.create_school_system('Denham School District')

    # Create a demo teacher
    teacher = classroom_models.ClassroomUser.create_user('teacher@demo.edu', 'Teacher Name', 'password', demo_schools, True)

    # Create a demo classroom
    classroom = classroom_models.Classroom.create_classroom(teacher, 'Demo English Classroom', demo_schools)

    # Create a demo student
    student = classroom_models.ClassroomUser.create_user('student@demo.edu', 'Student Name', 'password', demo_schools, False)