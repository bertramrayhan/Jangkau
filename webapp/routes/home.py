from flask import Blueprint, render_template, request
from sqlalchemy import or_  # <-- IMPORT FUNGSI 'or_'

from models import Lomba

home_bp = Blueprint("home", __name__)

def get_filtered_lomba(page, query_param):
    PER_PAGE = 6
    base_query = Lomba.query

    if query_param:
        search_term = f"%{query_param}%"
        
        search_filter = or_(
            Lomba.title.ilike(search_term),
            Lomba.location_details.ilike(search_term),
            Lomba.organizer.ilike(search_term)
            # Tambahkan kolom lain di sini jika perlu
            # Lomba.raw_description.ilike(search_term) 
        )
        
        # Terapkan filter ke query dasar
        base_query = base_query.filter(search_filter)

    # Lanjutkan dengan ordering dan pagination
    pagination = base_query.order_by(Lomba.registration_end.desc()).paginate(
        page=page, 
        per_page=PER_PAGE, 
        error_out=False
    )
    return pagination

@home_bp.route("/")
def index():
    page = request.args.get('page', 1, type=int)
    query_param = request.args.get('q', '', type=str)

    pagination = get_filtered_lomba(page, query_param)
    list_lomba = pagination.items

    if request.headers.get('HX-Request'):
        return render_template(
            "partials/content.html", 
            list_lomba=list_lomba, 
            pagination=pagination,
            query=query_param
        )
    
    return render_template(
        "index.html", 
        list_lomba=list_lomba, 
        pagination=pagination,
        query=query_param
    )