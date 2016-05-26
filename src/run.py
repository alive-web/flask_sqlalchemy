__author__ = 'plevytskyi'
import os
from app import app, db

db.create_all()
port = os.getenv('PORT', 5000)
app.run(host='0.0.0.0', port=port, debug=True)