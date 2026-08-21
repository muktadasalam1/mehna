# app.py - تطبيق مهنة مع جميع التحسينات الأمنية + نظام استعادة كلمة المرور + Cloudflare Tunnel + نظام الاشتراكات + توثيق الشركات + أدمن
import os
import secrets
import re
import logging
import subprocess
import threading
import time
from datetime import datetime, timedelta
from contextlib import contextmanager
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, jsonify)
from flask_socketio import SocketIO, join_room
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# ==================== تحسين إعدادات Socket.IO ====================
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=100000,
    async_mode='threading',
    logger=False,
    engineio_logger=False
)

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT', secrets.token_hex(16))
app.config['RESET_TOKEN_EXPIRY'] = 3600
logging.basicConfig(level=logging.ERROR)

MAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com', 'smtp_port': 587,
    'username': os.environ.get('MAIL_USERNAME', 'muktadasalam1111@gmail.com'),
    'password': os.environ.get('MAIL_PASSWORD', 'ingixipzmttzlfju'),
    'sender': os.environ.get('MAIL_USERNAME', 'muktadasalam1111@gmail.com')
}
DB_CONFIG = {'host': 'localhost', 'port': 5432, 'database': 'mehna_db', 'user': 'postgres', 'password': '123'}
login_attempts, apply_attempts = {}, {}

def get_user_plan(user_id):
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT plan, jobs_posted_this_month, plan_month_start, payment_status FROM users WHERE id = %s", [user_id])
        user = cur.fetchone()
        if user:
            if user['plan_month_start'] and user['plan_month_start'].month != datetime.now().month:
                cur.execute("UPDATE users SET jobs_posted_this_month = 0, plan_month_start = CURRENT_DATE WHERE id = %s", [user_id])
                return {'plan': user['plan'], 'jobs_posted': 0, 'payment_status': user['payment_status']}
            return {'plan': user['plan'], 'jobs_posted': user['jobs_posted_this_month'] or 0, 'payment_status': user['payment_status']}
        return {'plan': 'free', 'jobs_posted': 0, 'payment_status': 'none'}

def get_plan_limits(plan):
    return {
        'free': {'max_jobs': 1, 'max_applications': 10, 'name': 'مجانية', 'price': 0},
        'pro': {'max_jobs': 10, 'max_applications': 100, 'name': 'برو', 'price': 25000},
    }.get(plan, {'max_jobs': 1, 'max_applications': 10, 'name': 'مجانية', 'price': 0})

def check_job_limit(user_id):
    plan_info = get_user_plan(user_id)
    limits = get_plan_limits(plan_info['plan'])
    if plan_info['jobs_posted'] >= limits['max_jobs']: return False, limits, plan_info
    return True, limits, plan_info

@app.after_request
def add_security_headers(response):
    response.headers.update({
        'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'DENY', 'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.socket.io https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com https://cdnjs.cloudflare.com; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; img-src 'self' data: https:; connect-src 'self' ws: wss:;",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    })
    return response

def sanitize(value, max_length=255, allow_html=False):
    if not value: return ''
    value = str(value).strip()
    value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    if not allow_html: value = re.sub(r'<[^>]*>', '', value)
    return value[:max_length]

def validate_email(email): return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

def escape_html(text):
    if not text: return ''
    return str(text).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;').replace("'",'&#x27;')

def generate_csrf_token():
    if 'csrf_token' not in session: session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']
app.jinja_env.globals['csrf_token'] = generate_csrf_token

def csrf_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method in ['POST','PUT','DELETE']:
            token = request.form.get('csrf_token') or request.headers.get('X-CSRF-TOKEN')
            if not token or not secrets.compare_digest(token, session.get('csrf_token','')):
                flash('طلب غير صالح', 'error'); return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

def check_rate_limit(d, key, max=5, w=300):
    now = datetime.now()
    if key in d:
        attempts = [t for t in d[key] if (now-t).seconds < w]
        d[key] = attempts
        if len(attempts) >= max: return False
    else: d[key] = []
    d[key].append(now); return True

def is_valid_password(pw):
    if len(pw) < 6: return False, "كلمة المرور قصيرة"
    return True, ""

@contextmanager
def get_db():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    try:
        yield conn; conn.commit()
    except Exception as e:
        conn.rollback(); logging.error(f"DB error: {e}"); raise
    finally: conn.close()

def generate_reset_token(email): return URLSafeTimedSerializer(app.secret_key).dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])
def verify_reset_token(token):
    try: return URLSafeTimedSerializer(app.secret_key).loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=app.config['RESET_TOKEN_EXPIRY'])
    except: return None

def send_reset_email(to_email, reset_url):
    subject = "مهنة - استعادة كلمة المرور"
    body = f"""<div dir="rtl"><h2>استعادة كلمة المرور</h2><a href="{reset_url}">إعادة تعيين</a></div>"""
    if not MAIL_CONFIG['username']: print(f"\n{reset_url}\n"); return True
    try:
        msg = MIMEMultipart('alternative'); msg['Subject']=subject; msg['From']=MAIL_CONFIG['sender']; msg['To']=to_email
        msg.attach(MIMEText(body,'html','utf-8'))
        with smtplib.SMTP(MAIL_CONFIG['smtp_server'], MAIL_CONFIG['smtp_port']) as s:
            s.starttls(); s.login(MAIL_CONFIG['username'], MAIL_CONFIG['password']); s.send_message(msg)
        return True
    except Exception as e: print(f"خطأ: {e}"); return False

def login_required(f):
    @wraps(f)
    def decorated(*a, **k):
        if 'user_id' not in session: flash('سجل دخول اولا', 'error'); return redirect(url_for('login'))
        return f(*a, **k)
    return decorated

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated(*a, **k):
            if 'user_id' not in session: return redirect(url_for('login'))
            if session.get('user_role') != role: flash('غير مصرح', 'error'); return redirect(url_for('dashboard'))
            return f(*a, **k)
        return decorated
    return decorator

def admin_required(f):
    @wraps(f)
    def decorated(*a, **k):
        if 'user_id' not in session:
            flash('سجل دخول اولا', 'error')
            return redirect(url_for('login'))
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT is_admin FROM users WHERE id=%s", [session['user_id']])
            ad = cur.fetchone()
        if not ad or not ad[0]:
            flash('للأدمن فقط', 'error')
            return redirect(url_for('dashboard'))
        return f(*a, **k)
    return decorated

def is_job_owner(uid, jid):
    with get_db() as conn:
        c = conn.cursor(); c.execute("SELECT 1 FROM jobs WHERE id=%s AND employer_id=%s",[jid,uid])
        return c.fetchone() is not None

def is_app_owner(uid, aid):
    with get_db() as conn:
        c = conn.cursor(); c.execute("SELECT 1 FROM applications a JOIN jobs j ON a.job_id=j.id WHERE a.id=%s AND j.employer_id=%s",[aid,uid])
        return c.fetchone() is not None

def seed_data():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE user_type='employer'")
        if c.fetchone()[0] > 0: return
        c.execute("INSERT INTO users (email,password_hash,full_name,user_type,is_admin) VALUES (%s,%s,%s,%s,TRUE) RETURNING id",['employer@mehna.com',generate_password_hash('123456'),'أحمد محمد','employer'])
        eid = c.fetchone()[0]
        c.execute("INSERT INTO companies (name,description,location,industry,size,is_verified,verification_status) VALUES (%s,%s,%s,%s,%s,TRUE,'verified') RETURNING id",['شركة التقنية','شركة تطوير','بغداد','تقنية','11-50'])
        cid = c.fetchone()[0]
        c.execute("INSERT INTO users (email,password_hash,full_name,user_type) VALUES (%s,%s,%s,%s) RETURNING id",['seeker@mehna.com',generate_password_hash('123456'),'علي حسين','job_seeker'])
        sid = c.fetchone()[0]
        c.execute("INSERT INTO profiles (user_id,phone,location,bio,skills) VALUES (%s,%s,%s,%s,%s)",[sid,'07701234567','بغداد','مطور',['Python','Flask']])
        for j in [[eid,cid,'مطور Full Stack','نبحث عن مطور','1500-2500','بغداد','full_time'],[eid,cid,'مصمم UI/UX','مطلوب مصمم','1200-1800','بغداد','full_time']]:
            c.execute("INSERT INTO jobs (employer_id,company_id,title,description,salary_range,location,job_type) VALUES (%s,%s,%s,%s,%s,%s,%s)",j)

# ==================== تحسين Socket.IO ====================
@socketio.on('connect')
def handle_connect():
    if 'user_id' in session:
        join_room(f"user_{session['user_id']}")

@socketio.on('disconnect')
def handle_disconnect():
    pass

# ==================== طلب توثيق الشركة ====================
@app.route('/request-verification')
@login_required
@role_required('employer')
def request_verification():
    """طلب توثيق الشركة"""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT c.id, c.verification_status, c.verification_documents
            FROM companies c
            JOIN jobs j ON j.company_id = c.id
            WHERE j.employer_id = %s
            LIMIT 1
        """, [session['user_id']])
        company = c.fetchone()
        
        if not company:
            flash('⚠️ يجب إنشاء شركة أولاً', 'error')
            return redirect(url_for('create_company'))
        
        if company[1] == 'verified':
            flash('✅ شركتك موثقة بالفعل!', 'success')
            return redirect(url_for('dashboard'))
        
        if company[1] == 'pending':
            flash('⏳ طلب التوثيق قيد المراجعة بالفعل', 'info')
            return redirect(url_for('dashboard'))
        
        c.execute("""
            UPDATE companies 
            SET verification_status = 'pending' 
            WHERE id = %s
        """, [company[0]])
        
        flash('✅ تم تقديم طلب التوثيق بنجاح! سيتم مراجعته من قبل الإدارة.', 'success')
        
    return redirect(url_for('dashboard'))

# ==================== API Routes ====================
@app.route('/api/notifications')
@login_required
def api_notifications():
    with get_db() as conn:
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c.execute("SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 30",[session['user_id']])
        ns = c.fetchall()
        for n in ns: n['message'] = escape_html(n['message'])
        return jsonify([dict(n) for n in ns])

@app.route('/api/notifications/count')
@login_required
def api_notifications_count():
    with get_db() as conn:
        c = conn.cursor(); c.execute("SELECT COUNT(*) FROM notifications WHERE user_id=%s AND is_read=FALSE",[session['user_id']])
        return jsonify({'count':c.fetchone()[0]})

@app.route('/api/notifications/read-all', methods=['POST'])
@login_required
@csrf_required
def api_read_all():
    with get_db() as conn:
        c = conn.cursor(); c.execute("UPDATE notifications SET is_read=TRUE WHERE user_id=%s",[session['user_id']])
    return jsonify({'ok':True})

@app.route('/api/applications/count')
@login_required
def api_applications_count():
    if session.get('user_role')!='employer': return jsonify({'count':0})
    with get_db() as conn:
        c = conn.cursor(); c.execute("SELECT COUNT(*) FROM applications a JOIN jobs j ON a.job_id=j.id WHERE j.employer_id=%s AND a.status='pending'",[session['user_id']])
        return jsonify({'count':c.fetchone()[0]})

# ==================== الصفحات الرئيسية ====================
@app.route('/')
def index():
    with get_db() as conn:
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c.execute("SELECT j.*, c.name as company_name FROM jobs j JOIN companies c ON j.company_id=c.id WHERE j.is_active=TRUE ORDER BY j.created_at DESC LIMIT 6")
        jobs = c.fetchall()
        c.execute("SELECT COUNT(*) FROM jobs WHERE is_active=TRUE"); jc=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM companies WHERE is_verified=TRUE"); cc=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users WHERE user_type='job_seeker'"); sc=c.fetchone()[0]
    return render_template('index.html', page='home', jobs=jobs, stats={'jc':jc,'cc':cc,'sc':sc})

@app.route('/register', methods=['GET','POST'])
def register():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        try:
            email = sanitize(request.form.get('email',''),100)
            pw = request.form.get('password','')
            fn = sanitize(request.form.get('fullname',''),100)
            role = 'job_seeker' if sanitize(request.form.get('role','seeker'),20)=='seeker' else 'employer'
            if not email or not validate_email(email): flash('بريد غير صالح','error'); return render_template('index.html',page='register')
            if len(pw)<6: flash('كلمة المرور قصيرة','error'); return render_template('index.html',page='register')
            if not fn: flash('الاسم مطلوب','error'); return render_template('index.html',page='register')
            with get_db() as conn:
                c = conn.cursor()
                c.execute("INSERT INTO users (email,password_hash,full_name,user_type) VALUES (%s,%s,%s,%s) RETURNING id",[email,generate_password_hash(pw),fn,role])
                if role=='job_seeker': c.execute("INSERT INTO profiles (user_id) VALUES (%s)",[c.fetchone()[0]])
            flash('تم الانشاء','success'); return redirect(url_for('login'))
        except psycopg2.IntegrityError: flash('البريد مسجل','error')
        except Exception as e: logging.error(f"Reg: {e}"); flash('خطأ','error')
    return render_template('index.html',page='register')

@app.route('/login', methods=['GET','POST'])
def login():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = sanitize(request.form.get('email',''),100)
        pw = request.form.get('password','')
        if not check_rate_limit(login_attempts,request.remote_addr): flash('محاولات كثيرة','error'); return render_template('index.html',page='login')
        if not email or not pw: flash('جميع الحقول مطلوبة','error'); return render_template('index.html',page='login')
        with get_db() as conn:
            c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            c.execute("SELECT * FROM users WHERE email=%s AND is_active=TRUE",[email]); user=c.fetchone()
        if user and check_password_hash(user['password_hash'],pw):
            session.permanent=True
            role = 'admin' if user['is_admin'] else user['user_type']
            for k,v in [('user_id',user['id']),('user_name',escape_html(user['full_name'])),('user_role', role),('user_email',user['email']),('user_created',str(user['created_at'])[:10] if user['created_at'] else '---')]: session[k]=v
            with get_db() as conn: conn.cursor().execute("UPDATE users SET last_login=CURRENT_TIMESTAMP WHERE id=%s",[user['id']])
            flash(f'مرحبا {escape_html(user["full_name"])}!','success'); return redirect(url_for('dashboard'))
        flash('بيانات خاطئة','error')
    return render_template('index.html',page='login')

@app.route('/logout')
def logout(): session.clear(); flash('تم الخروج','success'); return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET','POST'])
def forgot_password():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = sanitize(request.form.get('email',''),100)
        if not email or not validate_email(email): flash('بريد غير صحيح','error'); return render_template('index.html',page='forgot_password')
        if not check_rate_limit(login_attempts,f"reset_{request.remote_addr}",3,900): flash('طلبات كثيرة','error'); return render_template('index.html',page='forgot_password')
        with get_db() as conn:
            c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            c.execute("SELECT id,email,is_active FROM users WHERE email=%s",[email]); user=c.fetchone()
        if user and user['is_active']: send_reset_email(email,url_for('reset_password',token=generate_reset_token(email),_external=True))
        flash('اذا كان البريد مسجل ستتلقى رابط','success'); return redirect(url_for('login'))
    return render_template('index.html',page='forgot_password')

@app.route('/reset-password/<token>', methods=['GET','POST'])
def reset_password(token):
    if 'user_id' in session: return redirect(url_for('dashboard'))
    email = verify_reset_token(token)
    if not email: flash('رابط غير صالح','error'); return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        pw,cp = request.form.get('password',''), request.form.get('confirm_password','')
        if pw!=cp: flash('غير متطابق','error'); return render_template('index.html',page='reset_password',token=token)
        v,msg = is_valid_password(pw)
        if not v: flash(msg,'error'); return render_template('index.html',page='reset_password',token=token)
        with get_db() as conn: conn.cursor().execute("UPDATE users SET password_hash=%s WHERE email=%s AND is_active=TRUE",[generate_password_hash(pw),email])
        flash('تم التغيير','success'); return redirect(url_for('login'))
    return render_template('index.html',page='reset_password',token=token)

@app.route('/profile')
@login_required
def profile(): return render_template('index.html',page='profile')

@app.route('/update-profile', methods=['POST'])
@login_required
@csrf_required
def update_profile():
    try:
        with get_db() as conn:
            conn.cursor().execute("UPDATE profiles SET phone=%s,location=%s,bio=%s WHERE user_id=%s",[sanitize(request.form.get('phone',''),20),sanitize(request.form.get('city',''),100),sanitize(request.form.get('bio',''),500),session['user_id']])
        flash('تم التحديث','success')
    except: flash('خطأ','error')
    return redirect(url_for('dashboard'))

@app.route('/jobs')
def jobs():
    with get_db() as conn:
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c.execute("SELECT j.*,c.name as company_name FROM jobs j JOIN companies c ON j.company_id=c.id WHERE j.is_active=TRUE ORDER BY j.created_at DESC")
        jobs = c.fetchall()
    return render_template('index.html',page='jobs',jobs=jobs)

@app.route('/job/<job_id>')
def job_detail(job_id):
    with get_db() as conn:
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c.execute("UPDATE jobs SET views_count=views_count+1 WHERE id=%s",[job_id])
        c.execute("SELECT j.*,c.name as company_name FROM jobs j JOIN companies c ON j.company_id=c.id WHERE j.id=%s",[job_id])
        job=c.fetchone(); applied=False
        if 'user_id' in session:
            c.execute("SELECT 1 FROM applications WHERE job_id=%s AND job_seeker_id=%s",[job_id,session['user_id']])
            applied=c.fetchone() is not None
    if not job: flash('غير موجودة','error'); return redirect(url_for('jobs'))
    return render_template('index.html',page='job',job=job,applied=applied)

# ==================== نظام التوثيق ====================
def can_user_post_job(user_id):
    with get_db() as conn:
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c.execute("""
            SELECT c.*,
                   (SELECT COUNT(*) FROM jobs WHERE company_id = c.id) as jobs_count
            FROM companies c
            JOIN jobs j ON j.company_id = c.id
            WHERE j.employer_id = %s
            LIMIT 1
        """, [user_id])
        company = c.fetchone()

        if not company:
            return False, 'لا يوجد شركة مسجلة', None

        if company['verification_status'] == 'verified':
            plan_info = get_user_plan(user_id)
            limits = get_plan_limits(plan_info['plan'])
            if plan_info['jobs_posted'] >= limits['max_jobs']:
                return False, f'لقد وصلت للحد الأقصى ({limits["max_jobs"]} وظائف) في الباقة {limits["name"]}. قم بالترقية.', company
            return True, '', company

        if company['jobs_count'] >= 1:
            return False, '⚠️ شركتك غير موثقة. لا يمكنك نشر أكثر من وظيفة واحدة. قم بطلب التوثيق.', company

        return True, '', company

# ==================== دالة post_job ====================
@app.route('/post-job', methods=['POST'])
@login_required
@role_required('employer')
@csrf_required
def post_job():
    try:
        can_post, msg, company = can_user_post_job(session['user_id'])

        if not can_post:
            flash(msg, 'error')
            return redirect(url_for('pricing'))

        title = sanitize(request.form.get('title', ''), 100)
        description = sanitize(request.form.get('description', ''), 2000)

        if not title or not description:
            flash('جميع الحقول مطلوبة', 'error')
            return redirect(url_for('dashboard'))

        with get_db() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO jobs (employer_id, company_id, title, description, salary_range, location, job_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [
                session['user_id'],
                company['id'],
                title,
                description,
                sanitize(request.form.get('salary', ''), 50),
                sanitize(request.form.get('location', ''), 100),
                sanitize(request.form.get('job_type', ''), 30)
            ])
            c.execute("UPDATE users SET jobs_posted_this_month = jobs_posted_this_month + 1 WHERE id = %s", [session['user_id']])

        flash('✅ تم نشر الوظيفة بنجاح!', 'success')

    except Exception as e:
        logging.error(f"Post job error: {e}")
        flash('حدث خطأ أثناء نشر الوظيفة', 'error')

    return redirect(url_for('dashboard'))

@app.route('/job/<job_id>/<action>')
@login_required
def job_action(job_id, action):
    if action not in ('delete','open','close'): return redirect(url_for('dashboard'))
    if not is_job_owner(session['user_id'],job_id): flash('غير مصرح','error'); return redirect(url_for('dashboard'))
    with get_db() as conn:
        c = conn.cursor()
        if action=='delete': c.execute("DELETE FROM jobs WHERE id=%s",[job_id])
        elif action=='open': c.execute("UPDATE jobs SET is_active=TRUE WHERE id=%s",[job_id])
        else: c.execute("UPDATE jobs SET is_active=FALSE WHERE id=%s",[job_id])
    flash('تم','success'); return redirect(url_for('dashboard'))

@app.route('/apply/<job_id>', methods=['POST'])
@login_required
@role_required('job_seeker')
@csrf_required
def apply(job_id):
    if not check_rate_limit(apply_attempts,f"apply_{session['user_id']}",10,3600): flash('تجاوزت الحد','error'); return redirect(url_for('job_detail',job_id=job_id))
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM applications WHERE job_id=%s AND job_seeker_id=%s",[job_id,session['user_id']])
        if c.fetchone(): flash('قدمت مسبقا','error'); return redirect(url_for('job_detail',job_id=job_id))
        c.execute("INSERT INTO applications (job_id,job_seeker_id) VALUES (%s,%s)",[job_id,session['user_id']])
        c.execute("SELECT employer_id,title FROM jobs WHERE id=%s",[job_id]); j=c.fetchone()
        if j: socketio.emit('new_applicant',{'message':f'متقدم على "{escape_html(j[1])}"','job_id':str(job_id)},room=f"user_{j[0]}")
    flash('تم التقديم','success'); return redirect(url_for('dashboard'))

@app.route('/applicants/<job_id>')
@login_required
def applicants(job_id):
    if not is_job_owner(session['user_id'],job_id): flash('غير مصرح','error'); return redirect(url_for('dashboard'))
    with get_db() as conn:
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c.execute("SELECT a.*,u.full_name,u.email,p.skills,p.phone FROM applications a JOIN users u ON a.job_seeker_id=u.id LEFT JOIN profiles p ON u.id=p.user_id WHERE a.job_id=%s ORDER BY a.created_at DESC",[job_id])
        apps=c.fetchall(); c.execute("SELECT title FROM jobs WHERE id=%s",[job_id]); job=c.fetchone()
    return render_template('index.html',page='applicants',applicants=apps,job=job)

@app.route('/application/<app_id>/<action>', methods=['POST'])
@login_required
@csrf_required
def manage_app(app_id, action):
    if action not in ('accepted','rejected') or not is_app_owner(session['user_id'],app_id): flash('غير مصرح','error'); return redirect(url_for('dashboard'))
    with get_db() as conn:
        c = conn.cursor()
        c.execute("UPDATE applications SET status=%s,reviewed_by=%s,reviewed_at=CURRENT_TIMESTAMP WHERE id=%s",[action,session['user_id'],app_id])
        c.execute("SELECT a.job_seeker_id,j.title FROM applications a JOIN jobs j ON a.job_id=j.id WHERE a.id=%s",[app_id]); r=c.fetchone()
        if r:
            msg = f'تم قبولك في "{escape_html(r[1])}"' if action=='accepted' else f'تم رفضك في "{escape_html(r[1])}"'
            socketio.emit('notification',{'message':msg,'type':action},room=f"user_{r[0]}")
            c.execute("INSERT INTO notifications (user_id,message) VALUES (%s,%s)",[r[0],msg])
    flash('تم','success'); return redirect(url_for('dashboard'))

@app.route('/create-company', methods=['GET','POST'])
@login_required
@role_required('employer')
def create_company():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT COUNT(*) FROM companies c
            JOIN jobs j ON j.company_id = c.id
            WHERE j.employer_id = %s
        """, [session['user_id']])
        if c.fetchone()[0] > 0:
            flash('لديك شركة بالفعل!', 'error')
            return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            cn = sanitize(request.form.get('company_name',''),100)
            if not cn:
                flash('اسم الشركة مطلوب', 'error')
                return render_template('index.html', page='create_company')

            with get_db() as conn:
                c = conn.cursor()
                c.execute("SELECT id FROM companies WHERE name = %s", [cn])
                if c.fetchone():
                    flash('⚠️ اسم الشركة مستخدم مسبقاً، اختر اسماً آخر', 'error')
                    return render_template('index.html', page='create_company')

            docs = f"المالك: {sanitize(request.form.get('owner_name',''),100)}\nرقم الهوية: {sanitize(request.form.get('owner_id',''),50)}"
            with get_db() as conn:
                conn.cursor().execute("""
                    INSERT INTO companies (name, description, website, location, verification_status, verification_documents)
                    VALUES (%s, %s, %s, %s, 'pending', %s)
                """, [cn, sanitize(request.form.get('description',''),500),
                      sanitize(request.form.get('website',''),200),
                      sanitize(request.form.get('location',''),100), docs])
            flash('✅ تم تقديم الطلب بنجاح!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            logging.error(f"Create co: {e}")
            flash('حدث خطأ، حاول مرة أخرى', 'error')
    return render_template('index.html', page='create_company')

@app.route('/edit-company/<company_id>', methods=['GET','POST'])
@login_required
@role_required('employer')
def edit_company(company_id):
    with get_db() as conn:
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c.execute("SELECT co.* FROM companies co JOIN jobs j ON j.company_id=co.id WHERE co.id=%s AND j.employer_id=%s",[company_id,session['user_id']])
        co = c.fetchone()
    if not co: flash('غير مصرح','error'); return redirect(url_for('dashboard'))
    if request.method=='POST':
        with get_db() as conn:
            conn.cursor().execute("UPDATE companies SET name=%s,description=%s,website=%s,location=%s WHERE id=%s",[sanitize(request.form.get('company_name',''),100),sanitize(request.form.get('description',''),500),sanitize(request.form.get('website',''),200),sanitize(request.form.get('location',''),100),company_id])
        flash('تم التحديث','success'); return redirect(url_for('dashboard'))
    return render_template('index.html',page='edit_company',company=co)

@app.route('/delete-company/<company_id>')
@login_required
@role_required('employer')
def delete_company(company_id):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM jobs WHERE company_id=%s AND employer_id=%s",[company_id,session['user_id']])
        c.execute("DELETE FROM companies WHERE id=%s",[company_id])
    flash('تم الحذف','success'); return redirect(url_for('dashboard'))

# ==================== دالة dashboard المصححة ====================
@app.route('/dashboard')
@login_required
def dashboard():
    with get_db() as conn:
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if session.get('user_role') == 'admin':
            return redirect(url_for('admin_panel'))

        if session['user_role'] == 'job_seeker':
            c.execute("SELECT * FROM profiles WHERE user_id=%s", [session['user_id']])
            p = c.fetchone()
            c.execute("""
                SELECT a.*, j.title, co.name as company_name
                FROM applications a
                JOIN jobs j ON a.job_id = j.id
                JOIN companies co ON j.company_id = co.id
                WHERE a.job_seeker_id = %s
                ORDER BY a.created_at DESC
            """, [session['user_id']])
            return render_template('index.html', page='dashboard', profile=p, applications=c.fetchall())

        else:
            # جلب الشركات الخاصة بصاحب العمل
            c.execute("""
                SELECT c.*
                FROM companies c
                INNER JOIN jobs j ON j.company_id = c.id
                WHERE j.employer_id = %s
                GROUP BY c.id
            """, [session['user_id']])
            companies = c.fetchall()

            # جلب الشركة الوحيدة الخاصة به
            c.execute("""
                SELECT c.*
                FROM companies c
                INNER JOIN jobs j ON j.company_id = c.id
                WHERE j.employer_id = %s
                LIMIT 1
            """, [session['user_id']])
            my_company = c.fetchone()

            # التحقق من إمكانية طلب التوثيق
            can_request_verification = False
            verification_status = None
            if my_company:
                verification_status = my_company['verification_status']
                if verification_status in ['rejected', None]:
                    can_request_verification = True

            # جلب الوظائف الخاصة بشركاته
            jobs_list = []
            if companies:
                ids = [str(x['id']) for x in companies]
                if ids:
                    c.execute("""
                        SELECT j.*, c.name as company_name,
                        (SELECT COUNT(*) FROM applications a WHERE a.job_id = j.id) as applicant_count
                        FROM jobs j
                        JOIN companies c ON j.company_id = c.id
                        WHERE j.company_id::text = ANY(%s)
                        ORDER BY j.created_at DESC
                    """, [ids])
                    jobs_list = c.fetchall()

            return render_template('index.html', page='dashboard',
                                  companies=companies,
                                  jobs=jobs_list,
                                  my_company=my_company,
                                  can_request_verification=can_request_verification,
                                  verification_status=verification_status)

# ==================== ميزات الأدمن ====================

@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    with get_db() as conn:
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c.execute("SELECT * FROM companies WHERE verification_status='pending' ORDER BY created_at DESC")
        pending_companies = c.fetchall()
        c.execute("SELECT * FROM companies WHERE verification_status='verified' ORDER BY created_at DESC LIMIT 20")
        verified_companies = c.fetchall()
        c.execute("SELECT * FROM companies WHERE verification_status='rejected' ORDER BY created_at DESC LIMIT 10")
        rejected_companies = c.fetchall()
        c.execute("SELECT COUNT(*) FROM users"); total_users = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM jobs WHERE is_active=TRUE"); total_jobs = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM companies WHERE verification_status='pending'"); pending_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM companies"); total_companies = c.fetchone()[0]
    return render_template('index.html', page='admin',
                          pending_companies=pending_companies,
                          verified_companies=verified_companies,
                          rejected_companies=rejected_companies,
                          stats={
                              'users': total_users,
                              'jobs': total_jobs,
                              'pending': pending_count,
                              'companies': total_companies
                          })

@app.route('/admin/verify-company/<company_id>')
@login_required
@admin_required
def verify_company(company_id):
    with get_db() as conn:
        conn.cursor().execute("UPDATE companies SET verification_status='verified', verified_at=CURRENT_TIMESTAMP WHERE id=%s", [company_id])
    flash('✅ تم توثيق الشركة بنجاح!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/reject-company/<company_id>')
@login_required
@admin_required
def reject_company(company_id):
    with get_db() as conn:
        conn.cursor().execute("UPDATE companies SET verification_status='rejected' WHERE id=%s", [company_id])
    flash('❌ تم رفض توثيق الشركة.', 'error')
    return redirect(url_for('admin_panel'))

@app.route('/admin/companies')
@login_required
@admin_required
def admin_companies():
    with get_db() as conn:
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c.execute("""
            SELECT c.*, u.email as owner_email, u.full_name as owner_name,
            (SELECT COUNT(*) FROM jobs j WHERE j.company_id = c.id) as jobs_count
            FROM companies c
            LEFT JOIN jobs j ON j.company_id = c.id
            LEFT JOIN users u ON j.employer_id = u.id
            GROUP BY c.id, u.email, u.full_name
            ORDER BY c.created_at DESC
        """)
        companies = c.fetchall()
    return render_template('index.html', page='admin_companies', companies=companies)

@app.route('/admin/company/<company_id>/delete')
@login_required
@admin_required
def admin_delete_company(company_id):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM jobs WHERE company_id=%s", [company_id])
        c.execute("DELETE FROM companies WHERE id=%s", [company_id])
    flash('🗑️ تم حذف الشركة بنجاح', 'success')
    return redirect(url_for('admin_companies'))

@app.route('/admin/company/<company_id>/details')
@login_required
@admin_required
def admin_company_details(company_id):
    with get_db() as conn:
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c.execute("""
            SELECT c.*,
                   (SELECT COUNT(*) FROM jobs j WHERE j.company_id = c.id) as jobs_count,
                   (SELECT COUNT(*) FROM applications a
                    JOIN jobs j ON a.job_id = j.id
                    WHERE j.company_id = c.id) as applications_count
            FROM companies c
            WHERE c.id = %s
        """, [company_id])
        company = c.fetchone()

        if not company:
            flash('الشركة غير موجودة', 'error')
            return redirect(url_for('admin_companies'))

        c.execute("""
            SELECT j.*,
                   (SELECT COUNT(*) FROM applications a WHERE a.job_id = j.id) as applicants_count
            FROM jobs j
            WHERE j.company_id = %s
            ORDER BY j.created_at DESC
        """, [company_id])
        jobs = c.fetchall()

        c.execute("""
            SELECT DISTINCT u.id, u.email, u.full_name, u.user_type, u.is_admin, u.is_active, u.created_at
            FROM users u
            JOIN jobs j ON j.employer_id = u.id
            WHERE j.company_id = %s
            LIMIT 1
        """, [company_id])
        owner = c.fetchone()

    return render_template('index.html', page='admin_company_details',
                          company=company, jobs=jobs, owner=owner)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    with get_db() as conn:
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c.execute("""
            SELECT id, email, full_name, user_type, is_admin, is_active, created_at,
            (SELECT COUNT(*) FROM jobs WHERE employer_id = users.id) as jobs_count
            FROM users ORDER BY created_at DESC
        """)
        users = c.fetchall()
    return render_template('index.html', page='admin_users', users=users)

@app.route('/admin/user/<user_id>/details')
@login_required
@admin_required
def admin_user_details(user_id):
    with get_db() as conn:
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c.execute("""
            SELECT u.*,
                   (SELECT COUNT(*) FROM jobs j WHERE j.employer_id = u.id) as jobs_count,
                   (SELECT COUNT(*) FROM applications a WHERE a.job_seeker_id = u.id) as applications_count
            FROM users u
            WHERE u.id = %s
        """, [user_id])
        user = c.fetchone()

        if not user:
            flash('المستخدم غير موجود', 'error')
            return redirect(url_for('admin_users'))

        c.execute("SELECT * FROM profiles WHERE user_id = %s", [user_id])
        profile = c.fetchone()

        c.execute("""
            SELECT j.*, c.name as company_name,
                   (SELECT COUNT(*) FROM applications a WHERE a.job_id = j.id) as applicants_count
            FROM jobs j
            JOIN companies c ON j.company_id = c.id
            WHERE j.employer_id = %s
            ORDER BY j.created_at DESC
        """, [user_id])
        jobs = c.fetchall()

        c.execute("""
            SELECT a.*, j.title, c.name as company_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            JOIN companies c ON j.company_id = c.id
            WHERE a.job_seeker_id = %s
            ORDER BY a.created_at DESC
        """, [user_id])
        applications = c.fetchall()

    return render_template('index.html', page='admin_user_details',
                          user=user, profile=profile, jobs=jobs, applications=applications)

@app.route('/admin/user/<user_id>/toggle')
@login_required
@admin_required
def admin_toggle_user(user_id):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET is_active = NOT is_active WHERE id = %s", [user_id])
    flash('تم تحديث حالة المستخدم', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<user_id>/make-admin')
@login_required
@admin_required
def admin_make_admin(user_id):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET is_admin = TRUE WHERE id = %s", [user_id])
    flash('تم جعل المستخدم أدمن', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<user_id>/remove-admin')
@login_required
@admin_required
def admin_remove_admin(user_id):
    if str(user_id) == str(session['user_id']):
        flash('⚠️ لا يمكنك إزالة صلاحية الأدمن من حسابك الخاص!', 'error')
        return redirect(url_for('admin_users'))
    with get_db() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET is_admin = FALSE WHERE id = %s", [user_id])
    flash('تم إزالة صلاحية الأدمن', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/stats')
@login_required
@admin_required
def admin_stats():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users"); total_users = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users WHERE user_type='employer'"); total_employers = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users WHERE user_type='job_seeker'"); total_seekers = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM jobs"); total_jobs = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM jobs WHERE is_active=TRUE"); active_jobs = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM applications"); total_apps = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM companies"); total_companies = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM companies WHERE verification_status='pending'"); pending = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM companies WHERE verification_status='verified'"); verified = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM companies WHERE verification_status='rejected'"); rejected = c.fetchone()[0]
        c.execute("SELECT title, views_count FROM jobs ORDER BY views_count DESC LIMIT 5")
        top_jobs = c.fetchall()
    return render_template('index.html', page='admin_stats',
                          stats={
                              'total_users': total_users,
                              'total_employers': total_employers,
                              'total_seekers': total_seekers,
                              'total_jobs': total_jobs,
                              'active_jobs': active_jobs,
                              'total_apps': total_apps,
                              'total_companies': total_companies,
                              'pending': pending,
                              'verified': verified,
                              'rejected': rejected,
                              'top_jobs': top_jobs
                          })

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard_full():
    with get_db() as conn:
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        c.execute("SELECT COUNT(*) FROM users"); total_users = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users WHERE user_type='employer'"); total_employers = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users WHERE user_type='job_seeker'"); total_seekers = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users WHERE is_admin=TRUE"); total_admins = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users WHERE is_active=TRUE"); active_users = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM jobs"); total_jobs = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM jobs WHERE is_active=TRUE"); active_jobs = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM jobs WHERE is_active=FALSE"); closed_jobs = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM applications"); total_apps = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM applications WHERE status='pending'"); pending_apps = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM applications WHERE status='accepted'"); accepted_apps = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM applications WHERE status='rejected'"); rejected_apps = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM companies"); total_companies = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM companies WHERE verification_status='pending'"); pending_companies = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM companies WHERE verification_status='verified'"); verified_companies = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM companies WHERE verification_status='rejected'"); rejected_companies = c.fetchone()[0]

        c.execute("SELECT id, email, full_name, user_type, created_at FROM users ORDER BY created_at DESC LIMIT 5")
        recent_users = c.fetchall()

        c.execute("""
            SELECT j.title, c.name as company_name, j.created_at, j.is_active
            FROM jobs j
            JOIN companies c ON j.company_id = c.id
            ORDER BY j.created_at DESC LIMIT 5
        """)
        recent_jobs = c.fetchall()

        c.execute("""
            SELECT c.name, COUNT(j.id) as jobs_count
            FROM companies c
            JOIN jobs j ON j.company_id = c.id
            GROUP BY c.id, c.name
            ORDER BY jobs_count DESC LIMIT 5
        """)
        top_companies = c.fetchall()

    return render_template('index.html', page='admin_dashboard_full',
                          stats={
                              'total_users': total_users,
                              'total_employers': total_employers,
                              'total_seekers': total_seekers,
                              'total_admins': total_admins,
                              'active_users': active_users,
                              'total_jobs': total_jobs,
                              'active_jobs': active_jobs,
                              'closed_jobs': closed_jobs,
                              'total_apps': total_apps,
                              'pending_apps': pending_apps,
                              'accepted_apps': accepted_apps,
                              'rejected_apps': rejected_apps,
                              'total_companies': total_companies,
                              'pending_companies': pending_companies,
                              'verified_companies': verified_companies,
                              'rejected_companies': rejected_companies
                          },
                          recent_users=recent_users,
                          recent_jobs=recent_jobs,
                          top_companies=top_companies)

# ==================== نظام الترقية ====================
@app.route('/upgrade-plan/<plan>')
@login_required
@role_required('employer')
def upgrade_plan(plan):
    if plan not in ['pro']:
        flash('باقة غير صالحة', 'error')
        return redirect(url_for('pricing'))

    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT c.id FROM companies c
                JOIN jobs j ON j.company_id = c.id
                WHERE j.employer_id = %s
                LIMIT 1
            """, [session['user_id']])
            company = c.fetchone()

            if not company:
                flash('⚠️ يجب إنشاء شركة أولاً قبل الترقية', 'error')
                return redirect(url_for('create_company'))

            c.execute("""
                UPDATE users
                SET plan = %s,
                    plan_month_start = CURRENT_DATE,
                    payment_status = 'active'
                WHERE id = %s
            """, [plan, session['user_id']])

            c.execute("""
                UPDATE companies
                SET verification_status = 'verified',
                    verified_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, [company[0]])

            flash('✅ تم الترقية وتوثيق الشركة بنجاح!', 'success')

    except Exception as e:
        logging.error(f"Upgrade error: {e}")
        flash('حدث خطأ أثناء الترقية', 'error')

    return redirect(url_for('dashboard'))

@app.route('/confirm-payment/<plan>')
@login_required
@role_required('employer')
def confirm_payment(plan):
    flash('🚧 نظام الدفع قيد التطوير. سيتم إطلاقه قريباً.', 'error')
    return redirect(url_for('pricing'))

@app.route('/pricing')
def pricing():
    plan_info = {}
    if 'user_id' in session:
        plan_info = get_user_plan(session['user_id'])
    return render_template('index.html', page='pricing', plan_info=plan_info)

@app.route('/about')
def about(): return render_template('index.html',page='about')

def start_cloudflare_tunnel():
    time.sleep(2)
    for n in ['cloudflared.exe','cloudflared-windows-amd64.exe']:
        if os.path.exists(n): te=n; break
    else: print("[!] cloudflared not found"); return
    try:
        p=subprocess.Popen([te,'tunnel','--url','http://localhost:5000','--no-autoupdate'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        for l in p.stdout:
            if 'trycloudflare.com' in l and 'https://' in l:
                m=re.search(r'https://[a-z0-9\-]+\.trycloudflare\.com',l)
                if m: print("\n"+f"PUBLIC URL: {m.group(0)}"+"\n"); break
    except Exception as e: print(f"[!] {e}")

if __name__=='__main__':
    seed_data()
    threading.Thread(target=start_cloudflare_tunnel,daemon=True).start()
    print("Server: http://127.0.0.1:5000\n")
    socketio.run(app, debug=False, allow_unsafe_werkzeug=True)