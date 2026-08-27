from extensions import db, socketio
from models.notification import Notification


def get_user_notifications(user_id, limit=30):
    return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(limit).all()


def get_unread_count(user_id):
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()


def mark_all_read(user_id):
    Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()


def create_notification(user_id, message):
    notification = Notification(user_id=user_id, message=message)
    db.session.add(notification)
    db.session.commit()
    return notification


def notify_employer_new_applicant(employer_id, job_title, job_id):
    message = f'متقدم على "{job_title}"'
    create_notification(employer_id, message)
    socketio.emit('new_applicant', {
        'message': message,
        'job_id': str(job_id)
    }, room=f"user_{employer_id}")


def notify_application_status_changed(user_id, message, status):
    create_notification(user_id, message)
    socketio.emit('notification', {
        'message': message,
        'type': status
    }, room=f"user_{user_id}")
