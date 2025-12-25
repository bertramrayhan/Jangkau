from flask import Blueprint, render_template, request, session
from sqlalchemy import or_, func

from models import Lomba, Tag

home_bp = Blueprint("home", __name__)

def get_filtered_lomba(page, query_param, selected_tags, is_free, lokasi):
    PER_PAGE = 6
    base_query = Lomba.query

    if is_free is not None:
        base_query = base_query.filter(Lomba.is_free == is_free)
    
    if lokasi is not None:
        base_query = base_query.filter(Lomba.location == lokasi)

    if query_param:
        search_term = f"%{query_param}%"
        
        search_filter = or_(
            Lomba.title.ilike(search_term),
            Lomba.location_details.ilike(search_term),
            Lomba.organizer.ilike(search_term),
            # Tambahkan kolom lain di sini jika perlu
            # Lomba.raw_description.ilike(search_term) 

            Lomba.tags.any(Tag.name.ilike(search_term))
        )
        
        # Terapkan filter ke query dasar
        base_query = base_query.filter(search_filter)

    if selected_tags:
        # Terjemahan: "Cari Lomba yang, setelah di-JOIN dengan tags,
        #              memiliki nama tag yang ada di dalam daftar selected_tags,
        #              dan jumlah tag yang cocok sama dengan jumlah tag yang dipilih."
        base_query = base_query.join(Lomba.tags).filter(Tag.name.in_(selected_tags)).group_by(Lomba.id).having(func.count(Tag.id) == len(selected_tags))

    # Lanjutkan dengan ordering dan pagination
    pagination = base_query.distinct().order_by(Lomba.registration_end.desc()).paginate(
        page=page, 
        per_page=PER_PAGE, 
        error_out=False
    )
    return pagination

@home_bp.route("/")
def index():
    page = request.args.get('page', 1, type=int)
    query_param = request.args.get('q', '', type=str)
    selected_tags = request.args.getlist('tags')
    lokasi = request.args.get('lokasi')

    is_free = None
    free_param = request.args.get('tipe_lomba')
    if free_param is not "all" and free_param is not None:
        # Convert string ke boolean
        is_free = free_param.lower() in ['true', '1', 'yes', 'on']

    pagination = get_filtered_lomba(page, query_param, selected_tags, is_free, lokasi)
    list_lomba = pagination.items

    session['previous_url'] = request.url

    if request.headers.get('HX-Request'):
        return render_template(
            "partials/content.html", 
            list_lomba=list_lomba, 
            pagination=pagination,
            query=query_param,
            selected_tags=selected_tags,
            tipe_lomba=free_param,
            lokasi=lokasi
        )
    
    list_tags = Tag.query.order_by(Tag.name.asc()).all()

    return render_template(
        "index.html", 
        list_lomba=list_lomba, 
        pagination=pagination,
        query=query_param,
        list_tags=list_tags,
        selected_tags=selected_tags,
        tipe_lomba=free_param,
        lokasi=lokasi
    )