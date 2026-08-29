from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.validators import sanitize, validate_email, escape_html
from utils.security import (
    generate_csrf_token, generate_reset_token, verify_reset_token,
    check_rate_limit, send_reset_email
)
from utils.decorators import login_required
from services import auth_service

bp = Blueprint('auth', __name__, url_prefix='')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        try:
            email = sanitize(request.form.get('email', ''), 100)
            pw = request.form.get('password', '')
            fn = sanitize(request.form.get('fullname', ''), 100)
            role = 'job_seeker' if sanitize(request.form.get('role', 'seeker'), 20) == 'seeker' else 'employer'

            if not email or not validate_email(email):
                flash('بريد غير صالح', 'error')
                return render_template('index_register.html', page='register')
            if len(pw) < 6:
                flash('كلمة المرور قصيرة', 'error')
                return render_template('index_register.html', page='register')
            if not fn:
                flash('الاسم مطلوب', 'error')
                return render_template('index_register.html', page='register')

            auth_service.register_user(email, pw, fn, role)
            flash('تم الانشاء', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('البريد مسجل', 'error')

    return render_template('index_register.html', page='register')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = sanitize(request.form.get('email', ''), 100)
        pw = request.form.get('password', '')

        if not check_rate_limit(request.remote_addr, attempt_type='login'):
            flash('محاولات كثيرة', 'error')
            return render_template('index_login.html', page='login')
        if not email or not pw:
            flash('جميع الحقول مطلوبة', 'error')
            return render_template('index_login.html', page='login')

        user = auth_service.authenticate_user(email, pw)
        if user:
            session.permanent = True
            role = 'admin' if user.is_admin else user.user_type
            session['user_id'] = user.id
            session['user_name'] = escape_html(user.full_name)
            session['user_role'] = role
            session['user_email'] = user.email
            session['user_created'] = str(user.created_at)[:10] if user.created_at else '---'
            auth_service.update_last_login(user.id)
            flash(f'مرحبا {escape_html(user.full_name)}!', 'success')
            return redirect(url_for('main.dashboard'))

        flash('بيانات خاطئة', 'error')

    return render_template('index_login.html', page='login')


@bp.route('/logout')
def logout():
    session.clear()
    flash('تم الخروج', 'success')
    return redirect(url_for('main.index'))


@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = sanitize(request.form.get('email', ''), 100)
        if not email or not validate_email(email):
            flash('بريد غير صحيح', 'error')
            return render_template('index_forgot_password.html', page='forgot_password')
        if not check_rate_limit(f"reset_{request.remote_addr}", attempt_type='reset'):
            flash('طلبات كثيرة', 'error')
            return render_template('index_forgot_password.html', page='forgot_password')

        user = auth_service.get_user_by_email(email)
        if user:
            send_reset_email(email, url_for('auth.reset_password', token=generate_reset_token(email), _external=True))

        flash('اذا كان البريد مسجل ستتلقى رابط', 'success')
        return redirect(url_for('auth.login'))

    return render_template('index_forgot_password.html', page='forgot_password')


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    email = verify_reset_token(token)
    if not email:
        flash('رابط غير صالح', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        pw = request.form.get('password', '')
        cp = request.form.get('confirm_password', '')
        if pw != cp:
            flash('غير متطابق', 'error')
            return render_template('index_reset_password.html', page='reset_password', token=token)

        from utils.validators import is_valid_password
        v, msg = is_valid_password(pw)
        if not v:
            flash(msg, 'error')
            return render_template('index_reset_password.html', page='reset_password', token=token)

        auth_service.update_user_password(email, pw)
        flash('تم التغيير', 'success')
        return redirect(url_for('auth.login'))

    return render_template('index_reset_password.html', page='reset_password', token=token)


@bp.route('/profile')
@login_required
def profile():
    return render_template('index_profile.html', page='profile')


@bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    try:
        from models.user import User
        from models.profile import Profile
        from extensions import db
        user = User.query.get(session['user_id'])
        if user and user.profile:
            user.profile.phone = sanitize(request.form.get('phone', ''), 20)
            user.profile.location = sanitize(request.form.get('city', ''), 100)
            user.profile.bio = sanitize(request.form.get('bio', ''), 500)
            db.session.commit()
        flash('تم التحديث', 'success')
    except:
        flash('خطأ', 'error')
    return redirect(url_for('main.dashboard'))
