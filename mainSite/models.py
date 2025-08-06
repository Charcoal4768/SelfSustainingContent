from . import db
from flask_login import UserMixin

class Users(db.Model, UserMixin):
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
    def make_user(cls, email, password, username, is_admin=False):
        new_user = cls(email=email, password=password, username=username, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()
        return new_user

article_tags = db.Table(
    'article_tags',
    db.Column('article_id', db.Integer, db.ForeignKey('articles.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    json_response = db.Column(db.JSON, default=[])
    comments = db.relationship('Comments', backref='article', lazy=True)

    tags = db.relationship("Tags", secondary=article_tags, back_populates="articles")

    @classmethod
    def get_article_by_id(cls,id:int):
        return cls.query.filter_by(id=id).first()
    @classmethod
    def create_article(cls, json_response:dict):
        if len(json_response) < 3:
            raise ValueError("json_response must be a valid version of ./generator/schema/article.json")

        search_tags = json_response.get('Tags', [])
        new_article = cls(
            title=json_response.get('title', "Untitled"),
            json_response=json_response
        )

        db.session.add(new_article)

        # Add or get existing tags
        for tag_str in search_tags:
            tag_name = tag_str.strip().lower()
            tag = Tags.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tags(name=tag_name)
                db.session.add(tag)
            new_article.tags.append(tag)

        db.session.add(new_article)
        db.session.commit()
        return new_article


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    body = db.Column(db.String(512))

    @classmethod
    def make_comment(cls, user_id, article_id, message):
        new_comment = cls(user_id=user_id, article_id=article_id, body=message)
        db.session.add(new_comment)
        db.session.commit()
        return new_comment

class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    articles = db.relationship("Articles", secondary=article_tags, back_populates="tags")
