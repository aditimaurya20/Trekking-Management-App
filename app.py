from flask import Flask
from models import db
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database created!")
    app.run(debug=True)