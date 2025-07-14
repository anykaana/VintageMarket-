from ext import app, db
from routes import User

with app.app_context():

    db.drop_all()
    db.create_all()

    with app.app_context():
        db.drop_all()
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                role='Admin'
            )
            admin_user.password = 'admin123'
            db.session.add(admin_user)
            db.session.commit()
