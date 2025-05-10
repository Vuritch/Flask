from flask import render_template, request, redirect, url_for, flash, session
from Resort.models import db, User
from Resort.users.forms import LoginForm, RegisterForm,ProfileForm,ChangePasswordForm
from Resort.users import users
from datetime import timedelta
from flask_login import  login_user, logout_user, current_user,login_required
from werkzeug.security import generate_password_hash, check_password_hash






@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # prevent duplicate
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash("Email already registered. Please use a different email or login.", "danger")
            return render_template("register.html", form=form)

        is_admin_creds = (
            form.email.data.lower() == 'admin@gmail.com'
            and form.password.data.lower() == 'admin1234'
        )
        role = 'admin' if is_admin_creds else 'guest'

        new_user = User(
            name=form.name.data,
            email=form.email.data.lower(),
            role=role
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        flash(
            "Registration successful! " + 
            ("Admin access granted." if is_admin_creds else "Please log in."),
            "success"
        )
        return redirect(url_for("users.login"))

    return render_template("register.html", form=form, title='Register')





@users.route('/logout')
def logout():
    logout_user()  # Use Flask-Login's logout_user function
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('users.login'))


@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            session['show_welcome'] = True
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            # DON'T redirect here — keep rendering with flash

  

    return render_template('login.html', form=form)





@users.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    profile_form = ProfileForm(obj=current_user)
    pwd_form     = ChangePasswordForm()

    # Save profile
    if profile_form.validate_on_submit() and 'submit_profile' in request.form:
        current_user.name  = profile_form.name.data
        current_user.email = profile_form.email.data.lower()
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('users.profile'))

    # Change password
    if pwd_form.validate_on_submit() and 'submit_password' in request.form:
        current_user.set_password(pwd_form.new_password.data)
        db.session.commit()
        flash('Password changed.', 'success')
        return redirect(url_for('users.profile'))

    return render_template(
        'profile.html',
        profile_form=profile_form,
        pwd_form=pwd_form,
        title='Your Profile'
    )






