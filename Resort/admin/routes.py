from flask import render_template,  redirect, url_for, flash
from Resort.models import User
from Resort.admin import admin
from flask_login import  login_required, current_user



@admin.route("/admin")
@login_required
def admin_dashboard():
    if current_user.email !='Admin@gmail.com':
        flash("Access Denied", "danger")
        return redirect(url_for('main.index'))  # أو أي صفحة تانية

    return render_template('admin.html')




@admin.route('/admin/users')
@login_required
def view_users():
    if current_user.email != 'Admin@gmail.com':
        flash("Access Denied", "danger")
        return redirect(url_for('main.index'))

    users = User.query.all()
    return render_template('users.html', users=users)