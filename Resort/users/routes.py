from flask import render_template, request, redirect, url_for, flash, session
from Resort.models import db, User
from Resort.users.forms import LoginForm, RegisterForm
from Resort.users import users
from datetime import timedelta
from flask_login import  login_user, logout_user, current_user




@users.route('/register', methods=['GET', 'POST'])
def register():
    # No changes needed here
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered. Please use a different email or login.", "danger")
            return render_template("register.html", form=form)
            
        new_user = User(name=form.name.data, email=form.email.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("users.login"))
    
    return render_template("register.html", form=form,title='Register')

@users.route('/logout')
def logout():
    logout_user()  # Use Flask-Login's logout_user function
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('users.login'))

@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email, password=password).first()

        if user:
            login_user(user, remember=form.remember.data)  # Use Flask-Login's login_user
            session["show_welcome"] = True
            
            if form.remember.data:
                users.permanent_session_lifetime = timedelta(days=30)
            
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html', form=form,title='Login')