__author__ = 'plevytskyi'
from app import User, db

db.create_all()

admin = User('admin', 'admin@example.com')
guest = User('guest', 'guest@example.com')

db.session.add(admin)
db.session.add(guest)
db.session.commit()
print admin