from flask import Blueprint, jsonify, session
from utils.decorators import login_required
from services import notification_service
from utils.validators import escape_html

bp = Blueprint('notifications', __name__, url_prefix='/api')


@bp.route('/notifications')
@login_required
def notifications():
    ns = notification_service.get_user_notifications(session['user_id'])
    for n in ns:
        n.message = escape_html(n.message)
    return jsonify([{
        'id': n.id,
        'user_id': n.user_id,
        'message': n.message,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat() if n.created_at else None
    } for n in ns])


@bp.route('/notifications/count')
@login_required
def notifications_count():
    count = notification_service.get_unread_count(session['user_id'])
    return jsonify({'count': count})


@bp.route('/notifications/read-all', methods=['POST'])
@login_required
def read_all():
    notification_service.mark_all_read(session['user_id'])
    return jsonify({'ok': True})


@bp.route('/applications/count')
@login_required
def applications_count():
    from services.application_service import get_pending_applications_count
    if session.get('user_role') != 'employer':
        return jsonify({'count': 0})
    count = get_pending_applications_count(session['user_id'])
    return jsonify({'count': count})
