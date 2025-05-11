import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'Shahbaaz-Yeager')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis and Celery configuration
    broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # Redis caching
    CACHE_TYPE = "RedisCache"
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    CACHE_REDIS_URL = "redis://localhost:6379/0"

    # Rate limiting
    RATELIMIT_STORAGE_URL = "redis://localhost:6379/0"
    
    # Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'ShahbaazSingh2825@gmail.com'
    MAIL_PASSWORD = 'bbje axvq hsfb ixip'
    MAIL_DEFAULT_SENDER = 'ShahbaazSingh2825@gmail.com'