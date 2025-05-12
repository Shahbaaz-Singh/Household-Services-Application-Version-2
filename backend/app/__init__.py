from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from celery import Celery
from config import Config
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
cache = Cache()
limiter = Limiter(get_remote_address, storage_uri="redis://localhost:6379/0")
jwt = JWTManager()
mail = Mail()

celery = None

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    )
    celery.conf.update(app.config)
    return celery

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    app.config['SECRET_KEY'] = 'secret-key'
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'
    app.config['JWT_ALGORITHM'] = 'HS256'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///household_services.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    
    Migrate(app, db)
    
    CORS(app)
    
    global celery
    celery = make_celery(app)
    
    from .routes import main
    app.register_blueprint(main)
    
    with app.app_context():
        db.create_all()
    
    return app
