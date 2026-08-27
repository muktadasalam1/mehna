# مهنة - Mehna

**منصة التوظيف العراقية** | Iraqi Job Platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-green?logo=flask)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?logo=postgresql)](https://www.postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](#license)

<div dir="rtl">

## نظرة عامة

**مهنة** هي منصة توظيف عراقية تربط أصحاب العمل بالباحثين عن عمل. توفر المنصة نظاماً كاملاً لإدارة الوظائف والتقديمات مع لوحة تحكم إدارية ونظام توثيق شركات.

</div>

---

## المميزات / Features

### للباحثين عن عمل (Job Seekers)
- إنشاء حساب مجاني وসম্পূর্ণ الملف الشخصي
- تصفح الوظائف المتاحة مع فلترة حسب الموقع والراتب
- التقديم على الوظائف بضغطة زر
- تتبع حالة التقديمات (مقبول / مرفوض / قيد المراجعة)
- استلام إشعارات فورية عند تحديث حالة التقديم

### لأصحاب العمل (Employers)
- إنشاء حساب شركة
- طلب توثيق الشركة من الإدارة
- نشر الوظائف وإدارتها
- استقبال ومراجعة طلبات التوظيف
- قبول أو رفض المتقدمين
- إشعارات فورية عند تقديم متقدم جديد
- إدارة باقة الاشتراك

### للإدارة (Admin)
- لوحة تحكم شاملة بإحصائيات المنصة
- مراجعة طلبات توثيق الشركات (قبول / رفض)
- إدارة المستخدمين (تفعيل / تعطيل / جعل أدمن)
- عرض تفاصيل الشركات والوظائف
- إحصائيات متقدمة

### مميزات تقنية
- إشعارات فورية عبر WebSocket (Socket.IO)
- نظام CSRF protection كامل
- Rate limiting على تسجيل الدخول والتقديمات
- أمان متعدد الطبقات (Security Headers, XSS Protection)
- تصميم متجاوب (Responsive) يدعم الجوال
- واجهة عربية (RTL) بالكامل
- دعم Cloudflare Tunnel للنشر العام

---

## المتطلبات / Prerequisites

- Python 3.8 أو أعلى
- PostgreSQL 14 أو أعلى
- pip (مدير الحزم)

---

## التثبيت والتشغيل / Installation & Setup

### 1. استنساخ المستودع

```bash
git clone https://github.com/yourusername/mehna.git
cd mehna
```

### 2. إعداد قاعدة البيانات

```bash
# إنشاء قاعدة البيانات
psql -U postgres -c "CREATE DATABASE mehna_db;"
```

### 3. تثبيت المكتبات

```bash
pip install flask flask-socketio psycopg2-binary werkzeug itsdangerous
```

أو باستخدام ملف المتطلبات:

```bash
pip install -r requirements.txt
```

### 4. تشغيل التطبيق

```bash
python app.py
```

سيتم تشغيل التطبيق على:
```
http://127.0.0.1:5000
```

### 5. بيانات الدخول التجريبية

| الدور | البريد الإلكتروني | كلمة المرور |
|-------|-------------------|-------------|
| صاحب عمل (Admin) | employer@mehna.com | 123456 |
| باحث عن عمل | seeker@mehna.com | 123456 |

---

## هيكل المشروع / Project Structure

```
mehna/
├── app.py                      # نقطة الدخول الرئيسية (App Factory)
├── config.py                   # إعدادات التطبيق
├── extensions.py               # مثيلات مشتركة (db, socketio, csrf)
├── requirements.txt            # المتطلبات
│
├── models/                     # نماذج SQLAlchemy
│   ├── __init__.py
│   ├── user.py                 # نموذج المستخدم
│   ├── profile.py              # نموذج البروفايل
│   ├── company.py              # نموذج الشركة
│   ├── job.py                  # نموذج الوظيفة
│   ├── application.py          # نموذج التقديم
│   └── notification.py         # نموذج الإشعار
│
├── routes/                     # مخططات Flask (Blueprints)
│   ├── __init__.py
│   ├── auth.py                 # مسارات المصادقة
│   ├── jobs.py                 # مسارات الوظائف
│   ├── companies.py            # مسارات الشركات
│   ├── admin.py                # مسارات الإدارة
│   ├── notifications.py        # مسارات API الإشعارات
│   └── main.py                 # المسارات الرئيسية (الصفحة الرئيسية، لوحة التحكم)
│
├── services/                   # منطق الأعمال
│   ├── __init__.py
│   ├── auth_service.py         # خدمات المصادقة
│   ├── job_service.py          # خدمات الوظائف
│   ├── application_service.py  # خدمات التقديمات
│   ├── company_service.py      # خدمات الشركات
│   └── notification_service.py # خدمات الإشعارات
│
├── utils/                      # أدوات مساعدة
│   ├── __init__.py
│   ├── decorators.py           # декораторات (@login_required, @admin_required)
│   ├── validators.py           # التحقق من المدخلات
│   └── security.py             # الأمان (CSRF, Rate Limiting, Headers)
│
├── templates/                  # قوالب Jinja2
│   ├── base.html               # القالب الأساسي
│   ├── index_home.html         # الصفحة الرئيسية
│   ├── index_jobs.html         # تصفح الوظائف
│   ├── index_job.html          # تفاصيل الوظيفة
│   ├── index_login.html        # تسجيل الدخول
│   ├── index_register.html     # إنشاء حساب
│   ├── index_forgot_password.html  # نسيت كلمة المرور
│   ├── index_reset_password.html   # إعادة تعيين كلمة المرور
│   ├── index_profile.html      # الملف الشخصي
│   ├── index_dashboard.html    # لوحة التحكم
│   ├── index_applicants.html   # المتقدمين
│   ├── index_create_company.html   # إنشاء شركة
│   ├── index_edit_company.html     # تعديل الشركة
│   ├── index_pricing.html      # الباقات
│   ├── index_about.html        # عن المنصة
│   ├── index_admin.html        # لوحة تحكم الأدمن
│   ├── index_admin_companies.html  # إدارة الشركات
│   ├── index_admin_users.html      # إدارة المستخدمين
│   ├── index_admin_stats.html      # الإحصائيات
│   ├── index_admin_company_details.html  # تفاصيل الشركة
│   ├── index_admin_dashboard_full.html   # لوحة التحكم الكاملة
│   └── components/             # مكونات مشتركة
│       ├── navbar.html         # شريط التنقل
│       ├── footer.html         # التذييل
│       └── job_card.html       # بطاقة الوظيفة
│
├── static/                     # ملفات ثابتة
│   ├── css/
│   │   └── base.css            # الأنماط الأساسية
│   ├── js/
│   │   ├── socket-client.js    # إعداد WebSocket
│   │   └── notifications.js    # إشعارات
│   └── logo.png                # شعار التطبيق
│
├── SKILLS/                     # وثائق المسح
├── docs/                       # التوثيق
├── run time/                   # ملفات التشغيل
├── tests/                      # الاختبارات
├── .gitignore
└── .gitattributes
```

---

## هيكل قاعدة البيانات / Database Schema

### جدول المستخدمين (users)
| العمود | النوع | الوصف |
|--------|-------|-------|
| id | SERIAL PK | المعرف الفريد |
| email | VARCHAR UNIQUE | البريد الإلكتروني |
| password_hash | VARCHAR | كلمة المرور المشفرة |
| full_name | VARCHAR | الاسم الكامل |
| user_type | VARCHAR | نوع المستخدم (employer/job_seeker) |
| is_admin | BOOLEAN | هل هو مدير |
| is_active | BOOLEAN | هل الحساب مفعل |
| plan | VARCHAR | الباقة الحالية (free/pro) |
| jobs_posted_this_month | INTEGER | عدد الوظائف المنشورة هذا الشهر |
| created_at | TIMESTAMP | تاريخ الإنشاء |

### جدول البروفايلات (profiles)
| العمود | النوع | الوصف |
|--------|-------|-------|
| user_id | INTEGER FK | معرف المستخدم |
| phone | VARCHAR | رقم الهاتف |
| location | VARCHAR | الموقع |
| bio | TEXT | نبذة شخصية |
| skills | TEXT[] | المهارات |

### جدول الشركات (companies)
| العمود | النوع | الوصف |
|--------|-------|-------|
| id | SERIAL PK | معرف الشركة |
| name | VARCHAR | اسم الشركة |
| description | VARCHAR | وصف الشركة |
| website | VARCHAR | الموقع الإلكتروني |
| location | VARCHAR | الموقع |
| verification_status | VARCHAR | حالة التوثيق (pending/verified/rejected) |
| verification_documents | TEXT | مستندات التوثيق |
| verified_at | TIMESTAMP | تاريخ التوثيق |

### جدول الوظائف (jobs)
| العمود | النوع | الوصف |
|--------|-------|-------|
| id | SERIAL PK | معرف الوظيفة |
| employer_id | INTEGER FK | معرف صاحب العمل |
| company_id | INTEGER FK | معرف الشركة |
| title | VARCHAR | عنوان الوظيفة |
| description | TEXT | وصف الوظيفة |
| salary_range | VARCHAR | نطاق الراتب |
| location | VARCHAR | الموقع |
| job_type | VARCHAR | نوع الوظيفة |
| is_active | BOOLEAN | هل الوظيفة نشطة |
| views_count | INTEGER | عدد المشاهدات |
| created_at | TIMESTAMP | تاريخ النشر |

### جدول التقديمات (applications)
| العمود | النوع | الوصف |
|--------|-------|-------|
| id | SERIAL PK | معرف التقديم |
| job_id | INTEGER FK | معرف الوظيفة |
| job_seeker_id | INTEGER FK | معرف الباحث |
| status | VARCHAR | الحالة (pending/accepted/rejected) |
| reviewed_by | INTEGER FK | تمت المراجعة بواسطة |
| reviewed_at | TIMESTAMP | تاريخ المراجعة |

### جدول الإشعارات (notifications)
| العمود | النوع | الوصف |
|--------|-------|-------|
| id | SERIAL PK | معرف الإشعار |
| user_id | INTEGER FK | معرف المستخدم |
| message | TEXT | رسالة الإشعار |
| is_read | BOOLEAN | هل تم قراءته |
| created_at | TIMESTAMP | تاريخ الإنشاء |

---

## API endpoints

### إشعارات
| Endpoint | Method | الوصف |
|----------|--------|-------|
| `/api/notifications` | GET | جلب الإشعارات |
| `/api/notifications/count` | GET | عدد الإشعارات غير المقروءة |
| `/api/notifications/read-all` | POST | تحديد الكل كمقروء |

### التقديمات
| Endpoint | Method | الوصف |
|----------|--------|-------|
| `/api/applications/count` | GET | عدد التقديمات المعلقة |

---

## الأمان / Security

- **CSRF Protection:** جميع الطلبات POST/PUT/DELETE تتطلب CSRF token
- **Rate Limiting:** حد أقصى 5 محاولات تسجيل دخول كل 5 دقائق
- **XSS Protection:** تنظيف جميع المدخلات وإضافة headers أمان
- **Session Security:** cookies آمنة مع SameSite=Lax
- **Password Hashing:** باستخدام Werkzeug (PBKDF2)
- **Security Headers:** HSTS, CSP, X-Frame-Options

---

## باقات الاشتراك / Subscription Plans

| الباقة | الحد الأقصى للوظائف | الحد الأقصى للتقديمات | السعر |
|--------|---------------------|----------------------|-------|
| المجانية (Free) | 1 وظيفة | 10 تقديمات | مجاني |
| البرو (Pro) | 10 وظائف | 100 تقديم | 25,000 د.ع |

---

## تقنيات الاستخدام / Built With

- **[Flask](https://flask.palletsprojects.com/)** - إطار عمل الويب
- **[Flask-SocketIO](https://flask-socketio.readthedocs.io/)** - إشعارات فورية
- **[PostgreSQL](https://www.postgresql.org/)** - قاعدة البيانات
- **[psycopg2](https://www.psycopg.org/)** - محرك PostgreSQL
- **[Werkzeug](https://werkzeug.palletsprojects.com/)** - أمان كلمات المرور
- **[itsdangerous](https://itsdangerous.palletsprojects.com/)** - توقيع التوكنات
- **[Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)** - النشر العام

---

## المساهمة / Contributing

1. forks المستودع
2. إنشاء فرع جديد (`git checkout -b feature/اسم-الميزة`)
3. عمل commit للتغييرات (`git commit -m 'إضافة ميزة جديدة'`)
4. رفع الفرع (`git push origin feature/اسم-الميزة`)
5. فتح Pull Request

---

## الترخيص / License

هذا المشروع مرخص بموجب MIT License - راجع ملف [LICENSE](LICENSE) للتفاصيل.

---

<div dir="rtl">

## ملاحظات تقنية مهمة

1. **لا يوجد ملف requirements.txt** - يجب إنشاؤه قبل النشر
2. **بيانات الدخول التجريبية** تُنشأ تلقائياً عند أول تشغيل
3. **Cloudflare Tunnel** يستخدم للنشر العام (يجب تثبيت cloudflared أولاً)
4. **قاعدة البيانات** يجب إنشاؤها يدوياً قبل التشغيل
5. **الملفات المخفية** مثل `.env` يجب عدم رفعها للمستودع

</div>
