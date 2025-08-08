from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_socketio import SocketIO, join_room, leave_room
from flask_migrate import Migrate
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException
import os
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.getenv("DATABASE_URL") or
    f"postgresql://{os.getenv('POSTGRES_USERNAME')}:{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DATABASE')}"
)
app.config['SESSION_COOKIE_SECURE'] = not app.debug and not app.testing
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# GLOBAL EXTENSIONS — import from here only
db = SQLAlchemy()
csrf = CSRFProtect()
socketio = SocketIO(app=app, cors_allowed_origins="*", async_mode="threading")

db.init_app(app)
csrf.init_app(app)
Migrate(app, db)

from .views import views
from .auth import auth
app.register_blueprint(auth)
app.register_blueprint(views)

# LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    from .models import Users
    try:
        return Users.query.get(int(user_id))
    except (TypeError, ValueError):
        return None
    
# Error handler
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    return render_template("error.html", error_code=e), 500

# Optional DB bootstrap
with app.app_context():
    db.create_all()

@socketio.on('join_room')
def on_join(data):
    room = data.get('room')
    join_room(room)
    print(f"{request.sid} has joined room {room}")