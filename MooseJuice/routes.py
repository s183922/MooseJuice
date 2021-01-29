from MooseJuice.forms import RegistrationForm, LoginForm, UpdateUsernameForm, UpdatePasswordForm, PurchaseForm, TransferMoneyForm, MoveOutForm, TableForm, GoalForm
from flask import render_template, url_for, flash, redirect, request
from MooseJuice.models import User, Post, Prices, Goals
from MooseJuice import app, bcrypt, db
from flask_login import login_user, current_user, logout_user, login_required, logout_user
from MooseJuice.utils import NewPost, getQuery, getRoom, getUserbalance, Tab, getDF, groupBy, MooseStats, getDFPost, getPrices, updateProgress, updatePosts
from werkzeug.utils import secure_filename
import secrets
import os
@app.before_first_request
def before_first_request():
    if not User.query.filter_by(status = 'admin').first():
        password = '$2b$12$rFvr/ona8l3EzGpuk2EkQOIv/1GH8GrUpxLGaDBmhg6FC7JmSwAZi'
        admin_user = User(username = 'admin', room = 'admin', status = 'admin', password=password)
        
        db.session.add(admin_user)
        db.session.commit()

        first_post = Post(post_type = "First commit", comment = "First commit", moose_balance=0, user_id=admin_user.id)
        db.session.add(first_post)
        db.session.commit()

        prices = Prices(beer_price = 5.0, soda_price = 5.0)
        db.session.add(prices)
        db.session.commit()
        


@app.route("/", methods = ['GET', 'POST'])
@app.route("/login", methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).filter_by(status = 'active').first()

        user_admin = User.query.filter_by(username = form.username.data).filter_by(status = 'admin').first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember_me.data)
            next_page = request.args.get('next')
            flash(f'You have been logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))

        elif user_admin and bcrypt.check_password_hash(user_admin.password, form.password.data):
            login_user(user_admin, remember = form.remember_me.data)
            next_page = request.args.get('next')
            flash(f'You have been logged in!', 'success')
            return redirect(next_page) if next_page else redirect('/admin')

        

        else:
            flash(f'Login unsuccessfull. Please check username and password', 'danger')

    return render_template('login.html', title = 'Login', form = form)

@app.route("/Home", methods = ['GET', 'POST'])
@login_required
def home():
    Tab.updateTab("balance")
    Tab.updateTab("date")
    updatePosts()
    image_file = url_for('static', filename = 'profile_pics/default.jpg' )
    form = PurchaseForm()
    room = ""
    beer_price, soda_price = getPrices()
    if current_user.is_authenticated:
        room = getRoom(current_user)

    if form.validate_on_submit() and form.submit.data:
        if (form.amount_soda.data and form.amount_soda.data != "0") or (form.amount_beer.data and form.amount_beer.data != "0"):
            purchase, message = NewPost(form, current_user.id)
            db.session.add(purchase)
            db.session.commit()
            flash(message, "success")
        
            return redirect(url_for('home'))


    return render_template('home.html', title = "Moose Juice", image_file = image_file, form = form, room = room, beer_price = beer_price, soda_price = soda_price)


rooms = {str(i):"available" for i in range(188,200)}
guests = {"Guest"  + str(i) :"available" for i in range(1,10)}


@app.route("/register", methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    
    for user in User.query.filter_by(status = "active"):
        if "Guest" in user.room:
            guests[user.room] = 'occupied'
        else:
            rooms[user.room] = 'occupied'

    form.room.choices = list(filter(None, [(room, "Room " + room) if cond != 'occupied' else None for room, cond in rooms.items()] + [(guest, guest) if cond != 'occupied' else None for guest, cond in guests.items()]))
   
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, password = hashed_password, room = form.room.data)
        
        db.session.add(user)
        db.session.commit()
        moose_balance = Post.query.all()[-1].moose_balance


      

        flash(f'Your account has been created! You are now able to login', 'success')
        return redirect(url_for('login'))
 
    
    return render_template('register.html', title = 'Register', form = form, rooms = rooms, guests = guests)




@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/account", methods = ['GET', 'POST'])
@login_required
def account():
    form = TransferMoneyForm()
    form2 = UpdateUsernameForm()
    form3 = UpdatePasswordForm()
    account_number = Prices.query.all()[-1].account
    room = getRoom(current_user)
    category, user_balance = getUserbalance(current_user)
    # user = User.query.filter_by(username = form2.username.data).first()
    image_file = url_for('static', filename = 'profile_pics/default.jpg')

    table = getDF(current_user)
    form4 = TableForm(table)
    date = request.form.get('date')
    week = request.form.get('week')
    month = request.form.get('month')

    if request.form.get('date'):
        Tab.updateTab('post')
        Tab.updateTab('date')
        form4.updateTable('Date', form4.date.data)
    if request.form.get('week'):
        Tab.updateTab('post')
        Tab.updateTab('week')
        form4.updateTable('Week', form4.week.data)
    if request.form.get('month'):
        Tab.updateTab('post')
        Tab.updateTab('month')
        form4.updateTable('Month', form4.month.data)
    
    
    if form.validate_on_submit() and form.submit.data:
        post, message = NewPost(form, current_user.id)
        if not post:
            flash(message, "danger")
        else:
            db.session.add(post)   
            db.session.commit()
            Tab.updateTab("balance")

            flash(message, "success")
        return redirect(url_for('account'))

    elif form.transfer.data and form.submit.data:

        if form.transfer.data < 0:
            Tab.updateTab("balance")

            flash("Please don't transfer a negative amount of money...", "danger")
            return redirect(url_for('account'))

    if form2.validate_on_submit() and bcrypt.check_password_hash(current_user.password, form2.password.data) and form2.submit.data:
        current_user.username = form2.username.data
        Tab.updateTab("update")
        db.session.commit()
        flash("Your username has been updated", 'success')
        return redirect(url_for('account'))
    
    elif request.method == 'GET':
        form2.username.data = current_user.username
        form2.password.data = '*******'

    elif not bcrypt.check_password_hash(current_user.password, form2.password.data) and form2.submit.data:
        Tab.updateTab("update")
        flash("Wrong password", 'danger')
        return redirect(url_for('account'))


    if form3.validate_on_submit() and bcrypt.check_password_hash(current_user.password, form3.password1.data) and form3.submit1.data:
        hashed_password = bcrypt.generate_password_hash(form3.new_password.data).decode('utf-8')
        current_user.password = hashed_password
        Tab.updateTab("update")
        db.session.commit()
        flash("Your password has been updated", 'success')
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form2.username.data = current_user.username
        form3.password1.data = '*******'

    elif not bcrypt.check_password_hash(current_user.password, form3.password1.data) and form3.submit1.data:
        Tab.updateTab("update")
        flash("Wrong password", 'danger')
        return redirect(url_for('account'))

    

    return render_template('account.html',
                            title = 'Account',
                            image_file = image_file,
                            room = room,
                            category = category,
                            form = form,
                            form2 = form2,
                            form3 = form3, 
                            form4 = form4,
                            user_balance = user_balance,
                            Tab = Tab,
                            table = table,
                            headings = table.columns,
                            account_number = account_number)



@app.route("/update_account", methods = ['GET', 'POST'])
@login_required
def update_account():
    form = UpdateAccountForm()
    user = User.query.filter_by(username = form.username.data).first()
    room = getRoom(current_user)
    if form.validate_on_submit() and bcrypt.check_password_hash(user.password, form.password.data):
        current_user.username = form.username.data
        hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        current_user.password = hashed_password
        db.session.commit()
        flash("Your account has been updated", 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.password.data = '*******'
    elif not bcrypt.check_password_hash(user.password, form.password.data):
        flash("Wrong password", 'danger')
    image_file = url_for('static', filename = 'profile_pics/default.jpg')
    return render_template('update_account.html', title = 'Update Account', image_file = image_file, form = form, room = room)



@app.route("/moving_out", methods = ['GET', 'POST'])
@login_required
def moving_out():
    form = MoveOutForm()
    room = getRoom(current_user)
    category, user_balance = getUserbalance(current_user)
    image_file = url_for('static', filename = 'profile_pics/default.jpg')

    if form.validate_on_submit():
        flash("You have moved out. See you soon!", 'success')
        current_user.status = 'inactive'
        db.session.commit()

        logout()

        return redirect(url_for('home'))
    return render_template('moveout.html', title = 'Moving Out', image_file = image_file, category = category, form = form, room = room, user_balance = user_balance)


@app.route("/MooseScore")
@login_required
def moosescore():
    room = getRoom(current_user)  
    moosestats = MooseStats(getDFPost())
    beers, sodas = updatePosts(True)
    return render_template('moosescore.html', title = "Moose Score", room = room, stats = moosestats, beers = beers, sodas = sodas)


def save_image(form):
    random_hex = secrets.token_hex(8) 
    _, f_ext = os.path.splitext(form.filename)
    image_fn = random_hex + f_ext
    image_path = os.path.join(app.root_path, 'static\\uploads', image_fn)
    form.save(image_path)

    return image_fn

@app.route("/Goals",methods = ['GET', 'POST'])
@login_required
def goals():
    room = getRoom(current_user)  
    updateProgress()
    form = GoalForm()
    goals = Goals.query.all()
    image_file = url_for('static', filename = 'profile_pics/default.jpg')
    goals = [("active" if goal.id == 1 else "",
             goal,
             "success" if goal.progress == 100 else "warning",
             url_for('static', filename = "uploads/" + goal.image_file)) for goal in goals]

    status = "active" if len(goals) == 0 else ""
    if form.validate_on_submit():
        goal = Goals(item=form.item.data, price=form.price.data)
        if form.image.data:
            filename = save_image(form.image.data)
           
            goal.image_file = filename

        db.session.add(goal)
        db.session.commit()

        return redirect(url_for('goals'))
            

   
    return render_template('goals.html', title = "Moose Score", room = room, form = form, goals = goals,status = status)