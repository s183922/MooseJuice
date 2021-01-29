from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, FloatField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from MooseJuice.models import User
from flask_login import current_user
from MooseJuice.utils import groupBy
import numpy as np
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    room     = SelectField('room', choices = [], validators = [DataRequired()])
    
    submit = SubmitField('Move in')

    def validate_username(self,username):
        user = User.query.filter_by(username = username.data).filter_by(status = "active").first()
        
        if user:
            
            raise ValidationError(f'There already exists a person with this name in kitchen T. Choose a different one.' )


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max = 20)])
    password = PasswordField('Password', validators = [DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

    # def validate_user(self,username):
    #     user = User.query.filter_by(username = username.data).filter_by(status = "active").first()

    #     if not user:
    #         raise ValidationError('The user either does not exist or is inactive')


class UpdateUsernameForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators = [DataRequired()])
    
    submit = SubmitField('Update Username')

    def validate_username(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).filter_by(status = "active").first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one')


class UpdatePasswordForm(FlaskForm):
    password1 = PasswordField('Password', validators = [DataRequired()])
    new_password = PasswordField('New Password', validators = [DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password', message="Must be equal to New Password")])

    submit1 = SubmitField('Update Password')



class PurchaseForm(FlaskForm):
    amount_beer = StringField('Beer')
    amount_soda = StringField('Soda')
    submit = SubmitField('Buy')


    formType = "Purchase"
    
    def validate_username(self, amount_beer):
        if amount_beer == None:
            raise ValidationError('That username is taken. Please choose a different one')

    

class TransferMoneyForm(FlaskForm):
    transfer = FloatField('Money to transfer', validators=[DataRequired(), NumberRange(min=0)])

    submit = SubmitField('Transfer Money')

    formType = "Transfer"
    

class MoveOutForm(FlaskForm):
    moveout = BooleanField('I am sure', validators=[DataRequired()])

    submit  = SubmitField('Move out')


class TableForm(FlaskForm):
    date = SelectField("Date", choices=[], default = 0)
    week = SelectField("Week", choices=[],  default = 0)
    month = SelectField("Month", choices=[],  default = 0)


    submit4 = SubmitField("Submit")
    def __init__(self, table):
        super(TableForm, self).__init__()
        self.table = table
        self.Dchoices = [(i, t[0]) for i, t in enumerate(groupBy(table, "Date").values)]
        self.date.choices = self.Dchoices
        

        self.Wchoices = [(i, t[0]) for i, t in enumerate(groupBy(table, "Week").values)]
        self.week.choices = self.Wchoices
        

        self.Mchoices = [(i, t[0]) for i, t in enumerate(groupBy(table, "Month").values)]
        self.month.choices = self.Mchoices

        self.beers = groupBy(table, "Date")["Beers"].iloc[0]
        self.sodas = groupBy(table, "Date")["Sodas"].iloc[0]
        self.transfer = groupBy(table, "Date")["Transfer"].iloc[0]
        self.amount = groupBy(table, "Date")["Amount"].iloc[0]


    def updateTable(self, type_, number):
        self.beers = groupBy(self.table, type_)["Beers"].iloc[int(number)]
        self.sodas = groupBy(self.table, type_)["Sodas"].iloc[int(number)]
        self.transfer = int(np.ceil(float(groupBy(self.table, type_)["Transfer"].iloc[int(number)])))
        self.amount = int(np.ceil(float(groupBy(self.table, type_)["Amount"].iloc[int(number)])))

        return ""

class GoalForm(FlaskForm):
    item = StringField("Name of Goal", validators=[DataRequired()])
    price = FloatField("Price of Goal", validators=[DataRequired(), NumberRange(min=0)])
    image = FileField("Upload image", validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField("Add new goal")