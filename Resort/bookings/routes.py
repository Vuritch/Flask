from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session
)
from datetime import datetime
from flask_login import login_required, current_user

from Resort.models import (
    db,
    RoomType,
    Room,
    ExtraService,
    GuestOption,
    Booking,
    BookingExtraService,
    Guest,
)
from Resort.bookings.forms import GuestForm

bookings = Blueprint('bookings', __name__, url_prefix='/bookings')


@bookings.route('/booking', methods=['GET', 'POST'])
@login_required
def booking():
    """Stage 1: choose dates/room/extras → stash in session (no DB write)."""
    today          = datetime.now().date().isoformat()
    room_types     = RoomType.query.options(db.joinedload(RoomType.rooms)).all()
    dining_extras  = ExtraService.query.filter_by(type='dining').all()
    service_extras = ExtraService.query.filter_by(type='service').all()
    bed_extras     = ExtraService.query.filter_by(type='bed').all()
    guest_options  = GuestOption.query.order_by(
                         GuestOption.adult_count,
                         GuestOption.child_count
                     ).all()

    if request.method == 'POST':
        try:
            room_type_id     = int(request.form['room_type_id'])
            check_in         = datetime.strptime(request.form['check_in'],  '%Y-%m-%d').date()
            check_out        = datetime.strptime(request.form['check_out'], '%Y-%m-%d').date()
            special_requests = request.form.get('special_requests', '')

            guest_option_id = int(request.form['guests'])
            guest_opt = GuestOption.query.get(guest_option_id)
            if not guest_opt:
                flash("Invalid guest selection.", "danger")
                return redirect(url_for('bookings.booking'))
            total_guests = guest_opt.adult_count + guest_opt.child_count

            room_type = RoomType.query.get(room_type_id)
            if not room_type:
                flash("Room type not found.", "danger")
                return redirect(url_for('bookings.booking'))
            if total_guests > room_type.max_guests:
                flash(f"That room holds up to {room_type.max_guests} guests only.", "warning")
                return redirect(url_for('bookings.booking'))

            room = Room.query.filter_by(
                room_type_id=room_type_id, is_available=True
            ).first()
            if not room:
                flash("No available rooms of that type.", "danger")
                return redirect(url_for('bookings.booking'))

            # financials
            room_rate       = float(request.form.get('room_rate', 0))
            taxes_and_fees  = float(request.form.get('taxes_and_fees', 0))
            dining_total    = float(request.form.get('dining_total', 0))
            services_total  = float(request.form.get('services_total', 0))
            total_price     = float(request.form.get('total_price', 0))

            extras_ids = [int(x) for x in request.form.getlist('extras')]
            dining_id  = request.form.get('dining_package')
            dining_id  = int(dining_id) if dining_id else None

            session['pending_booking'] = {
                'user_id':          current_user.id,
                'room_id':          room.id,
                'check_in':         check_in.isoformat(),
                'check_out':        check_out.isoformat(),
                'guest_option_id':  guest_option_id,
                'special_requests': special_requests,
                'bed_preference':   request.form.get('bed_preference',''),
                'dining_id':        dining_id,
                'extras':           extras_ids,
                'room_rate':        room_rate,
                'taxes_and_fees':   taxes_and_fees,
                'dining_total':     dining_total,
                'services_total':   services_total,
                'total_price':      total_price,
            }
            return redirect(url_for('bookings.guest'))

        except Exception as e:
            flash(f"Error parsing booking: {e}", "danger")
            return redirect(url_for('bookings.booking'))

    return render_template(
        "booking.html",
        title="Book Your Stay",
        today=today,
        room_types=room_types,
        dining_extras=dining_extras,
        service_extras=service_extras,
        bed_extras=bed_extras,
        guest_options=guest_options,
    )


@bookings.route('/guest', methods=['GET', 'POST'])
@login_required
def guest():
    form = GuestForm()
    if form.validate_on_submit():
        session['guest_data'] = {
            'guest_name':        form.guest_name.data,
            'guest_age':         form.guest_age.data,
            'guest_email':       form.guest_email.data,
            'guest_address':     form.guest_address.data,
            'guest_phone':       form.guest_phone.data,
            'guest_nationality': form.guest_nationality.data,
        }
        flash('Guest data saved. Please confirm and pay.', 'success')
        return redirect(url_for('bookings.confirm_booking'))

    return render_template('guest.html', form=form)


@bookings.route('/confirm_booking', methods=['GET', 'POST'])
@login_required
def confirm_booking():
    pending = session.get('pending_booking')
    guest_d = session.get('guest_data')
    if not pending or not guest_d:
        flash("Session expired; please start over.", "warning")
        return redirect(url_for('bookings.booking'))

    if request.method == 'POST':
        return redirect(url_for('bookings.payment'))

    room     = Room.query.get(pending['room_id'])
    opt      = GuestOption.query.get(pending['guest_option_id'])
    dining   = ExtraService.query.get(pending['dining_id']) if pending['dining_id'] else None
    services = [
        ExtraService.query.get(eid)
        for eid in pending['extras']
        if ExtraService.query.get(eid).type == 'service'
    ]

    return render_template(
        'confirm_booking.html',
        guest=guest_d,
        pending=pending,
        room=room,
        opt=opt,
        dining=dining,
        services=services
    )


@bookings.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    pending = session.get('pending_booking')
    guest_d = session.get('guest_data')
    if not pending or not guest_d:
        flash("Session expired; please start over.", "warning")
        return redirect(url_for('bookings.booking'))

    if request.method == 'GET':
        room = Room.query.get(pending['room_id'])
        return render_template('payment.html', pending=pending, room=room)

    # --- POST: validate and “charge” ---
    holder = request.form.get('card_holder')
    number = request.form.get('card_number')
    expiry = request.form.get('expiry')
    cvv    = request.form.get('cvv')
    if not all([holder, number, expiry, cvv]):
        flash("Fill in all payment fields.", "warning")
        return redirect(url_for('bookings.payment'))

    # TODO: real gateway call here…
    if False:  # replace with your payment check
        flash("Payment failed.", "danger")
        return redirect(url_for('bookings.payment'))

    try:
        # 1) Create Booking
        room      = Room.query.get(pending['room_id'])
        check_in  = datetime.fromisoformat(pending['check_in']).date()
        check_out = datetime.fromisoformat(pending['check_out']).date()
        opt       = GuestOption.query.get(pending['guest_option_id'])

        booking = Booking(
            user_id          = pending['user_id'],
            room_id          = room.id,
            check_in         = check_in,
            check_out        = check_out,
            num_adults       = opt.adult_count,
            num_children     = opt.child_count,
            bed_preference   = pending['bed_preference'],
            dining_package   = ExtraService.query.get(pending['dining_id']).name
                                if pending['dining_id'] else None,
            room_rate        = pending['room_rate'],
            taxes_and_fees   = pending['taxes_and_fees'],
            dining_total     = pending['dining_total'],
            services_total   = pending['services_total'],
            total_price      = pending['total_price'],
            special_requests = pending['special_requests'],
            status           = 'paid'
        )
        db.session.add(booking)
        db.session.flush()

        # 2) Extras
        for eid in pending['extras']:
            svc = ExtraService.query.get(eid)
            if svc and svc.type == 'service':
                db.session.add(BookingExtraService(
                    booking_id       = booking.id,
                    extra_service_id = svc.id
                ))

        # 3) Create Guest and link it
        guest = Guest(
            guest_name        = guest_d['guest_name'],
            guest_age         = guest_d['guest_age'],
            guest_email       = guest_d['guest_email'],
            guest_address     = guest_d['guest_address'],
            guest_phone       = guest_d['guest_phone'],
            guest_nationality = guest_d['guest_nationality'],
        )
        db.session.add(guest)
        db.session.flush()   # now guest.guest_id is set

        # Link the booking → guest FK
        booking.guest_id = guest.guest_id

        # 4) Mark room unavailable
        room.is_available = False

        db.session.commit()

        # cleanup
        session.pop('pending_booking', None)
        session.pop('guest_data', None)

        flash("Payment successful! Thank you.", "success")
        return redirect(url_for('bookings.booking_summary', booking_id=booking.id))

    except Exception as e:
        db.session.rollback()
        flash(f"Error completing booking: {e}", "danger")
        return redirect(url_for('bookings.payment'))


@bookings.route('/booking_summary/<int:booking_id>')
@login_required
def booking_summary(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    guest   = booking.guest
    return render_template(
        'booking_summary.html',
        booking=booking,
        guest=guest
    )


@bookings.route('/my_bookings')
@login_required
def my_bookings():
    all_b = Booking.query.filter_by(user_id=current_user.id) \
                        .order_by(Booking.check_in.desc()) \
                        .all()
    return render_template('my_bookings.html', bookings=all_b)
