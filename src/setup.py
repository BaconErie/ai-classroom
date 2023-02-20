import sqlite3

connection = sqlite3.connect('data.db')
cursor = connection.cursor()

response = cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'open_users\';')

if response.fetchone() is None:
    cursor.execute('CREATE TABLE open_users (id INTEGER PRIMARY KEY, email TEXT, name TEXT, password TEXT, salt TEXT);')


response = cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'classroom_users\';')

if response.fetchone() is None:
    cursor.execute('CREATE TABLE classroom_users (id INTEGER PRIMARY KEY, email TEXT, name TEXT, password TEXT, salt TEXT, school_system_id INTEGER);')

if response.fetchppoojppjpojpoijpopoj poj poj poij poij poi jopijoij  jijiiii  ioipoij   