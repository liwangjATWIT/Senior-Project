from flask import Flask as fs

def create_app(secrete_key: str):
    app = fs(__name__)
    app.config['SECRETE_KEY'] = secrete_key

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app