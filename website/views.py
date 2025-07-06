from flask import Blueprint as bl, render_template

views = bl('views', __name__)

@views.route('/')
def login():
    return render_template("login.html")