from flask import Flask, render_template
from random import randint

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login/classroom')
def login_classroom():
    return render_template('login_classroom.html')

@app.route('/login/classroom/api')
def login_api():
    return {str(randint(1,19)): 'id'}

@app.route('/login/classroom/<classroom_public_id>')
def login_to_classroom(classroom_public_id):
    return render_template('login_to_classroom.html', school_system='Proxy County Public Schools')

if __name__ == '__main__':
    app.run()