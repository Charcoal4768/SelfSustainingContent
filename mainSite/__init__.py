from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from dotenv import load_dotenv
from .sockets import socketio
import os

db = SQLAlchemy()
# socketio = SocketIO()

def make_app():
    load_dotenv()
    sql_pass = os.getenv("POSTGRES_PASSWORD")
    sql_user = os.getenv("POSTGRES_USERNAME")
    sql_db = os.getenv("POSTGRES_DATABASE")
    sql_port = os.getenv("POSTGRES_PORT")
    sql_host = os.getenv("POSTGRES_HOST")

    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{sql_user}:{sql_pass}@{sql_host}:{sql_port}/{sql_db}"
    print(f"postgresql://{sql_user}:{sql_pass}@{sql_host}:{sql_port}/{sql_db}")
    
    from .views import views
    from .auth import auth

    app.register_blueprint(auth)
    app.register_blueprint(views)

    LogMan = LoginManager()

    @LogMan.user_loader
    def load_user(user_id):
        from .models import Users
        try:
            return Users.query.get(int(user_id))
        except (TypeError, ValueError):
            return None

    
    LogMan.init_app(app)
    db.init_app(app)

    make_db(app)

    make_socket(app)

    return app

def make_db(app):
    with app.app_context():
        db.create_all()

def make_socket(app):
    socketio.init_app(app, cors_allowed_origins="*")

    # @socket.on('connect')
    # def handle_connect():
    #     if current_user.is_authenticated:
    #         print(f"{current_user.username} connected")
    #     else:
    #         print("Anonymous user connected")
    
    # @socket.on('disconnect')
    # def handle_disconnect():
    #     if current_user.is_authenticated:
    #         print(f"{current_user.username} disconnected")
    #     else:
    #         print("Anonymous user disconnected")