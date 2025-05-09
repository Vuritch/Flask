from flask import render_template, request, redirect, url_for, flash,session
from Resort.models import db, Booking
from Resort.bookings import bookings 
from datetime import  datetime
from functools import wraps
from flask_login import login_required, current_user
from Resort.models import  db, User,Room, ExtraService, Booking, BookingExtraService,RoomType,Guest,GuestOption

from Resort.bookings.forms import GuestForm 



# The custom login_required decorator is now removed, using Flask-Login's instead

@bookings.route("/booking", methods=['GET', 'POST'])
@login_required
def booking():
    today = datetime.now().date().isoformat()
    room_types = RoomType.query.options(db.joinedload(RoomType.rooms)).all()
    extra_services = ExtraService.query.all()
    dining_extras = ExtraService.query.filter_by(type='dining').all()
    service_extras = ExtraService.query.filter_by(type='service').all()
    bed_extras = ExtraService.query.filter_by(type='bed').all()
    guest_options = GuestOption.query.\
         order_by(GuestOption.adult_count, GuestOption.child_count).all()
    if request.method == 'POST':
        try:
            # basic form fields
            room_type_id = int(request.form['room_type_id'])
            check_in  = datetime.strptime(request.form['check_in'], '%Y-%m-%d').date()
            check_out = datetime.strptime(request.form['check_out'], '%Y-%m-%d').date()
            special_requests = request.form.get('special_requests','')

            # fetch the selected GuestOption by its ID
            guest_option_id = int(request.form['guests'])
            guest_opt = GuestOption.query.get(guest_option_id)
            if not guest_opt:
                flash("Invalid guest selection.", "danger")
                return redirect(url_for('bookings.booking'))

            adults   = guest_opt.adult_count
            children = guest_opt.child_count
            total    = adults + children


            # load room_type and enforce max_guests
            room_type = RoomType.query.get(room_type_id)
            if not room_type:
                flash("Room type not found.", "danger")
                return redirect(url_for('bookings.booking'))
            if total > room_type.max_guests:
                flash(f"That room holds up to {room_type.max_guests} guests only.", "warning")
                return redirect(url_for('bookings.booking'))

            # extras/dining/bed as before …
            extras       = request.form.getlist('extras')
            dining_pkg   = request.form.get('dining_package')
            # … split out bed_pref and service_extras …

            # financials from hidden inputs
            room_rate    = float(request.form.get('room_rate', 0))
            taxes_and_fees = float(request.form.get('taxes_and_fees',0))
            dining_total = float(request.form.get('dining_total',0))
            services_total = float(request.form.get('services_total',0))
            total_price  = float(request.form.get('total_price',0))
            
            # pick an available room
            room = Room.query.filter_by(room_type_id=room_type_id, is_available=True).first()
            if not room:
                flash("No available rooms of that type.", "danger")
                return redirect(url_for('bookings.booking'))

            # create booking
            booking = Booking(  #استخدمها بدل session
                user_id=current_user.id,
                room_id=room.id,
                check_in=check_in,
                check_out=check_out,
                bed_preference=request.form.get('bed_preference',''),
                dining_package = ExtraService.query.get(int(dining_pkg)).name if dining_pkg else None,
                room_rate=room_rate,
                taxes_and_fees=taxes_and_fees,
                dining_total=dining_total,
                services_total=services_total,
                total_price=total_price,
                
                # new columns (if you added them)
                num_adults=adults,
                num_children=children,

                special_requests=special_requests,
                status='pending'
            )
            db.session.add(booking)
            db.session.flush()  # so booking.id exists

            # record each child’s age category
           # for age_cat in request.form.getlist('child_ages'):
                #db.session.add(BookingGuest(booking_id=booking.id, age=age_cat))

         
            # link service extras as before
            for e_id in [int(x) for x in extras]:
                svc = ExtraService.query.get(e_id)
                if svc and svc.type=='service':
                    db.session.add(BookingExtraService(
                        booking_id=booking.id,
                        extra_service_id=svc.id
                    ))

            # mark room unavailable
            room.is_available = False
            db.session.commit()

            flash("Booking successful! Check your email for confirmation.", "success")
            return redirect(url_for('bookings.guest'))

        except Exception as e:
            db.session.rollback()
            flash("Error processing booking: " + str(e), "danger")
            return redirect(url_for('bookings.booking'))

    included_adults   = 2 
    extra_adult_price = 20
    
    return render_template(
        "booking.html",
        title="Book Your Stay",
        today=today,
        room_types=room_types,
        dining_extras=dining_extras,
        service_extras=service_extras,
        bed_extras=bed_extras,
        guest_options=guest_options,
        included_adults=included_adults,
        extra_adult_price=extra_adult_price
    )



@bookings.route('/my_bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.check_in.desc()).all()
    return render_template('my_bookings.html', bookings=bookings)



@bookings.route('/guest', methods=['GET', 'POST'])
@login_required
def guest():
    form = GuestForm()
    
    if form.validate_on_submit():
        
        guest_data = {
            'guest_name': form.guest_name.data,
            'guest_age': form.guest_age.data,
            'guest_email': form.guest_email.data,
            'guest_address': form.guest_address.data,
            'guest_phone': form.guest_phone.data,
            'guest_nationality': form.guest_nationality.data
        }
        
        session['guest_data'] = guest_data

        flash('Guest data saved temporarily. You can proceed to confirm the booking.', 'success')
        return redirect(url_for('bookings.confirm_booking')) 

    return render_template('guest.html', form=form)



@bookings.route('/confirm_booking', methods=['GET','POST'])
@login_required
def confirm_booking():
    guest_data = session.get('guest_data')
    if not guest_data:
        flash("No guest data found. Please fill in the form first.", "warning")
        return redirect(url_for('guest'))  

    latest_booking = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.id.desc()).first()
    if not latest_booking:
        flash("No booking found to confirm.", "danger")
        return redirect(url_for('bookings.booking')) 

    if request.method == 'POST':
        flash("Guest details confirmed. Proceed to payment.", "success")
        return redirect(url_for('bookings.payment', booking_id=latest_booking.id))

    return render_template('confirm_booking.html', guest_data=guest_data, booking=latest_booking)







@bookings.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    guest_data = session.get('guest_data')  # يجب أن يكون محفوظًا

    if request.method == 'POST':
        card_number = request.form.get('card_number')
        expiry = request.form.get('expiry')
        cvv = request.form.get('cvv')
        card_holder = request.form.get('card_holder')

        if not all([card_number, expiry, cvv, card_holder]):
            flash("Please fill in all payment fields.", "warning")
            return redirect(url_for('bookings.payment', booking_id=booking_id))

        try:
            # أنشئ الضيف الآن
            guest = Guest(
                guest_name=guest_data['guest_name'],
                guest_age=guest_data['guest_age'],
                guest_email=guest_data['guest_email'],
                guest_address=guest_data['guest_address'],
                guest_phone=guest_data['guest_phone'],
                guest_nationality=guest_data['guest_nationality']
            )
            db.session.add(guest)
            db.session.flush()  # حتى نتمكن من استخدام guest.guest_id

            # حدث الحجز
            booking.status = 'paid'
            booking.guest_id = guest.guest_id
            db.session.commit()

            session.pop('guest_data', None)

            flash("Payment successful! Thank you.", "success")
            return redirect(url_for('bookings.booking_summary', booking_id=booking.id))

        except Exception as e:
            db.session.rollback()
            flash("Error during payment: " + str(e), "danger")
            return redirect(url_for('bookings.payment', booking_id=booking_id))

    return render_template('payment.html', booking=booking)



@bookings.route('/booking_summary/<int:booking_id>')
@login_required
def booking_summary(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    guest = booking.guest

    return render_template('booking_summary.html', booking=booking, guest=guest)


