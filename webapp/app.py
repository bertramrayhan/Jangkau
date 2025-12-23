from flask import Flask
from helpers import convert_to_id_date
from routes import home_bp
from models import db
import os

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, '..', 'database', 'jangkau.db')  # satu level ke atas dari webapp
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

app.jinja_env.filters["convert_to_id_date"] = convert_to_id_date

def register_routes(app):
    app.register_blueprint(home_bp)

if __name__ == '__main__':
    register_routes(app)
    app.run(debug=True, port=5000)