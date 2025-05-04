from flask import render_template, request, redirect, url_for, flash
from Resort.models import db, Booking
from Resort.bookings import bookings 
from datetime import  datetime
from functools import wraps
from flask_login import login_required, current_user






# The custom login_required decorator is now removed, using Flask-Login's instead

@bookings.route("/booking", methods=['GET', 'POST'])
@login_required  # Using Flask-Login's login_required decorator
def booking():
    if request.method == 'POST':
        try:
            # Get basic form data
            check_in = datetime.strptime(request.form.get('check_in'), '%Y-%m-%d').date()
            check_out = datetime.strptime(request.form.get('check_out'), '%Y-%m-%d').date()
            room_type = request.form.get('room_type')
            guests = request.form.get('guests')
            
            # Get additional form data
            child_ages = ','.join(request.form.getlist('child_ages')) if request.form.getlist('child_ages') else None
            bed_preference = request.form.get('bed_preference')
            special_requests = request.form.get('special_requests')
            
            # Get extras (dining and services)
            extras = request.form.getlist('extras')
            dining_package = next((extra for extra in extras if extra in ['breakfast', 'halfboard', 'fullboard']), None)
            airport_transfer = 'airport' in extras
            spa_package = 'spa' in extras
            romantic_package = 'romantic' in extras
            
            # Get price breakdown
            room_rate = float(request.form.get('room_rate', 0))
            taxes_and_fees = float(request.form.get('taxes_and_fees', 0))
            dining_total = float(request.form.get('dining_total', 0))
            services_total = float(request.form.get('services_total', 0))
            total_price = float(request.form.get('total_price'))
            
          
            # Create new booking
            new_booking = Booking(
                user_id=current_user.id,  # Use current_user instead of session
                room_type=room_type,
                check_in=check_in,
                check_out=check_out,
                guests=guests,
                child_ages=child_ages,
                bed_preference=bed_preference,
                dining_package=dining_package,
                airport_transfer=airport_transfer,
                spa_package=spa_package,
                romantic_package=romantic_package,
                room_rate=room_rate,
                taxes_and_fees=taxes_and_fees,
                dining_total=dining_total,
                services_total=services_total,
                total_price=total_price,
                special_requests=special_requests,
                status='pending'
            )
            
            # Save to database
            db.session.add(new_booking)
            db.session.commit()
            
            # Send confirmation
            flash('''Booking request submitted successfully! 
                  We will confirm your reservation shortly. 
                  A confirmation email will be sent to your registered email address.''', 'success')
            return redirect(url_for('bookings.booking'))
            
        except Exception as e:
            db.session.rollback()
            # Print detailed error information
            import traceback
            print("Booking Error Details:")
            print(str(e))
            print("Traceback:")
            print(traceback.format_exc())
            flash('An error occurred while processing your booking. Please try again.', 'danger')
            return redirect(url_for('bookings.booking'))
        
    # For GET request, pass today's date to template for date validation
    today = datetime.now().date().isoformat()
    return render_template('booking.html', title='Book Your Stay', today=today)




