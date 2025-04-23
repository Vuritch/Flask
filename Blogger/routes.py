from flask import render_template, flash, redirect, url_for
from Blogger import app,db
from Blogger.forms import RegistrationForm,LoginForm
from Blogger.models import User , Blog
from werkzeug.security import generate_password_hash,check_password_hash

@app.route('/',methods=['GET'])
def index():
    return render_template('index.html', title='Home', cssFile='home.css')

@app.route('/about',methods=['GET'])
def about():
    return render_template('about.html', title='about', cssFile='about.css')

@app.route('/contact',methods=['GET'])
def contact():
    return render_template('contact.html', title='concat')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            flash(f'Login successful for {user.email}', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', title='Login', form=form)
   
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            password=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.name.data}', 'success')
        return redirect(url_for('login'))  # redirect للمسار login بعد التسجيل
    return render_template('register.html', title='Register', form=form)
