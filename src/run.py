__author__ = 'plevytskyi'
import os
from app import app, db

db.create_all()
port = os.getenv('PORT', 5000)
hostname = os.getenv('URL', 'hostname')
print('port={}, hostname={}'.format(port, hostname))
app.run(debug=True, port=port)