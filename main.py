import sqlite3
from flask import Flask, request
from datetime import datetime, timedelta
from utils import session_utils

app = Flask(__name__)
DB_PATH = "prod.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                public_id TEXT UNIQUE,
                steps INTEGER,
                is_finished BOOLEAN
            )
        ''')
        conn.commit()


init_db()

timedelta_between_create_requests = timedelta(milliseconds=10)
last_created_session_datetime: datetime | None = None


@app.route('/create-session', methods=['POST'])
def create_session():
    global last_created_session_datetime

    current_datetime = datetime.now()
    if last_created_session_datetime is not None and \
            (current_datetime - last_created_session_datetime) <= timedelta_between_create_requests:
        return {'success': False, 'msg': 'Too frequent create requests'}

    last_created_session_datetime = current_datetime
    public_id = session_utils.create_session_id()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (public_id, steps, is_finished) VALUES (?, ?, ?)
        ''', (public_id, 0, False))
        conn.commit()

    return {'success': True, 'data': {'public_id': public_id}}


@app.route('/update-session', methods=['POST'])
def update_session():
    data = request.get_json(force=True)
    public_id, steps, is_finished = data['public_id'], data['steps'], data['is_finished']

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        session_data = cursor.execute('''
            SELECT * FROM sessions WHERE public_id = ?
        ''', [public_id]).fetchone()

        if session_data is None:
            return {'success': False, 'msg': 'No session with current public_id'}

        _, _, current_steps, current_finished_status = session_data

        if current_finished_status == 1:
            return {'success': False, 'msg': 'Session already finished'}

        new_steps, new_finished_status = current_steps + steps, is_finished

        cursor.execute('''
            UPDATE sessions SET steps = ?, is_finished = ? WHERE public_id = ?
        ''', (new_steps, new_finished_status, public_id))
        conn.commit()

    return {'success': True, 'data': {}}


if __name__ == '__main__':
    app.run(debug=True)
