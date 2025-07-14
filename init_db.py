from ext import db
from ext import app

with app.app_context():
    db.create_all()
