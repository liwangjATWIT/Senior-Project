from flask import Blueprint as bl, render_template, session, redirect, url_for, flash

views = bl('views', __name__)

@views.route('/')
def home():
    user = session.get('user')
    if not user:
        flash("Please log in first.", category="error")
        return redirect(url_for('auth.login'))

    # Get all the travel data from session
    itinerary = session.get('itinerary', [])  # Use .get() instead of .pop() to keep data
    destination = session.get('destination', 'New York, NY')  # Get destination from session
    origin = session.get('origin', '')
    departure_date = session.get('departure_date', '')
    return_date = session.get('return_date', '')
    
    return render_template('home.html', 
                         user=user, 
                         itinerary=itinerary,
                         destination=destination,
                         origin=origin,
                         departure_date=departure_date,
                         return_date=return_date)