# مهنة (Mehna) — Architecture & Migration Design Document

**Status:** Proposed
**Applies to:** Restructuring `app.py` (1081 lines) and `templates/index.html` (monolithic) into a modular Flask application
**Audience:** Human developers **and** AI coding agents implementing this migration

---

## 0. How to use this document

This file is the single source of truth for the target architecture. It is written so that:

- A **developer** can read it top to bottom and understand *why* the structure looks this way, not just *what* it looks like.
- An **agent** (e.g. Claude Code) can read it and mechanically execute the migration steps in section 6 without needing to ask clarifying questions — every decision (naming, imports, file boundaries) is specified explicitly.

**Rule for agents:** Do not invent structure not described here. If something in the current `app.py` doesn't map cleanly to a category below, stop and flag it rather than guessing — see section 8 (Open Questions / Escalation).

---

## 1. Current State (Before)

```
mehna/
├── app.py                 # Everything: config, db connection, all routes,
│                           # all business logic, socket.io handlers, CLI seed data
├── templates/
│   └── index.html          # Every page for every role (seeker/employer/admin)
├── static/
│   └── logo.png
├── SKILLS/
│   └── summary-skill.md
├── docs/
│   └── directory-layout/
└── run time/
```

### Problems this causes

| Problem | Concrete symptom |
|---|---|
| No separation of concerns | Route handlers contain SQL, validation, CSRF logic, and socket emits inline |
| Merge conflicts | Any two people touching different features (jobs vs. notifications) edit the same 1000+ line file |
| No reusable templates | Job seeker, employer, and admin views likely duplicate navbar/job-card markup inside one HTML file |
| Hard to test | Business logic is not importable/testable in isolation from Flask request context |
| Hard to onboard | A new contributor (or an agent) must read the entire file to understand any one feature |
| Circular import risk | A naive split of `app.py` will break because `db`/`socketio` are currently defined and used in the same file |

---

## 2. Target State (After)

```
mehna/
├── app.py                      # Entry point ONLY — creates and runs the app
├── config.py                   # Config classes (Development/Production/Testing)
├── extensions.py               # Shared instances: db, socketio, csrf, limiter
├── requirements.txt
│
├── models/
│   ├── __init__.py             # imports all models so `db.create_all()` sees them
│   ├── user.py
│   ├── profile.py
│   ├── company.py
│   ├── job.py
│   ├── application.py
│   └── notification.py
│
├── routes/                     # Blueprints — one per domain, thin controllers only
│   ├── __init__.py
│   ├── auth.py
│   ├── jobs.py
│   ├── applications.py
│   ├── companies.py
│   ├── admin.py
│   └── notifications.py
│
├── services/                   # Business logic — framework-agnostic where possible
│   ├── __init__.py
│   ├── auth_service.py
│   ├── job_service.py
│   ├── application_service.py
│   ├── company_service.py
│   └── notification_service.py # owns all socketio.emit(...) calls
│
├── utils/
│   ├── __init__.py
│   ├── decorators.py           # @login_required, @admin_required, @employer_required
│   ├── validators.py           # input validation/sanitization helpers
│   └── security.py             # CSRF setup, rate-limit config, security headers
│
├── static/
│   ├── css/
│   │   ├── base.css
│   │   ├── auth.css
│   │   ├── jobs.css
│   │   ├── dashboard.css
│   │   └── admin.css
│   ├── js/
│   │   ├── socket-client.js    # single Socket.IO connection setup, reused everywhere
│   │   ├── notifications.js
│   │   ├── jobs.js
│   │   └── applications.js
│   └── logo.png
│
├── templates/
│   ├── base.html                # shared <head>, RTL setup, nav, flash messages
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── jobs/
│   │   ├── browse.html
│   │   └── job_detail.html
│   ├── seeker/
│   │   ├── dashboard.html
│   │   └── my_applications.html
│   ├── employer/
│   │   ├── dashboard.html
│   │   ├── post_job.html
│   │   └── applicants.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── companies.html
│   │   └── users.html
│   └── components/              # Jinja {% include %} partials, reused across roles
│       ├── navbar.html
│       ├── job_card.html
│       ├── notification_bell.html
│       └── pagination.html
│
├── migrations/                  # Flask-Migrate / Alembic versioned schema changes
├── tests/
│   ├── test_auth.py
│   ├── test_jobs.py
│   └── ...
├── SKILLS/
├── docs/
└── run time/
```

---

## 3. Core Architectural Principles

1. **App Factory pattern.** `app.py` never defines routes or models directly. It only builds and configures the `Flask` app via a `create_app()` function. This is what makes testing (separate test config) and avoiding circular imports possible.

2. **Extensions live in one neutral file.** `db`, `socketio`, `csrf`, and any rate limiter are instantiated in `extensions.py` with no app attached (`db = SQLAlchemy()`), then bound to the app inside `create_app()` via `db.init_app(app)`. Models and blueprints import from `extensions.py`, never from `app.py`. This is the single most important rule for avoiding circular imports.

3. **One blueprint per domain, matching the feature list in the README.** Routes map to: `auth`, `jobs`, `applications`, `companies`, `admin`, `notifications`. A route file only contains: request parsing, calling a service function, and returning a response. No raw SQL or business rules inside route handlers.

4. **Services contain business logic, not Flask specifics.** A service function should be callable and testable without an active request context wherever feasible (e.g. `job_service.create_job(employer_id, data)` — not `job_service.create_job(request)`). Services are what enforce rules like "Free plan = 1 active job max" or "Pro plan = 10 active jobs max."

5. **Models are pure data layer.** SQLAlchemy models only — no business rules, no request handling. Relationships and constraints (foreign keys, uniqueness) live here.

6. **Templates use inheritance + partials, not copy-paste.** `base.html` defines the shell (RTL `<html dir="rtl">`, nav, flash messages, Socket.IO script include). Every page extends it. Repeated fragments (job card, notification bell) are `components/` partials included wherever needed — written once, used by seeker/employer/admin views alike.

7. **Notification/WebSocket logic is centralized.** All `socketio.emit(...)` calls live in `services/notification_service.py`. Route handlers and other services call `notification_service.notify_new_application(...)` etc. rather than importing `socketio` directly. This keeps the real-time logic auditable in one place.

8. **Security utilities are explicit, not scattered.** CSRF setup, rate-limiting decorators, and security headers (HSTS, CSP, X-Frame-Options mentioned in the README) live in `utils/security.py` and are applied in `create_app()` or via decorators in `utils/decorators.py` — not re-implemented per route.

---

## 4. Request Lifecycle (reference for both humans and agents)

To understand how a request should flow through the new structure, trace this example: **a job seeker applies to a job.**

```
Browser POST /jobs/42/apply
        │
        ▼
routes/applications.py  (blueprint route)
   - reads request.form
   - checks @login_required, @role_required('job_seeker')
   - calls application_service.submit_application(user_id, job_id, data)
        │
        ▼
services/application_service.py
   - validates job exists & is_active (via job_service or models/job.py)
   - checks plan limits / duplicate application rules
   - creates Application row (models/application.py)
   - calls notification_service.notify_employer_new_applicant(job.employer_id, application)
        │
        ▼
services/notification_service.py
   - creates Notification row
   - socketio.emit('new_notification', ..., room=f'user_{employer_id}')
        │
        ▼
routes/applications.py returns JSON/redirect to browser
```

Any new feature should be traceable through this same layering: **route → service → model**, with notifications always going through `notification_service`.

---

## 5. Naming & File-Placement Rules (for the agent to apply mechanically)

| If the code... | It belongs in... |
|---|---|
| Defines a `@app.route` or `@bp.route` | `routes/<domain>.py` |
| Runs a DB query, enforces a business rule, or computes something derived (e.g. plan limits, stats) | `services/<domain>_service.py` |
| Defines a SQLAlchemy model / table | `models/<entity>.py` |
| Is a decorator used across multiple route files (`login_required`, `admin_required`) | `utils/decorators.py` |
| Validates/sanitizes raw input | `utils/validators.py` |
| Configures CSRF, rate limits, or security headers | `utils/security.py` |
| Instantiates `db`, `socketio`, `csrf` | `extensions.py` (only) |
| Is environment/config values (DB URI, secret key, rate limit thresholds) | `config.py` |
| Calls `socketio.emit(...)` | `services/notification_service.py` only |
| Is shared HTML (nav, job card, notification bell) | `templates/components/*.html` |
| Is a full page for one role | `templates/<role>/<page>.html`, extending `base.html` |

**Blueprint naming convention:** `bp = Blueprint('jobs', __name__, url_prefix='/jobs')`, mirroring the file name.

**Service function naming convention:** verbs describing intent — `create_job`, `get_active_jobs_for_seeker`, `verify_company`, `submit_application` — not generic CRUD names like `insert()`.

---

## 6. Migration Plan (step-by-step, safe order)

This order is chosen so the app **stays runnable after every step** — do not reorder.

### Step 1 — Scaffolding
1. Create the folder structure from section 2 (empty `__init__.py` files where noted).
2. Create `extensions.py`:
   ```python
   from flask_sqlalchemy import SQLAlchemy
   from flask_socketio import SocketIO
   from flask_wtf import CSRFProtect

   db = SQLAlchemy()
   socketio = SocketIO()
   csrf = CSRFProtect()
   ```
3. Create `config.py` with a `Config` base class holding everything currently hardcoded in `app.py` (DB URI, `SECRET_KEY`, rate-limit numbers).

### Step 2 — Extract models
1. For each table in the README's schema section (`users`, `profiles`, `companies`, `jobs`, `applications`, `notifications`), find its model/class in `app.py` and move it verbatim into the matching `models/<entity>.py`, importing `db` from `extensions.py`.
2. In `models/__init__.py`, import every model so a single `from models import *` (used in `create_app`) registers them all with SQLAlchemy.
3. **Do not change column definitions during this step.** This step is a pure move, not a redesign.

### Step 3 — Extract services
1. For each route currently in `app.py`, identify the "business logic" portion (DB writes/reads, validation, plan-limit checks) as distinct from the "handle the HTTP request" portion.
2. Move the business logic into the matching `services/<domain>_service.py` function, named per section 5's convention.
3. Any `socketio.emit(...)` call found anywhere gets moved into `services/notification_service.py` as a named function (e.g. `notify_application_status_changed`).

### Step 4 — Extract routes into blueprints
1. For each route, create the corresponding thin handler in `routes/<domain>.py`: parse request → call service function → return response.
2. Apply `@login_required` / `@admin_required` from `utils/decorators.py` (extract these decorators from `app.py` if they exist inline; if login logic doesn't exist yet as decorators, write them here).
3. Register each blueprint at the bottom of its file's module scope; do not call `app.register_blueprint` here — that happens in `create_app()`.

### Step 5 — Rebuild `app.py` as an app factory
```python
from flask import Flask
from extensions import db, socketio, csrf
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    socketio.init_app(app)
    csrf.init_app(app)

    from routes.auth import bp as auth_bp
    from routes.jobs import bp as jobs_bp
    from routes.applications import bp as applications_bp
    from routes.companies import bp as companies_bp
    from routes.admin import bp as admin_bp
    from routes.notifications import bp as notifications_bp

    for bp in (auth_bp, jobs_bp, applications_bp, companies_bp, admin_bp, notifications_bp):
        app.register_blueprint(bp)

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True)
```

### Step 6 — Split `index.html`
1. Create `templates/base.html` containing: `<html dir="rtl">`, `<head>` (CSS links), navbar include, flash-message block, `{% block content %}{% endblock %}`, and the Socket.IO client script include at the bottom.
2. Identify each distinct "page" currently toggled/rendered inside `index.html` (login, register, job browse, job detail, seeker dashboard, employer dashboard, post job, applicants list, admin dashboard, company management, user management) and extract each into its own file under the matching `templates/<role>/` folder, with `{% extends "base.html" %}` and content in `{% block content %}`.
3. Extract repeated markup (navbar, job card, notification bell, pagination controls) into `templates/components/*.html` and replace duplicated blocks with `{% include %}`.
4. Update each route's `render_template(...)` call to point at the new path (e.g. `render_template('jobs/browse.html', ...)`).

### Step 7 — Split static assets
1. Break any inline `<script>`/`<style>` blocks out of `index.html` into the `static/js/` and `static/css/` files listed in section 2, grouped by the same domain boundaries as the templates.
2. `socket-client.js` should contain the single shared `io()` connection setup; other JS files should reuse it rather than each opening their own socket.

### Step 8 — Generate `requirements.txt`
The README notes this file is missing. Freeze current dependencies:
```
flask
flask-socketio
flask-sqlalchemy
psycopg2-binary
werkzeug
itsdangerous
flask-wtf
```
(Adjust to actual installed versions via `pip freeze` at execution time.)

### Step 9 — Smoke test
1. Run `python app.py` (or `flask run` if converted to use the CLI) and verify:
   - App boots with no import errors (this catches circular-import mistakes immediately).
   - Login, job browse, job posting, application submission, and a real-time notification all still work end-to-end.
2. Compare route-by-route against the "API endpoints" table in the README to confirm nothing was dropped.

### Step 10 — Cleanup
1. Delete the now-empty logic from the old `app.py`/`index.html` once everything is verified moved.
2. Update the README's "Project Structure" section to match section 2 of this document.

---

## 7. Conventions Checklist (apply to all new/moved code)

- [ ] No `socketio.emit` outside `services/notification_service.py`
- [ ] No raw SQL/ORM queries inside `routes/*.py`
- [ ] No `import app` anywhere (nothing should depend on the entry-point module)
- [ ] Every blueprint has a `url_prefix` matching its domain (`/jobs`, `/applications`, `/admin`, etc.)
- [ ] Every new template extends `base.html`
- [ ] Any markup appearing on 2+ pages is a `components/` partial, not copy-pasted
- [ ] Config values (rate limits, plan limits, secret key) come from `config.py`, never hardcoded in routes/services
- [ ] Arabic RTL layout (`dir="rtl"`) is set once in `base.html`, not per-page

---

## 8. Open Questions / Escalation

If, during migration, the agent or developer encounters any of the following, **stop and ask a human** rather than guessing:

- Logic in `app.py` that doesn't clearly belong to one of the six domains (auth/jobs/applications/companies/admin/notifications) — may indicate a missing seventh blueprint (e.g. `subscriptions` for plan/billing logic).
- Any place where the same DB write appears to happen from two different code paths (risk of losing a business rule during extraction).
- Session/auth mechanism details not visible in the README (how `is_admin`/`user_type` currently gates access) — must be preserved exactly, not redesigned, during this migration.
- Cloudflare Tunnel / deployment scripts referenced in `run time/` — out of scope for this migration unless explicitly requested.

This migration is a **restructuring, not a rewrite**: behavior, routes, and database schema should be unchanged at the end — only file organization changes.
