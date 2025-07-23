from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from dotenv import load_dotenv
import os

db = SQLAlchemy()

def make_app():
    load_dotenv()
    sql_pass = os.getenv("POSTGRES_PASSWORD")
    sql_user = os.getenv("POSTGRES_USERNAME")
    sql_db = os.getenv("POSTGRESS_DATABASE")
    sql_port = os.getenv("POSTGRES_PORT")
    sql_host = os.getenv("POSTGRES_HOST")

    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{sql_user}:{sql_pass}@{sql_host}:{sql_port}/{sql_db}"
    
    from .views import views
    from .auth import auth
    from .models import Users

    app.register_blueprint(auth)
    app.register_blueprint(views)

    LogMan = LoginManager()

    @LogMan.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))
    
    LogMan.init_app(app)
    db.init_app(app)

    make_db(app)

    return app

def make_db(app):
    with app.app_context():
        db.create_all()