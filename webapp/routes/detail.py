from flask import Blueprint, render_template, request, url_for
from models import Lomba, Tag
from sqlalchemy import and_

detail_bp = Blueprint("detail", __name__)

@detail_bp.route('/detail/<int:id>')
def index(id):
    lomba = Lomba.query.get_or_404(id)
    
    similar_lomba = get_similar_lomba(lomba, limit=3)

    # Dapatkan referrer URL (halaman sebelumnya)
    referrer = request.headers.get('Referer')
    
    # Logic untuk back_url yang smart
    # 1. Jika ada parameter 'from' di URL, gunakan itu
    from_url = request.args.get('from')
    if from_url:
        back_url = from_url
    # 2. Jika referrer dari halaman home, gunakan itu
    elif referrer and request.host in referrer and not '/detail/' in referrer:
        back_url = referrer
    # 3. Default ke home
    else:
        back_url = url_for('home.index')
    
    return render_template('detail.html', lomba=lomba, back_url=back_url, similar_lomba=similar_lomba)

def get_similar_lomba(current_lomba, limit=3):
    # Ambil semua tag dari lomba saat ini
    current_tag_ids = [tag.id for tag in current_lomba.tags]
    
    # Kalau lomba saat ini tidak ada tag sama sekali
    if not current_tag_ids:
        # Fallback: return lomba terbaru
        return Lomba.query.filter(Lomba.id != current_lomba.id).order_by(Lomba.created_at.desc()).limit(limit).all()
    
    # Query lomba yang memiliki minimal 1 tag yang sama
    similar_lomba = Lomba.query.filter(
        and_(
            Lomba.tags.any(Tag.id.in_(current_tag_ids)),
            Lomba.id != current_lomba.id
        )
    ).all()
    
    # Hitung similarity score dan sort
    scored_lomba = []
    for lomba in similar_lomba:
        lomba_tag_ids = [tag.id for tag in lomba.tags]
        shared_tags = set(current_tag_ids) & set(lomba_tag_ids)
        similarity_score = len(shared_tags)
        scored_lomba.append((lomba, similarity_score))
    
    # Sort by similarity score (descending)
    scored_lomba.sort(key=lambda x: x[1], reverse=True)
    
    # Ambil top N lomba
    result_lomba = [lomba for lomba, score in scored_lomba[:limit]]

    return result_lomba