from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.validators import sanitize, validate_email, escape_html, is_valid_password
from utils.security import (
    generate_csrf_token, generate_reset_token, verify_reset_token,
    check_rate_limit, send_reset_email
)
from services import auth_service
from extensions import db

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        if not check_rate_limit(request.remote_addr, attempt_type='register'):
            flash('محاولات كثيرة، حاول لاحقاً', 'error')
            return render_template('index_register.html', page='register')

        try:
            email = sanitize(request.form.get('email', ''), 100)
            pw = request.form.get('password', '')
            fn = sanitize(request.form.get('full_name', ''), 100)
            ut = request.form.get('user_type', 'job_seeker')

            if not email or not validate_email(email):
                flash('بريد غير صالح', 'error')
                return render_template('index_register.html', page='register')
            valid, msg = is_valid_password(pw)
            if not valid:
                flash(msg, 'error')
                return render_template('index_register.html', page='register')
            if not fn:
                flash('الاسم مطلوب', 'error')
                return render_template('index_register.html', page='register')

            user = auth_service.register(email, pw, fn, ut)
            if not user:
                flash('البريد مسجل مسبقاً', 'error')
                return render_template('index_register.html', page='register')

            flash('تم التسجيل بنجاح، سجّل دخولك', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            flash('خطأ في التسجيل', 'error')

    return render_template('index_register.html', page='register')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        try:
            email = sanitize(request.form.get('email', ''), 100)
            pw = request.form.get('password', '')

            if not check_rate_limit(request.remote_addr, attempt_type='login'):
                flash('محاولات كثيرة، حاول لاحقاً', 'error')
                return render_template('index_login.html', page='login')

            user = auth_service.login(email, pw)
            if not user:
                flash('بيانات خاطئة', 'error')
                return render_template('index_login.html', page='login')

            session.permanent = True
            session['user_id'] = user.id
            session['user_role'] = user.user_type
            session['user_name'] = user.full_name
            session['user_email'] = user.email
            session['user_created'] = str(user.created_at)[:10] if user.created_at else '---'
            auth_service.update_last_login(user.id)

            # Record login IP for admin users
            if user.is_admin:
                from models.user import User
                from extensions import db as _db
                user.last_login_ip = request.remote_addr
                _db.session.commit()

                # Create admin session record
                from models.admin_security import AdminSession, log_admin_activity, ACTION_LOGIN
                admin_session = AdminSession(
                    admin_id=user.id,
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string[:500] if request.user_agent else None,
                    session_token=session.get('csrf_token'),
                )
                _db.session.add(admin_session)
                _db.session.commit()

                log_admin_activity(user.id, ACTION_LOGIN,
                                   ip_address=request.remote_addr,
                                   description='تسجيل دخول')

            flash(f'مرحبا {escape_html(user.full_name)}!', 'success')
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            flash('خطأ في تسجيل الدخول', 'error')

    return render_template('index_login.html', page='login')


@bp.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج', 'success')
    return redirect(url_for('main.index'))


@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = sanitize(request.form.get('email', ''), 100)
        if not email or not validate_email(email):
            flash('بريد غير صالح', 'error')
            return render_template('index_forgot_password.html', page='forgot_password')

        if not check_rate_limit(request.remote_addr, attempt_type='reset'):
            flash('محاولات كثيرة، حاول لاحقاً', 'error')
            return render_template('index_forgot_password.html', page='forgot_password')

        user = auth_service.get_user_by_email(email)
        if user:
            token = generate_reset_token(user.id)
            send_reset_email(email, token)
            flash('تم إرسال رابط إعادة التعيين', 'success')
        else:
            flash('البريد غير مسجل', 'error')

    return render_template('index_forgot_password.html', page='forgot_password')


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user_id = verify_reset_token(token)
    if not user_id:
        flash('رابط غير صالح أو منتهي', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        pw = request.form.get('password', '')
        valid, msg = is_valid_password(pw)
        if not valid:
            flash(msg, 'error')
            return render_template('index_reset_password.html', page='reset_password', token=token)

        auth_service.reset_password(user_id, pw)
        flash('تم تحديث كلمة المرور', 'success')
        return redirect(url_for('auth.login'))

    return render_template('index_reset_password.html', page='reset_password', token=token)


@bp.route('/profile/update', methods=['POST'])
def update_profile():
    try:
        from models.user import User
        user = User.query.get(session['user_id'])
        if user:
            user.full_name = sanitize(request.form.get('full_name', ''), 100)
            if user.profile:
                user.profile.phone = sanitize(request.form.get('phone', ''), 20)
                user.profile.location = sanitize(request.form.get('location', ''), 100)
                user.profile.bio = sanitize(request.form.get('bio', ''), 500)
            db.session.commit()
        flash('تم التحديث', 'success')
    except Exception:
        flash('خطأ', 'error')
    return redirect(url_for('main.dashboard'))
