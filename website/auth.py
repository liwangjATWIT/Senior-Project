from flask import Blueprint as bl, render_template, request, flash, redirect, url_for, session

auth = bl('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email == "admin@example.com" and password == "password":
            session['user'] = email
            flash("Login successful!", category="success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", category="error")
    return render_template("login.html")

@auth.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", category="success")
    return render_template("logout.html")

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 4:
            flash('Email mush be greater than 4 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name mush be greater than 1 character.', category='error')
        elif len(lastName) < 2:
            flash('Last name mush be greater than 2 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 12:
            flash('Password must be at least 12 characters.', category='error')
        else:
            flash('Account created!', category='success')

    return render_template("sign_up.html")

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # Simulated password reset logic
        if email == "admin@example.com":
            flash("Reset link sent to your email.", category="success")
        else:
            flash("If that email is registered, a reset link will be sent.", category="success")
        return render_template("login.html")  # or redirect to login
    return render_template("forgot_password.html")

@auth.route('/dashboard')
def dashboard():
    if not session.get('user'):
        flash("Please log in to view the dashboard.", category="error")
        return redirect(url_for('auth.login'))
    return render_template("dashboard.html")