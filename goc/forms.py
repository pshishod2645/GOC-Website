from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FieldList, FormField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.widgets import TextArea
from goc import db, USERNAME_REGEX_NOT
from goc.models import User
import requests, re

class SignUpForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(max=40)])
    username = StringField('Username (Codeforces)', validators=[DataRequired(), Length(max=60)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=80)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    profile_pic_url = StringField()

    def validate_username(self, username): 
        if re.search(USERNAME_REGEX_NOT, str(username.data)):
            raise ValidationError('Username should contain only Latin letters, digits, underscore or dash characters')
        else:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username has already been taken')

    def validate_email(self, email): 
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email has already been taken.')

    def validate_on_submit(self):
        if not FlaskForm.validate(self): 
            return False

        username_errors, email_errors = [], []

        url = 'https://codeforces.com/api/user.info?handles=' + str(self.username.data)
        data = requests.get(url).json()

        if(data['status'] == "FAILED"):
            username_errors.append('Invalid Username. Please provide a valid codeforces username')
        elif('email' not in data['result'][0]):
            email_errors.append('Email Address not yet public on codeforces')
        else: 
            email = data['result'][0]['email']
            if email != str(self.email.data) : 
                email_errors.append('Email address is different than on codeforces')

        if len(username_errors) > 0 or len(email_errors) > 0: 
            self.username.errors = tuple(username_errors)
            self.email.errors = tuple(email_errors)
            return False
        
        self.profile_pic_url.data = data['result'][0]['titlePhoto']
        return True

class LoginForm(FlaskForm):
    username_or_email = StringField('Username/Email', validators=[DataRequired(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=80)])
    submit = SubmitField('Log In')
    
    def validate(self):
        if not FlaskForm.validate(self): 
            return False
            
        username_or_email_errors, password_errors = [], []

        user = db.session.query(User).filter((User.username==self.username_or_email.data) | (User.email==self.username_or_email.data)).first()

        if user:
            if user.password != str(self.password.data):
                password_errors.append('Invalid Password')
        else:
            username_or_email_errors.append('Please enter valid username/email')
        
        if len(username_or_email_errors) > 0 or len(password_errors) > 0: 
            self.username_or_email.errors = tuple(username_or_email_errors)
            self.password.errors = tuple(password_errors)
            return False
        return True

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()]) 
    content = StringField('Content', validators=[DataRequired()])
    tags = StringField('Tag', validators=[DataRequired()])
    submit = SubmitField('Add Post')

class ShortlistingRound(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()])
    selected = BooleanField('Got Selected?', default = False)

class InterviewRound(ShortlistingRound):
    joining = BooleanField('Will be joining?', default=False)

class Shortlisting(FlaskForm):
    content = StringField('Content', validators=[DataRequired()])
    rounds = FieldList(FormField(ShortlistingRound))

class Interview(FlaskForm): 
    content = StringField('Content', validators=[DataRequired()])
    rounds = FieldList(FormField(InterviewRound))

class BlogForm(PostForm):    
    shortlisting = FormField(Shortlisting)
    interview = FormField(Interview)      
    addShortListing = SubmitField('Add Company')
    addInterview = SubmitField('Add Company')
    submit = SubmitField('Add Blog')

    def validate(self): 
        if not FlaskForm.validate(self):
            return False
        
        joining_companies = []
        submit_errors = []
        for round in self.interview.rounds: 
            if round.joining.data == True: 
                joining_companies.append(round.company_name.data) 
        
        if len(joining_companies) > 1: 
            submit_errors.append('You can join atmost one among ' + ', '.join(joining_companies))
            self.submit.errors = tuple(submit_errors)
            return False
        return True