from __future__ import annotations
from random import randint
import sqlite3
from open_models import ChatLogEntry
from datetime import datetime, timezone
import secrets
import hashlib
import ai

class SchoolSystem:
    def get_school_system_by_id(id: int) -> SchoolSystem | None:
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('SELECT name FROM school_systems WHERE id=?', [id])
        response = cursor.fetchone()

        connection.close()

        if response is None:
            return None

        name = response[0]

        return SchoolSystem(id, name)
    
    def create_school_system(name: str) -> SchoolSystem:
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('INSERT INTO school_systems (name) VALUES (?)', [name])
        
        connection.commit()
        
        cursor.execute('SELECT LAST_INSERT_ROWID();')
        id = cursor.fetchone()[0]

        connection.close()

        return SchoolSystem(id, name)
    
    def search_school_systems(name: str) -> List[SchoolSystem]:
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('SELECT id FROM school_systems WHERE name LIKE ?', [f'{name}%'])

        response = cursor.fetchall()

        connection.close()

        school_systems = []

        print(response, name)

        for line in response:
            id = line[0]
            school_systems.append(SchoolSystem.get_school_system_by_id(id))

        return school_systems


    def __init__(self, id, name):
        self.id = id
        self.name = name


class Classroom:
    # CLASS METHODS #

    def get_classroom_by_id(id) -> Classroom | None:
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('SELECT teacher_id, name, join_code, school_system_id FROM main_classroom_table WHERE id=?', [id])
        response = cursor.fetchone()

        connection.close()

        if response is None:
            return None

        teacher = response[0]
        name = response[1]
        join_code = response[2]
        school_system_id = response[3]
        school_system = SchoolSystem.get_school_system_by_id(school_system_id)

        return Classroom(id, teacher, name, join_code, school_system)
        
    def get_classroom_by_join_code(join_code) -> Classroom | None:
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('SELECT id, teacher_id, name, school_system_id FROM main_classroom_table WHERE join_code=?', [join_code])
        response = cursor.fetchone()

        connection.close()

        if response is None:
            return None

        id = response[0]
        teacher = response[1]
        name = response[2]
        school_system_id = response[3]
        school_system = SchoolSystem.get_school_system_by_id(school_system_id)

        return Classroom(id, teacher, name, join_code, school_system)

    def create_classroom(teacher: ClassroomUser, name: str, school_system: SchoolSystem) -> Classroom:
        if not teacher.is_teacher:
            raise UserIsNotATeacher('Create classroom')

        # Generate a unique join code
        join_code = None
        not_unique = True

        while not_unique:
            join_code = randint(1, 999_999_999)

            if Classroom.get_classroom_by_join_code(join_code) is None:
                not_unique = False
                break
        
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('INSERT INTO main_classroom_table (teacher_id, name, join_code, school_system_id, is_chat_allowed, is_logs_allowed) VALUES (?, ?, ?, ?, TRUE, TRUE)', [teacher.id, name, join_code, school_system.id])
        connection.commit()

        cursor.execute('SELECT LAST_INSERT_ROWID();')
        id = cursor.fetchone()[0]
        
        connection.close()

        return Classroom(id, teacher, name, join_code, school_system)

    
    # INSTANCE METHODS #
    def __init__(self, id: int, teacher: ClassroomUser, name: str, join_code: int, school_system: SchoolSystem):
        self.id = id
        self.teacher = teacher
        self.name = name
        self.join_code = join_code
        self.school_system = school_system

    def get_students(self) -> List[ClassroomUser]:
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('SELECT student_id FROM classroom_students WHERE classroom_id=?', [self.id])
        response = cursor.fetchall()

        connection.close()

        students = []

        for line in response:
            student_id = line[0]

            students.append(ClassroomUser.get_user_by_id(student_id))
        
        return students
    
    def add_student(self, student: ClassroomUser) -> None:
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('INSERT INTO classroom_students (classroom_id, student_id) VALUES (?, ?)', [self.id, student.id])
        
        connection.commit()
        connection.close()

    def is_chat_allowed(self) -> bool:
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('SELECT is_chat_allowed FROM main_classroom_table WHERE classroom_id=?', [self.id])
        response = cursor.fetchone()

        connection.close()

        return response[0]
    
    def is_logs_allowed(self) -> bool:
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('SELECT is_log_allowed FROM main_classroom_table WHERE classroom_id=?', [self.id])
        response = cursor.fetchone()

        connection.close()

        return response[0]


class ClassroomUser:
    # CLASS METHODS #

    def get_user_by_id(id: int):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM classroom_users WHERE id=?', [id])
        response = cursor.fetchone()

        connection.close()

        if response is None:
            return None

        return ClassroomUser(response[0], response[1], response[2], response[3], response[4], SchoolSystem.get_school_system_by_id(response[5]), response[6])
    
    def get_user_by_email(email: str):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM classroom_users WHERE email=?', [email])
        response = cursor.fetchone()

        connection.close()

        if response is None:
            return None

        return ClassroomUser(response[0], response[1], response[2], response[3], response[4], SchoolSystem.get_school_system_by_id(response[5]), response[6])

    def create_user(email: str, name, password, school_system, is_teacher):
        if ClassroomUser.get_user_by_email(email) is not None:
            raise ClassroomUserAlreadyExistsException(email)


        # PASSWORD HASHING #

        # Generate salt
        salt = secrets.token_hex(64)

        # Hash password
        hashed_password = hashlib.sha256(f'{password};{salt}'.encode('utf-8')).hexdigest()

        # INSERT DATA INTO DATABASE #
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('INSERT INTO classroom_users (email, name, password, salt, school_system_id, teacher) VALUES (?, ?, ?, ?, ?, ?)', [email, name, hashed_password, salt, school_system.id, is_teacher])
        connection.commit()

        cursor.execute('SELECT id FROM classroom_users WHERE email=?', [email])
        id = cursor.fetchone()[0]

        connection.close()

        return ClassroomUser(id, email, name, hashed_password, salt, school_system, is_teacher)

    # INSTANCE METHODS #

    def __init__(self, id, email, name, password, salt, school_system, is_teacher):
        '''NOTE: This function should NOT be called directly. Please use the create_user classmethod'''
        self.id = id
        self.email = email
        self.name = name
        self.password = password
        self.salt = salt
        self.school_system = school_system
        self.is_teacher = is_teacher

    def get_chat_sessions_by_classroom(self, classroom: Classroom) -> ClassroomChatSession | None:
        # There should only be one chat session by each student, so no need to fetchall and stuff

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('SELECT id, name FROM classroom_chat_sessions WHERE user_id=? AND classroom_id=?', [self.id, classroom.id])
        response = cursor.fetchone()

        connection.close()

        if response is None:
            return None

        return ClassroomChatSession(response[0], response[1], self, classroom)
    
    def create_chat_session(self, name, classroom):
        if not classroom.is_chat_allowed():
            raise ChatNotAllowed()

        possible_chat_sessions = self.get_chat_sessions_by_classroom()
        if not self.is_teacher and possible_chat_sessions is not None:
            raise StudentAlreadyHasSession(self, possible_chat_sessions[0])

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('INSERT INTO classroom_chat_sessions (name, user_id) VALUES (?, ?)', [name, self.id])
        connection.commit()

        cursor.execute('SELECT LAST_INSERT_ROWID();')
        id = cursor.fetchone()[0]

        connection.close()

        return ClassroomChatSession(id, name, self, classroom)
    
    def get_classrooms(self) -> List[Classroom] | None:
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        if self.is_teacher:
            cursor.execute('SELECT id FROM main_classroom_table WHERE teacher_id=?', [self.id]) # For those who might want to repurpose this code in the future, this is a good indication that I should've made a seperate class for teachers. - BaconErie
        else:
            cursor.execute('SELECT classroom_id FROM classroom_students WHERE student_id=?', [self.id])

        response = cursor.fetchall()

        if len(response) == 0:
            return None

        classrooms = []

        for line in response:
            classroom_id = line[0]
            classrooms.append(Classroom.get_classroom_by_id(classroom_id))
        
        return classrooms

class ClassroomChatSession:
    def __init__(self, id, name, owner, classroom):
        self.id = id
        self.name = name
        self.owner = owner
        self.classroom = classroom
    
    def delete(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('DELETE FROM chat_logs WHERE session_id=?', [self.id])
        connection.commit()

        cursor.execute('DELETE FROM classroom_chat_sessions WHERE id=?', [self.id])
        connection.commit()

        connection.close()

    def get_logs(self):
        if not self.classroom.is_logs_allowed():
            raise LogsNotAllowed()

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM chat_logs WHERE session_id=?', [self.id])
        response = cursor.fetchall()

        connection.close()

        log = []

        for line in response:
            id = line[0]
            prompt = line[1]
            output = line[2]
            date = datetime.fromtimestamp(line[3])
            log.append(ChatLogEntry(id, prompt, output, date, self))
        
        return log
    
    def say(self, prompt):
        if not self.classroom.is_chat_allowed():
            raise ChatNotAllowed()

        response = ai.ai_output(prompt)
        date = datetime.now(timezone.utc)


        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('INSERT INTO chat_logs (prompt, response, date, session_id) VALUES (?, ?, ?, ?)', [prompt, response, date.timestamp(), self.id])
        connection.commit()

        cursor.execute('SELECT LAST_INSERT_ROWID();')
        id = cursor.fetchone()[0]

        connection.close()

        return ChatLogEntry(id, prompt, response, date, self)


class ClassroomUserAlreadyExistsException(Exception):

    def __init__(self, email):
        self.email = email
        super().__init__(f'User with email {email} already exists.')


class StudentAlreadyHasSession(Exception):
    def __init__(self, student: ClassroomUser, session: ClassroomChatSession):
        self.student = student
        self.session = session
        super().__init__(f'Student with id {student.id} already has a chat session with id {session.id}')

class LogsNotAllowed(Exception):
    def __init__(self):
        super().__init__(f'You are not allowed to view logs')

class ChatNotAllowed(Exception):
    def __init__(self):
        super().__init__(f'You are not allowed to chat')

class UserIsNotATeacher(Exception):
    def __init__(self, action):
        self.action = action
        super().__init__(f'You must be a teacher to perform the following action: {action}')