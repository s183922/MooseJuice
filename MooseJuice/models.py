from datetime import datetime
from MooseJuice import db, login_manager, admin
from flask_login import UserMixin, current_user
from flask_table import Table, Col
from flask_admin.contrib.sqla import ModelView

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id          = db.Column(db.Integer, primary_key=True)
    username    = db.Column(db.String(20), unique=False, nullable=False)
    password    = db.Column(db.String(60), unique=False, nullable=False)
    room        = db.Column(db.String(10), unique=False, nullable=False)
    status      = db.Column(db.String(10), unique=False, nullable=False, default = 'active')
    movein_date = db.Column(db.DateTime, nullable=False, default = datetime.utcnow)
    
    posts = db.relationship('Post', backref='author', lazy = True)

    def __repr__(self):
        return f"User {self.id} {self.username} {self.room}"
        
class Post(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    post_type   = db.Column(db.String(20), nullable=False)
    date        = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    amount      = db.Column(db.Float, nullable=False, default = 0)

    beers       = db.Column(db.Integer, default = 0)
    sodas       = db.Column(db.Integer, default = 0)


    user_balance = db.Column(db.Float, default = 0)

    moose_balance = db.Column(db.Float, nullable=False, default = 0)


    comment     = db.Column(db.String(100))


    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post {self.id}: type = {self.post_type}, amount = {self.amount}, author = {self.author.username}, date = {self.date})"


class Prices(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    date        = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    beer_price  = db.Column(db.Float, nullable=False)
    soda_price  = db.Column(db.Float, nullable=False)
    account     = db.Column(db.String(50), nullable=True, default = "5396-560516")


class Goals(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    item      = db.Column(db.String(100), nullable=False)
    price     = db.Column(db.Float, nullable=False)
    progress  = db.Column(db.Integer, nullable=False, default = 0.0)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Prices, db.session))
admin.add_view(ModelView(Goals, db.session))