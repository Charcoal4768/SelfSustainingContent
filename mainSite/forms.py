from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, SelectField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class SignupForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=150)])
    password = PasswordField("Password", validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirmpassword = PasswordField("Confirm Password", validators=[
        DataRequired(),
        Length(min=6),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField("Sign Up")


# class ArticleForm(FlaskForm):
#     product1 = StringField('Product 1', validators=[DataRequired()])
#     product2 = StringField('Product 2', validators=[DataRequired()])
#     affiliate1 = StringField('Affiliate 1')
#     affiliate2 = StringField('Affiliate 2')
#     includeHN = BooleanField('Include HackerNews?')
#     extra = TextAreaField('Extra Info')
#     articleExtra = TextAreaField('Article Extra')
#     articleType = SelectField('Article Type', choices=[
#         ("Pros vs Cons", "PROS VS CONS"),
#         ("Why", "WHY STYLE"),
#         ("How to", "HOW TO"),
#         ("Listicle", "LISTICLE"),
#         ("Top X", "TOP X")
#     ])