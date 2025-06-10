from flask import Blueprint as bl

views = bl('views', __name__)

@views.route('/')
def home():
    return "<h1>Hello Worlds</h1>"