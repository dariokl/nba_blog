from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from webapp import db
from webapp.models import User
from webapp.users.forms import RegistrationForm, LoginForm, UpdateUserForm
from webapp.users.userpic import add_profile_pic

users = Blueprint('users',__name__)



#register
@users.route('/register', methods=["GET", "POST"])
def register():
    """ Simple register view that updates the database after submiting the form"""

    form= RegistrationForm()

    if form.validate_on_submit():

        user = User(email = form.email.data,
                    username = form.username.data,
                    password = form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('You have sucesfully registered your account')

        return redirect(url_for('users.login'))

    return render_template('register.html', form=form)

#login
@users.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user.check_password(form.password.data) and user is not None:

            login_user(user)
            flash('Log in success!')

            next = request.args.get('next')

            if next == None or not next[0]=='/':

                next = url_for('core.index')

            return redirect(next)

    return render_template('login.html', form=form)




#logout
@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('core.index'))
#acccount
@users.route('/account', methods=["GET", "POST"])
@login_required
def account():
    """ A view that allows you to change username and profile picture"""

    form = UpdateUserForm()

    if form.validate_on_submit():
        print(form)
        if form.picture.data:
            username = current_user.username
            pic = add_profile_pic(form.picture.data,username)
            current_user.profile_image = pic

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('User Account Updated')
        return redirect(url_for('users.account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image)
    return render_template('account.html', profile_image=profile_image, form=form)
