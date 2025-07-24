from flask import Blueprint as bl, render_template, session, redirect, url_for, flash

views = bl('views', __name__)

@views.route('/')
def home():
    user = session.get('user')
    if not user:
        flash("Please log in first.", category="error")
        return redirect(url_for('auth.login'))

    itinerary = session.pop('itinerary', None)
    return render_template('home.html', user=user, itinerary=itinerary)
