from flask import Flask, Blueprint, render_template
from helpers import convert_to_id_date, get_domain_from_url
from routes import home_bp, detail_bp
from models import db
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

ENV = os.getenv('APP_ENV', 'development')

if ENV == 'production':
    # MODE PRODUKSI (saat di Vercel)
    print("🚀 Running in PRODUCTION mode. Connecting to Postgres...")
    db_url = os.getenv('DATABASE_URL')
    
    # Perbaikan kecil: SQLAlchemy lebih suka 'postgresql://' daripada 'postgres://'
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    # MODE PENGEMBANGAN (saat di komputer lokal)
    print("💻 Running in DEVELOPMENT mode. Connecting to SQLite...")
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(BASE_DIR, '..', 'database', 'jangkau.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db.init_app(app)

def apply_filters(app):
    app.jinja_env.filters["convert_to_id_date"] = convert_to_id_date
    app.jinja_env.filters["get_domain_from_url"] = get_domain_from_url

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('404.html'), 500  # Untuk sementara gunakan 404 template

tentang_bp = Blueprint("tentang", __name__)
@tentang_bp.route("/tentang")
def index():
    return render_template('tentang.html')

def register_routes(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(detail_bp)
    app.register_blueprint(tentang_bp)

apply_filters(app)
register_routes(app)
register_error_handlers(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000)