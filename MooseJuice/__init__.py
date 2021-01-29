from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView


app = Flask(__name__)
UPLOAD_FOLDER = '/static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


app.config['SECRET_KEY'] = '8ba4ae8044cb14a474c522fecde7c4db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

class AdminView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.status == 'admin' and current_user.room == 'admin'

admin = Admin(app, index_view=AdminView())


from MooseJuice import routes

