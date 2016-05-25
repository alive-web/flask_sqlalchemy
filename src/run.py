__author__ = 'plevytskyi'
import os
from app import app, db

db.create_all()
port = os.getenv('PORT', 5000)
print(port)
app.run(debug=True, port=port)