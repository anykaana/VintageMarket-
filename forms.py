from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SelectField
from wtforms.fields import StringField, PasswordField, DateField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class RegisterForm(FlaskForm):
    profile_img = FileField("Profile Image", validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'მხოლოდ JPG და PNG!')
    ])
    username = StringField("Username", validators=[
        DataRequired(message="მომხმარებლის სახელი სავალდებულოა"),
        Length(min=5, max=25, message="მომხმარებლის სახელი უნდა იყოს 5-დან 25 სიმბოლომდე")
    ])
    password = PasswordField("Password", validators=[
        DataRequired(message="პაროლი სავალდებულოა"),
        Length(min=6, message="პაროლი უნდა შეიცავდეს მინიმუმ 6 სიმბოლოს")
    ])
    repeat_password = PasswordField("Repeat Password", validators=[
        DataRequired(message="გაიმეორეთ პაროლი"),
        EqualTo("password", message="პაროლები არ ემთხვევა")
    ])
    birthday = DateField("Birthday", format='%Y-%m-%d')
    submit = SubmitField("რეგისტრაცია")


class LoginForm(FlaskForm):
    username = StringField("მომხმარებელი", validators=[DataRequired()])
    password = PasswordField("პაროლი", validators=[DataRequired()])
    login = SubmitField("შესვლა")


class ProductForm(FlaskForm):
    img = FileField('სურათი', validators=[
   
        FileAllowed(['jpg', 'jpeg', 'png'], 'მხოლოდ სურათების ატვირთვაა შესაძლებელი!')
    ])
    name = StringField('დასახელება', validators=[DataRequired()])
    price = FloatField('ფასი', validators=[DataRequired()])
    category = SelectField('კატეგორია', choices=[
        ('მარკები', 'მარკები'),
        ('ფოტოაპარატები', 'ფოტოაპარატები'),
        ('ტანსაცმელი', 'ტანსაცმელი'),
        ('კასეტები', 'კასეტები'),
        ('წიგნები', 'წიგნები'),
        ('საათები', 'საათები'),
        ('სხვა საკოლექციო ნივთები', 'სხვა საკოლექციო ნივთები')
    ], validators=[DataRequired()])
    submit = SubmitField('დამატება')