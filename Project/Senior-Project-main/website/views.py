from flask import Blueprint as bl, render_template, session, redirect, url_for, request, flash

views = bl('views', __name__)

@views.route('/home')
def home():
    user = session.get('user')
    if not user:
        flash("Please log in first.", category="error")
        return redirect(url_for('auth.login'))

    itinerary = session.get('itinerary')
    
    return render_template('home.html', user=user, itinerary=itinerary)