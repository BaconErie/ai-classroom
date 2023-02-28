import sqlite3

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
    
    cursor.execute('INSERT INTO STUDENT_NAMES (hash, suffix, salt) VALUES (?, ?, ?)', ('2386002a2071edbb03611e081464f52005e9f990627683bdeff643eaa1955d0f', 'me', '175d4547113bc310e46161f20eff50ccc5c5edd621772d9e7537d25a5b13eacabcd5b6274c5375b8e6baa45dbdd3309a6843036fc98aeb66848335a407320d58'))
    connection.commit()

connection.close()