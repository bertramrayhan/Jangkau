from flask import Blueprint, render_template
from helpers import get_db_connection
from models import Lomba

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def index():
    conn = get_db_connection()
    list_lomba = Lomba.query.limit(6).all()

    return render_template("index.html", list_lomba=list_lomba)
