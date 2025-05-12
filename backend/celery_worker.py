from app import create_app, make_celery
from app import tasks

app = create_app()
celery = make_celery(app)

if __name__ == '__main__':
    app.app_context().push()