# admin.py
import os
from functools import wraps
from werkzeug.utils import secure_filename
from flask import (
    render_template, request, redirect, url_for,
    flash, abort, current_app
)
from flask_login import login_required, current_user
from Resort.admin import admin
from Resort import  db, ALLOWED_EXTENSIONS, allowed_file
from Resort.models import (
    User, Booking, RoomType, Room,
    ExtraService, GuestOption,Guest
)
from Resort.admin.forms import (
    UserForm, RoomTypeForm, RoomForm,
    ExtraServiceForm, GuestOptionForm
)
from wtforms.validators import Optional
from flask_wtf.file import FileAllowed


# ————————— Admin‐only decorator —————————
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ————————— Dashboard —————————
@admin.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        'Users':          User.query.count(),
        'Bookings':       Booking.query.count(),
        'Guests':         Guest.query.count(),
        'Room Types':     RoomType.query.count(),
        'Rooms':          Room.query.count(),
        'Extras':         ExtraService.query.count(),
        'Guest Options':  GuestOption.query.count(),
    }
    return render_template('admin/dashboard.html', stats=stats)

# ————————— Bookings List & Delete —————————
@admin.route('/admin/bookings')
@login_required
@admin_required
def admin_bookings():
    # show most recent first
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)

@admin.route('/admin/bookings/delete/<int:booking_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_booking(booking_id):
    b = Booking.query.get_or_404(booking_id)
    db.session.delete(b)
    db.session.commit()
    flash(f'Booking #{booking_id} deleted.', 'warning')
    return redirect(url_for('admin.admin_bookings'))
@admin.route('/admin/bookings/accept/<int:booking_id>', methods=['POST'])
@login_required
@admin_required
def admin_accept_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.status == 'pending':
        booking.status = 'accepted'
        db.session.commit()
        flash(f'Booking #{booking.id} accepted.', 'success')
    else:
        flash(f'Booking #{booking.id} is already {booking.status}.', 'info')
    return redirect(url_for('admin.admin_bookings'))

@admin.route('/admin/bookings/decline/<int:booking_id>', methods=['POST'])
@login_required
@admin_required
def admin_decline_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.status == 'pending':
        booking.status = 'declined'
        # Optionally free the room
        booking.room.is_available = True
        db.session.commit()
        flash(f'Booking #{booking.id} declined.', 'warning')
    else:
        flash(f'Booking #{booking.id} is already {booking.status}.', 'info')
    return redirect(url_for('admin.admin_bookings'))

# ————————— Users CRUD —————————
@admin.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)


@admin.route('/admin/users/create', methods=['GET','POST'])
@login_required
@admin_required
def admin_create_user():
    form = UserForm()
    if form.validate_on_submit():
        u = User(
            name=form.name.data,
            email=form.email.data.lower(),
            role=form.role.data
        )
        u.set_password(form.password.data)
        db.session.add(u)
        db.session.commit()
        flash('User created.', 'success')
        return redirect(url_for('admin.admin_users'))
    return render_template('admin/user_form.html', form=form, title='Create User')


@admin.route('/admin/users/edit/<int:user_id>', methods=['GET','POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    u = User.query.get_or_404(user_id)
    form = UserForm(obj=u)
    # make password optional on edit
    form.password.validators = []
    if form.validate_on_submit():
        u.name  = form.name.data
        u.email = form.email.data.lower()
        u.role  = form.role.data
        if form.password.data:
            u.set_password(form.password.data)
        db.session.commit()
        flash('User updated.', 'success')
        return redirect(url_for('admin.admin_users'))
    return render_template('admin/user_form.html', form=form, title='Edit User')


@admin.route('/admin/users/delete/<int:user_id>')
@login_required
@admin_required
def admin_delete_user(user_id):
    u = User.query.get_or_404(user_id)
    db.session.delete(u)
    db.session.commit()
    flash('User deleted.', 'warning')
    return redirect(url_for('admin.admin_users'))


# ————————— Room Types CRUD —————————
@admin.route('/admin/room_types')
@login_required
@admin_required
def admin_room_types():
    types = RoomType.query.all()
    return render_template('admin/room_types.html', room_types=types)


@admin.route('/admin/room_types/create', methods=['GET','POST'])
@login_required
@admin_required
def admin_create_room_type():
    form = RoomTypeForm()
    if form.validate_on_submit():
        # save main image
        main = form.main_image.data
        fn_main = secure_filename(main.filename)
        main.save(os.path.join(current_app.config['UPLOAD_FOLDER'], fn_main))

        # save gallery images
        gallery_fns = []
        for img in form.gallery_images.data:
            if img and allowed_file(img.filename):
                fn = secure_filename(img.filename)
                img.save(os.path.join(current_app.config['UPLOAD_FOLDER'], fn))
                gallery_fns.append(fn)

        rt = RoomType(
            name          = form.name.data,
            description   = form.description.data,
            base_price    = form.base_price.data,
            max_guests    = form.max_guests.data,
            main_image    = fn_main,
            gallery_images= ','.join(gallery_fns),
            features      = form.features.data,
            is_luxury     = form.is_luxury.data,
            luxury_label  = form.luxury_label.data
        )
        db.session.add(rt)
        db.session.commit()
        flash('Room type created!', 'success')
        return redirect(url_for('admin.admin_room_types'))

    return render_template('admin/room_type_form.html', form=form, title='Create Room Type')


@admin.route('/admin/room_types/edit/<int:type_id>', methods=['GET','POST'])
@login_required
@admin_required
def admin_edit_room_type(type_id):
    rt = RoomType.query.get_or_404(type_id)
    form = RoomTypeForm(obj=rt)
    # make file fields optional
    form.main_image.validators    = [ Optional(), FileAllowed(ALLOWED_EXTENSIONS, 'Images only') ]
    form.gallery_images.validators= [ Optional(), FileAllowed(ALLOWED_EXTENSIONS, 'Images only') ]

    if form.validate_on_submit():
        # if new main image uploaded
        if form.main_image.data:
            m = form.main_image.data
            fn = secure_filename(m.filename)
            m.save(os.path.join(current_app.config['UPLOAD_FOLDER'], fn))
            rt.main_image = fn

        # if new gallery
        if form.gallery_images.data:
            fns = []
            for img in form.gallery_images.data:
                if img and allowed_file(img.filename):
                    fn = secure_filename(img.filename)
                    img.save(os.path.join(current_app.config['UPLOAD_FOLDER'], fn))
                    fns.append(fn)
            rt.gallery_images = ','.join(fns)

        # update text fields
        rt.name         = form.name.data
        rt.description  = form.description.data
        rt.base_price   = form.base_price.data
        rt.max_guests   = form.max_guests.data
        rt.features     = form.features.data
        rt.is_luxury    = form.is_luxury.data
        rt.luxury_label = form.luxury_label.data

        db.session.commit()
        flash('Room type updated!', 'success')
        return redirect(url_for('admin.admin_room_types'))

    return render_template('admin/room_type_form.html', form=form, title='Edit Room Type')

# ————————— Guests List & Delete —————————
@admin.route('/admin/room_types/delete/<int:type_id>')
@login_required
@admin_required
def admin_delete_room_type(type_id):
    rt = RoomType.query.get_or_404(type_id)

    # — Prevent deleting a RoomType if any Rooms still reference it —
    if rt.rooms:
        flash(
            f"Cannot delete room type “{rt.name}”: "
            f"{len(rt.rooms)} room(s) still assigned. "
            "Please delete or reassign those rooms first.",
            "danger"
        )
        return redirect(url_for('admin.admin_room_types'))

    # Safe to delete
    db.session.delete(rt)
    db.session.commit()
    flash('Room type deleted.', 'warning')
    return redirect(url_for('admin.admin_room_types'))

@admin.route('/admin/guests')
@login_required
@admin_required
def admin_guests():
    """Show all guest records to the admin."""
    guests = Guest.query.order_by(Guest.guest_id.desc()).all()
    return render_template('admin/guests.html', guests=guests)

@admin.route('/admin/guests/delete/<int:guest_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_guest(guest_id):
    """Allow an admin to delete a guest record."""
    g = Guest.query.get_or_404(guest_id)
    db.session.delete(g)
    db.session.commit()
    flash(f'Guest #{guest_id} deleted.', 'warning')
    return redirect(url_for('admin.admin_guests'))
# ————————— Rooms CRUD —————————
@admin.route('/admin/rooms')
@login_required
@admin_required
def admin_rooms():
    rooms = Room.query.all()
    return render_template('admin/rooms.html', rooms=rooms)


@admin.route('/admin/rooms/create', methods=['GET','POST'])
@login_required
@admin_required
def admin_create_room():
    form = RoomForm()
    # populate room_type choices
    form.room_type_id.choices = [(rt.id, rt.name) for rt in RoomType.query.all()]

    if form.validate_on_submit():
        r = Room(
            room_number  = form.room_number.data,
            floor        = form.floor.data,
            room_type_id = form.room_type_id.data,
            is_available = form.is_available.data,
            notes        = form.notes.data
        )
        db.session.add(r)
        db.session.commit()
        flash('Room added.', 'success')
        return redirect(url_for('admin.admin_rooms'))

    return render_template('admin/room_form.html', form=form, title='Add Room')


@admin.route('/admin/rooms/edit/<int:room_id>', methods=['GET','POST'])
@login_required
@admin_required
def admin_edit_room(room_id):
    r = Room.query.get_or_404(room_id)
    form = RoomForm(obj=r)
    form.room_type_id.choices = [(rt.id, rt.name) for rt in RoomType.query.all()]

    if form.validate_on_submit():
        form.populate_obj(r)
        db.session.commit()
        flash('Room updated.', 'success')
        return redirect(url_for('admin.admin_rooms'))

    return render_template('admin/room_form.html', form=form, title='Edit Room')


@admin.route('/admin/rooms/delete/<int:room_id>', methods=['POST', 'GET'])
@login_required
@admin_required
def admin_delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    if room.bookings:
        flash(f"Cannot delete room {room.room_number}. It's linked to existing bookings.", 'danger')
        return redirect(url_for('admin.admin_rooms'))

    db.session.delete(room)
    db.session.commit()
    flash('Room deleted.', 'warning')
    return redirect(url_for('admin.admin_rooms'))



# ————————— Extra Services CRUD —————————
@admin.route('/admin/extra_services')
@login_required
@admin_required
def admin_extra_services():
    services = ExtraService.query.all()
    return render_template('admin/extra_services.html', services=services)


@admin.route('/admin/extra_services/create', methods=['GET','POST'])
@login_required
@admin_required
def admin_create_extra_service():
    form = ExtraServiceForm()
    if form.validate_on_submit():
        es = ExtraService(
            name       = form.name.data,
            description= form.description.data,
            price      = form.price.data,
            type       = form.type.data,
            per_adult  = form.per_adult.data          # ← SAVE IT
        )
        db.session.add(es)
        db.session.commit()
        flash('Extra service created.', 'success')
        return redirect(url_for('admin.admin_extra_services'))
    return render_template('admin/extra_service_form.html', form=form, title='Create Extra Service')

@admin.route('/admin/extra_services/edit/<int:svc_id>', methods=['GET','POST'])
@login_required
@admin_required
def admin_edit_extra_service(svc_id):
    es = ExtraService.query.get_or_404(svc_id)
    form = ExtraServiceForm(obj=es)
    if form.validate_on_submit():
        form.populate_obj(es)   # this will fill per_adult too
        db.session.commit()
        flash('Extra service updated.', 'success')
        return redirect(url_for('admin.admin_extra_services'))
    return render_template('admin/extra_service_form.html', form=form, title='Edit Extra Service')


@admin.route('/admin/extra_services/delete/<int:svc_id>')
@login_required
@admin_required
def admin_delete_extra_service(svc_id):
    es = ExtraService.query.get_or_404(svc_id)
    db.session.delete(es)
    db.session.commit()
    flash('Extra service deleted.', 'warning')
    return redirect(url_for('admin.admin_extra_services'))


# ————————— Guest Options CRUD —————————
@admin.route('/admin/guest_options')
@login_required
@admin_required
def admin_guest_options():
    opts = GuestOption.query.all()
    return render_template('admin/guest_options.html', opts=opts)


@admin.route('/admin/guest_options/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_create_guest_option():
    form = GuestOptionForm()
    
    if form.validate_on_submit():
        adult = form.adult_count.data
        child = form.child_count.data or 0  

        label = f"{adult} Adult{'s' if adult > 1 else ''}"
        if child:
            label += f", {child} Child{'ren' if child > 1 else ''}"

        go = GuestOption(
            adult_count=adult,
            child_count=child,
            label=label
        )
        db.session.add(go)
        db.session.commit()
        flash('Guest option created.', 'success')
        return redirect(url_for('admin.admin_guest_options'))

    return render_template('admin/guest_option_form.html', form=form, title='Create Guest Option')



@admin.route('/admin/guest_options/edit/<int:opt_id>', methods=['GET','POST'])
@login_required
@admin_required
def admin_edit_guest_option(opt_id):
    go = GuestOption.query.get_or_404(opt_id)
    form = GuestOptionForm(obj=go)
    if form.validate_on_submit():
        form.populate_obj(go)
        db.session.commit()
        flash('Guest option updated.', 'success')
        return redirect(url_for('admin.admin_guest_options'))
    return render_template('admin/guest_option_form.html', form=form, title='Edit Guest Option')


@admin.route('/admin/guest_options/delete/<int:opt_id>')
@login_required
@admin_required
def admin_delete_guest_option(opt_id):
    go = GuestOption.query.get_or_404(opt_id)
    db.session.delete(go)
    db.session.commit()
    flash('Guest option deleted.', 'warning')
    return redirect(url_for('admin.admin_guest_options'))
