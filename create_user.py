from src import create_app, db
from src.models.admin_user import AdminUser

app = create_app()
with app.app_context():
    u = AdminUser(username="admin")
    u.set_password("1234")
    db.session.add(u)
    db.session.commit()
    print("Admin user created with username 'admin' and password '1234'")