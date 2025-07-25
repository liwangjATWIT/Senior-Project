from flask import Blueprint as bl, render_template, request, flash, redirect, url_for, session
from .models import User, db
from datetime import datetime
import re
from transformers import AutoTokenizer, AutoModelForCausalLM  # type: ignore
import torch  # type: ignore

auth = bl('auth', __name__)

tokenizer = AutoTokenizer.from_pretrained("unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit")
# model = AutoModelForCausalLM.from_pretrained("unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit")
model = AutoModelForCausalLM.from_pretrained(
    "unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit",
    device_map="auto",
    load_in_4bit=True,
    torch_dtype=torch.float16,
)


# Move model to GPU if available, else CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Set model to evaluation mode
model.eval()

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(input_string):
    return input_string.strip() if input_string else ""

device = next(model.parameters()).device
def generate_itinerary(origin, destination, departure_date, return_date):
    start_date = datetime.strptime(departure_date, "%Y-%m-%d")
    end_date = datetime.strptime(return_date, "%Y-%m-%d")
    days = (end_date - start_date).days + 1
    prompt = f"""
    You are a helpful travel assistant. Based on the trip details below, generate a detailed, realistic daily travel itinerary with **approximate times** for each meal and activity.

    Trip Details:
    - Origin: {origin}
    - Destination: {destination}
    - Travel Dates: {start_date} to {end_date}
    - Trip Length: {days} days

    Day 1:
    - Begin with a morning flight from the origin to the destination.
    - Do not include breakfast.
    - After check-in, the traveler should **rest for the afternoon**.
    - Include **only one specific named attraction in the early evening**, followed by dinner and return to hotel.
    - No more than 1 attraction or activity this day.

    Day {days} (Final Day):
    - Only include **one light attraction in the morning**.
    - After lunch, traveler must **check out** and take a **flight from {destination} to {origin}**.
    - ❗ Do **not** include anything after the flight.
    - ❗ End the itinerary with exactly: `flight from {destination} to {origin}`

    Days 2 to {days - 1}:
    - Include **2 to 3 named attractions or activities**.
    - Ensure a mix of museums, landmarks, parks, and local restaurants or food spots.
    - Attractions must be real, not generic phrases.
    - Space them out reasonably (morning, afternoon, evening), with breaks for lunch and dinner.

    Format:
    YYYY-MM-DD  
    Breakfast at [place] — 8:30 AM  
    Morning: [Attraction 1] — 10:00 AM  
    Lunch at [place] — 12:30 PM  
    Afternoon: [Attraction 2] — 2:00 PM  
    (Optional) Evening: [Attraction or scenic walk] — 5:00 PM  
    Dinner at [place] — 7:00 PM  
    Return to hotel
    """

    try:
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=600,
            do_sample=False,           # Greedy decoding for focused output
            temperature=0.3,           # Low temperature for less randomness
            top_p=0.9,
            repetition_penalty=1.1,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id
        )
        # Decode only new tokens
        generated_text = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[-1]:],
            skip_special_tokens=True
        )

        date_pattern = r"\w+day, \w+ \d{1,2}, \d{4}"  # e.g., Friday, July 25, 2025

        itinerary = []
        current_day = ""
        current_date = ""
        seen = set()

        for line in generated_text.strip().split("\n"):
            clean_line = line.strip()
            if not clean_line or clean_line in seen:
                continue
            seen.add(clean_line)

            # Detect 'Day N: Date' line
            if clean_line.startswith("Day "):
                parts = clean_line.split(":", 1)
                current_day = parts[0].strip()
                if len(parts) > 1:
                    match = re.search(date_pattern, parts[1])
                    current_date = match.group(0) if match else ""
                else:
                    current_date = ""
                continue

            # Detect line that is just a date
            if re.match(date_pattern, clean_line):
                current_date = clean_line
                continue

            # Otherwise it's an activity line
            itinerary.append({
                'day': current_day,
                'date': current_date,
                'activities': clean_line
            })

        return itinerary

    except Exception as e:
        print(f"Error generating itinerary: {e}")
        return []

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
