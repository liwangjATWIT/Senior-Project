from flask import Blueprint as bl, render_template

views = bl('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")