from flask import Blueprint as bl, render_template, request, flash, redirect, url_for, session
from .models import User, db
from datetime import datetime
import re
# from transformers import AutoTokenizer, AutoModelForCausalLM  # type: ignore
# import torch  # type: ignore
import requests

auth = bl('auth', __name__)

# # Load GPT-2 model and tokenizer once at server start
# tokenizer = AutoTokenizer.from_pretrained("openai-community/gpt2")
# model = AutoModelForCausalLM.from_pretrained("openai-community/gpt2")
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model.to(device)
# model.eval()

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(input_string):
    return input_string.strip() if input_string else ""



COLAB_API_URL = "https://your-ngrok-url.ngrok-free.app/generate"  # <-- replace with actual URL

def generate_itinerary(origin, destination, departure_date, return_date):
    # Calculate number of days
    from datetime import datetime
    fmt = "%Y-%m-%d"
    try:
        days = (datetime.strptime(return_date, fmt) - datetime.strptime(departure_date, fmt)).days + 1
        if days <= 0:
            raise ValueError("Return date must be after departure date")
    except Exception as e:
        return [{
            'day': 'Error',
            'date': '',
            'activities': f'Invalid date input: {e}'
        }]

    payload = {
        "origin": origin,
        "destination": destination,
        "start_date": departure_date,
        "end_date": return_date,
        "days": days
    }

    try:
        response = requests.post(COLAB_API_URL, json=payload)
        response.raise_for_status()
        result = response.json()

        if "itinerary" in result:
            raw = result["itinerary"]
            # Split by days for your UI
            itinerary = [{"day": f"Day {i+1}", "date": "", "activities": day.strip()} 
                         for i, day in enumerate(raw.split("\n\n")) if day.strip()]
            return itinerary

        return [{"day": "Error", "date": "", "activities": "Unexpected response format"}]

    except Exception as e:
        return [{
            'day': 'Error',
            'date': '',
            'activities': f"Failed to generate itinerary: {e}"
        }]


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email'))
        password = request.form.get('password')
        
        if not email or not password:
            flash("Please fill in all fields.", category="error")
            return render_template("login.html")
        
        if not validate_email(email):
            flash("Please enter a valid email address.", category="error")
            return render_template("login.html")
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user'] = email
            session['user_id'] = user.id
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash("Login successful!", category="success")
            return redirect(url_for('auth.dashboard'))
        else:
            flash("Invalid email or password.", category="error")
            return render_template("login.html")

    return render_template("login.html")

@auth.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    flash("You have been logged out.", category="success")
    return render_template("logout.html")

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email'))
        firstName = sanitize_input(request.form.get('firstName'))
        lastName = sanitize_input(request.form.get('lastName'))
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if not email or not firstName or not lastName or not password1 or not password2:
            flash('Please fill in all fields.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif not validate_email(email):
            flash('Please enter a valid email address.', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(lastName) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 12:
            flash('Password must be at least 12 characters.', category='error')
        else:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('An account with this email already exists.', category='error')
            else:
                try:
                    new_user = User(
                        email=email,
                        first_name=firstName,
                        last_name=lastName
                    )
                    new_user.set_password(password1)
                    
                    db.session.add(new_user)
                    db.session.commit()
                    
                    flash('Account created successfully! Please log in.', category='success')
                    return redirect(url_for('auth.login'))
                except Exception as e:
                    db.session.rollback()
                    flash('An error occurred while creating your account. Please try again.', category='error')

    return render_template("sign_up.html")

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email'))
        
        if not email:
            flash("Please enter your email address.", category="error")
            return render_template("forgot_password.html")
        
        if not validate_email(email):
            flash("Please enter a valid email address.", category="error")
            return render_template("forgot_password.html")
        
        user = User.query.filter_by(email=email).first()
        flash("If that email is registered, a reset link will be sent.", category="success")
        return redirect(url_for('auth.login'))
    
    return render_template("forgot_password.html")

@auth.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('user'):
        flash("Please log in to view the dashboard.", category="error")
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=session['user']).first()
    if not user:
        flash("User not found. Please log in again.", category="error")
        session.pop('user', None)
        session.pop('user_id', None)
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        origin = request.form.get('origin')
        destination = request.form.get('destination')
        departure_date = request.form.get('departureDate')
        return_date = request.form.get('returnDate')

        if origin and destination and departure_date and return_date:
            itinerary = generate_itinerary(origin, destination, departure_date, return_date)
            session['itinerary'] = itinerary
            flash("Itinerary generated successfully!", category="success")
            return redirect(url_for('views.home'))
        else:
            flash("All fields are required to generate your itinerary.", category="error")

    return render_template("dashboard.html", user=user)

@auth.route('/home')
def home():
    user = session.get('user')
    if not user:
        return redirect(url_for('views.home'))

    return render_template('auth_home.html', user=user)
