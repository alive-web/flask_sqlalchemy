__author__ = 'plevytskyi'
import os
from app import app, db

db.create_all()
port = os.getenv('PORT', 5000)
hostname = os.getenv('URL', 'secret-forest-72981.herokuapp.com')
print('port={}, hostname={}'.format(port, hostname))
app.run(hostname=hostname, port=port, debug=True)