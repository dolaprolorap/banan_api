from flask import Flask, request

from utils import session_utils
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Session(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(unique=True)
    steps: Mapped[int]
    is_finished: Mapped[bool]


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prod.db'
db.init_app(app)
with app.app_context():
    db.create_all()


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

    session = Session(
        public_id=public_id,
        steps=0,
        is_finished=False
    )
    db.session.add(session)
    db.session.commit()

    return {'success': True, 'data': {'public_id': public_id}}


@app.route('/update-session', methods=['POST'])
def update_session():
    data = request.get_json(force=True)
    public_id, steps, is_finished = data['public_id'], data['steps'], data['is_finished']

    db.session.query(Session).\
        filter(Session.public_id == public_id).\
        update({
            'steps': steps,
            'is_finished': is_finished
        })
    db.session.commit()

    return {'success': True, 'data': {}}
