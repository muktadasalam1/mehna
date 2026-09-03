# Admin Account Page — Security Card + Activity Log

**Status:** Planned
**Area:** `admin/account`
**Depends on:** existing sidebar dashboard redesign (dark theme, orange accents, RTL)

## 1. Goal

Extend the current `admin/account` page (profile card only) with two new sections that match the existing card design:

1. **Security card** — placed beside the existing profile card, same height.
2. **Activity Log card** — full-width, placed below both cards.

This turns the account page from "who you are" into "who you are + how secure your account is + what you've done," using data the system should already be capturing (or will start capturing) rather than static filler.

## 2. UX / Layout

- Grid: existing profile card keeps its current width; add a second card of matching height to its side (stack vertically on narrow/mobile).
- Below both: one full-width card.
- Reuse existing card component styling: dark surface, orange accent (`#f5851f`-ish per current palette), rounded corners, RTL text alignment, same spacing/typography as the profile card.
- Icons: reuse the existing icon set style (outline icons in orange circular badges, as seen on the profile card fields).

### 2.1 Security Card (side)

Fields:
- آخر تسجيل دخول (last login) — timestamp + approximate location/IP
- الجلسات النشطة (active sessions) — count, with a link/button to "عرض الجلسات" (view sessions)
- تفعيل التحقق بخطوتين (2FA) — status badge (مفعّل / غير مفعّل) + toggle/link
- تغيير كلمة المرور — button linking to change-password flow

### 2.2 Activity Log Card (bottom, full width)

- Reverse-chronological list/table of the admin's own actions.
- Each row: action icon, short description (e.g. "تمت الموافقة على شركة X"), actor is implicit (the logged-in admin), relative timestamp (e.g. "منذ ٣ ساعات"), and a link to the affected entity when applicable (user/company/job).
- Paginate or "load more" after ~10 rows.
- Empty state: friendly message if no activity yet.

## 3. Data Model (Backend)

### 3.1 New table: `admin_activity_log`

| column | type | notes |
|---|---|---|
| id | UUID/int PK | |
| admin_id | FK -> users/admins | who performed the action |
| action_type | enum/string | e.g. `user_created`, `company_approved`, `job_edited`, `job_deleted`, `login` |
| target_type | string, nullable | e.g. `user`, `company`, `job` |
| target_id | int/UUID, nullable | FK-ish reference to affected entity |
| description | string | human-readable, pre-rendered or built from action_type + target at read time |
| ip_address | string, nullable | |
| created_at | datetime | indexed, used for ordering |

### 3.2 New table (or reuse if it exists): `admin_sessions`

| column | type | notes |
|---|---|---|
| id | UUID PK | |
| admin_id | FK | |
| ip_address | string | |
| user_agent | string | |
| created_at | datetime | session start |
| last_active_at | datetime | |
| is_current | derived, not stored | compare to current request's session token |

### 3.3 `users`/`admins` table additions (if not present)

- `two_factor_enabled` (bool, default false)
- `last_login_at` (datetime, nullable)
- `last_login_ip` (string, nullable)

## 4. Backend Work (Flask)

1. **Migration**: add `admin_activity_log` table, `admin_sessions` table (if not existing), and the two new columns on the admin/user table.
2. **Activity logging hook**: a small helper (e.g. `log_admin_activity(admin_id, action_type, target_type=None, target_id=None, description=None)`) called from existing admin actions (user create/edit/delete, company approve/reject, job edit/delete, etc). Wire it into the existing admin routes that already perform these actions — do not duplicate business logic, just add a call at the point of success.
3. **Login hook**: update the admin login route to set `last_login_at`, `last_login_ip`, and create/update an `admin_sessions` row.
4. **New API endpoints** (JSON, consumed by the account page JS):
   - `GET /admin/api/account/security` → last login, active session count, 2FA status
   - `GET /admin/api/account/sessions` → list of active sessions (for the "view sessions" link/modal)
   - `POST /admin/api/account/sessions/<id>/revoke` → revoke a session
   - `GET /admin/api/account/activity?page=1&per_page=10` → paginated activity log for the current admin
5. **2FA toggle endpoint** (if 2FA isn't implemented yet, stub the field as "Coming soon" in phase 1 and skip building the actual 2FA flow — flag this explicitly as out of scope for this phase unless you want it included).
6. **Auth/permissions**: all new endpoints scoped to the currently authenticated admin only (no cross-admin data leakage) — apply the same `@login_required`/admin-check decorators used elsewhere in `admin/*` routes.

## 5. Frontend Work (HTML/CSS/JS, admin/account page)

1. Add the two new card containers to the `admin/account` template, matching the existing card markup/classes.
2. On page load, fetch `/admin/api/account/security` and `/admin/api/account/activity` (first page) via `fetch()`, populate the cards, show loading skeletons while waiting (reuse any existing loading-state pattern from the dashboard, or add a simple pulse skeleton if none exists).
3. "View sessions" opens a modal (or expands inline) listing sessions from `/admin/api/account/sessions`, with a "revoke" button per session (disabled for the current session).
4. Activity log: render rows from the API; "Load more" button calls the next page and appends.
5. RTL: ensure new cards use the same `dir="rtl"` context and orange badge/icon pattern as the existing profile card fields (تاريخ الانضمام، البريد الإلكتروني، إلخ).
6. Empty/error states for both new cards (e.g. API failure → "تعذر تحميل البيانات" with a retry button).

## 6. Phasing

- **Phase 1 (this doc's core scope):** DB migration, activity logging hook wired into existing actions, security card (last login + session count, 2FA shown as static/placeholder if not built), activity log card with pagination.
- **Phase 2 (optional follow-up, not required for this doc):** full 2FA implementation, session revoke UI polish, filtering activity log by action type.

## 7. Acceptance Criteria

- [ ] Visiting `admin/account` shows three cards: profile (existing, unchanged), security (new), activity log (new, full width).
- [ ] Security card shows real last-login time and an accurate active-session count.
- [ ] Performing any logged admin action (user/company/job create/edit/delete/approve) creates a row in `admin_activity_log` and appears in the activity feed on next load.
- [ ] Activity log paginates without page reload.
- [ ] All new endpoints reject requests from admins trying to view another admin's data.
- [ ] New cards visually match the existing card design (dark theme, orange accents, spacing, RTL).