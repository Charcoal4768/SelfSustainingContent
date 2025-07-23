from . import db
from flask_login import current_user, UserMixin

class Users(db.Model, UserMixin):
    #simple user model with email, password, id, optional username and an equiries feild
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    comments = db.relationship('Comments', backref='user', lazy=True)
    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    @classmethod
    def make_user(cls, email, password, username):
        new_user = cls(email=email, password=password, username=username)
        db.session.add(new_user)
        db.session.commit()
        return new_user
    
class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForiegnKey('users.id'), nullable=False)
    body = db.Column(db.String(512))
    @classmethod
    def make_comment(cls, user_id, messgae):
        new_comment = cls(user_id=user_id,messgae=messgae)
        db.session.add(new_comment)
        db.session.commit()
        return new_comment