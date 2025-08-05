from . import db
from flask_login import current_user, UserMixin

class Users(db.Model, UserMixin):
    #simple user model with email, password, id, optional username and an equiries feild
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    is_admin = db.Column(db.Boolean, default=False)
    comments = db.relationship('Comments', backref='user', lazy=True)
    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    @classmethod
    def make_user(cls, email, password, username, is_admin = False):
        new_user = cls(email=email, password=password, username=username, is_admin = is_admin)
        db.session.add(new_user)
        db.session.commit()
        return new_user
    
class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    body = db.Column(db.String(512))
    @classmethod
    def make_comment(cls, user_id, message):
        new_comment = cls(user_id=user_id, body=message)
        db.session.add(new_comment)
        db.session.commit()
        return new_comment