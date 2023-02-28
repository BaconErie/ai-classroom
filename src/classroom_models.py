class ClassroomUser:
    # CLASS METHODS #

    def get_user_by_id(id):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM classroom_users WHERE id=?', [id])
        response = cursor.fetchone()

        connection.close()

        if response is None:
            return None

        return ClassroomUser(response[0], response[1], response[2], response[3], response[4])
    
    def get_user_by_email(email):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM classroom_users WHERE email=?', [email])
        response = cursor.fetchone()

        connection.close()

        if response is None:
            return None

        return ClassroomUser(response[0], response[1], response[2], response[3], response[4])

    def create_user(email, name, password, is_teacher):
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

        cursor.execute('INSERT INTO classroom_users (email, name, password, salt) VALUES (?, ?, ?, ?)', [email, name, hashed_password, salt])
        connection.commit()

        cursor.execute('SELECT id FROM classroom_users WHERE email=?', [email])
        id = cursor.fetchone()[0]

        connection.close()

        return ClassroomUser(id, email, name, hashed_password, salt)

    # INSTANCE METHODS #

    def __init__(self, id, email, name, password, salt):
        '''NOTE: This function should NOT be called directly. Please use the create_user classmethod'''
        self.id = id
        self.email = email
        self.name = name
        self.password = password
        self.salt = salt

    def get_chat_sessions(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('SELECT id, name FROM classroom_chat_sessions WHERE user_id=?', [self.id])
        response = cursor.fetchall()

        if len(response) == 0:
            return None

        chat_sessions = []

        for line in response:
            chat_sessions.append(ClassroomChatSession(line[0], line[1], self))
        
        return chat_sessions
    
    def create_chat_session(self, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('INSERT INTO classroom_chat_sessions (name, user_id) VALUES (?, ?)', [name, self.id])
        connection.commit()

        cursor.execute('SELECT LAST_INSERT_ROWID();')
        id = cursor.fetchone()[0]

        connection.close()

        return ClassroomChatSession(id, name, self)

class ClassroomChatSession:
    def __init__(self, id, name, owner):
        self.id = id
        self.name = name
        self.owner = owner
    
    def delete(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        cursor.execute('DELETE FROM chat_logs WHERE session_id=?', [self.id])
        connection.commit()

        cursor.execute('DELETE FROM classroom_chat_sessions WHERE id=?', [self.id])
        connection.commit()

        connection.close()

    def get_logs(self):
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