from flask import Blueprint as bl, render_template, request, flash

auth = bl('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
# '/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return "<p>Logout</p>"

@auth.route('/sign-up', methods=['GET', 'POST'])
# '/sign-up', methods=['GET', 'POST'])
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