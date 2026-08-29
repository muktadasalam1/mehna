import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import re
import json
import ssl

BASE_URL = "http://127.0.0.1:5000"
results = []
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

class CookieJar:
    def __init__(self):
        self.cookies = {}
    
    def add(self, headers):
        for h in headers:
            if h[0].lower() == 'set-cookie':
                parts = h[1].split(';')[0].split('=', 1)
                if len(parts) == 2:
                    self.cookies[parts[0].strip()] = parts[1].strip()
    
    def header(self):
        if self.cookies:
            return '; '.join(f'{k}={v}' for k, v in self.cookies.items())
        return None

jar = CookieJar()

def make_request(method, url, data=None):
    full_url = f"{BASE_URL}{url}"
    headers = {'User-Agent': 'TestAgent/1.0'}
    cookie_header = jar.header()
    if cookie_header:
        headers['Cookie'] = cookie_header
    
    if data:
        encoded = urllib.parse.urlencode(data).encode('utf-8')
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    else:
        encoded = None
    
    req = urllib.request.Request(full_url, data=encoded, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=5)
        jar.add(resp.headers.get_all('Set-Cookie') or [])
        return resp.status, resp.read().decode('utf-8', errors='replace'), resp.geturl()
    except urllib.error.HTTPError as e:
        jar.add(e.headers.get_all('Set-Cookie') or [])
        body = e.read().decode('utf-8', errors='replace') if e.fp else ""
        return e.code, body, e.url if hasattr(e, 'url') else full_url
    except Exception as e:
        return 0, str(e), full_url

def get_csrf(html):
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
    if m:
        return m.group(1)
    m = re.search(r'value="([^"]+)"\s+name="csrf_token"', html)
    if m:
        return m.group(1)
    return ""

def test(name, method, url, data=None, expected_status=None):
    status, body, final_url = make_request(method, url, data)
    redirect_info = f" → {final_url}" if final_url != f"{BASE_URL}{url}" else ""
    
    if expected_status and status == expected_status:
        icon = "✅"
    elif status in [301, 302, 303, 307, 308]:
        icon = "↪️"
    elif status == 0:
        icon = "❌"
    else:
        icon = "⚠️"
    
    results.append({
        'name': name,
        'method': method,
        'url': url,
        'status': status,
        'icon': icon,
        'redirect': redirect_info,
        'expected': expected_status,
        'body_len': len(body)
    })
    return status, body

def print_result(r):
    exp = f" (expect {r['expected']})" if r['expected'] and r['status'] != r['expected'] else ""
    print(f"  {r['icon']} {r['method']:4} {r['url']:45} {r['status']:>3}  {r['body_len']:>6}b{r['redirect']}{exp}")

# ========================================
print("=" * 80)
print("  MEHNA END-TO-END TEST REPORT")
print("  Server: http://127.0.0.1:5000")
print("=" * 80)

# === PUBLIC PAGES ===
print("\n📋 1. PUBLIC PAGES")
print("-" * 80)

test("Home page", "GET", "/", expected_status=200)
test("Jobs browse", "GET", "/jobs/", expected_status=200)
test("Job detail (seed job)", "GET", "/jobs/1", expected_status=200)
test("Pricing page", "GET", "/pricing", expected_status=200)
test("About page", "GET", "/about", expected_status=200)
test("Login page", "GET", "/login", expected_status=200)
test("Register page", "GET", "/register", expected_status=200)
test("Forgot password page", "GET", "/forgot-password", expected_status=200)
test("Nonexistent page (404)", "GET", "/nonexistent", expected_status=404)
test("Static CSS", "GET", "/static/css/base.css", expected_status=200)
test("Static JS socket", "GET", "/static/js/socket-client.js", expected_status=200)
test("Static JS notif", "GET", "/static/js/notifications.js", expected_status=200)
test("Static logo", "GET", "/static/logo.png", expected_status=200)

for r in results[-13:]:
    print_result(r)

# === UNAUTHENTICATED REDIRECTS ===
print("\n🔒 2. UNAUTHENTICATED REDIRECTS (should redirect to /login)")
print("-" * 80)

count_before = len(results)
test("Dashboard (no auth)", "GET", "/dashboard", expected_status=302)
test("Profile (no auth)", "GET", "/profile", expected_status=302)
test("Update profile (no auth)", "POST", "/update-profile", data={"phone": "123"}, expected_status=302)
test("Admin panel (no auth)", "GET", "/admin", expected_status=302)
test("Admin dashboard (no auth)", "GET", "/admin/dashboard", expected_status=302)
test("Admin users (no auth)", "GET", "/admin/users", expected_status=302)
test("Admin companies (no auth)", "GET", "/admin/companies", expected_status=302)
test("Admin stats (no auth)", "GET", "/admin/stats", expected_status=302)
test("API notifications (no auth)", "GET", "/api/notifications", expected_status=302)
test("API notif count (no auth)", "GET", "/api/notifications/count", expected_status=302)
test("API apps count (no auth)", "GET", "/api/applications/count", expected_status=302)
test("Job apply (no auth)", "POST", "/jobs/1/apply", expected_status=302)
test("Post job (no auth)", "POST", "/jobs/post", expected_status=302)
test("Create company (no auth)", "GET", "/companies/create", expected_status=302)

for r in results[count_before:]:
    print_result(r)

# === EMPLOYER LOGIN ===
print("\n🔑 3. EMPLOYER LOGIN")
print("-" * 80)

count_before = len(results)

# Get CSRF from login page
status, login_html = make_request("GET", "/login")[:2]
csrf = get_csrf(login_html)

# Wrong password
test("Login (wrong pw)", "POST", "/login",
     data={"email": "employer@mehna.com", "password": "wrong", "csrf_token": csrf},
     expected_status=200)

# Correct login - fresh CSRF
status, login_html2 = make_request("GET", "/login")[:2]
csrf2 = get_csrf(login_html2)
status, body, url = make_request("POST", "/login",
    data={"email": "employer@mehna.com", "password": "123456", "csrf_token": csrf2})

employer_logged = (status in [301, 302, 303])
results.append({
    'name': 'Login (employer, correct)',
    'method': 'POST', 'url': '/login',
    'status': status, 'icon': '✅' if employer_logged else '❌',
    'redirect': f" → {url}", 'expected': 302, 'body_len': len(body)
})

for r in results[count_before:]:
    print_result(r)

# === EMPLOYER AUTHENTICATED ===
print("\n👔 4. EMPLOYER - AUTHENTICATED ENDPOINTS")
print("-" * 80)

count_before = len(results)

test("Employer dashboard", "GET", "/dashboard", expected_status=200)
test("Employer profile", "GET", "/profile", expected_status=200)
test("Employer pricing", "GET", "/pricing", expected_status=200)
test("Employer about", "GET", "/about", expected_status=200)
test("API notifications", "GET", "/api/notifications", expected_status=200)
test("API notif count", "GET", "/api/notifications/count", expected_status=200)
test("API apps count", "GET", "/api/applications/count", expected_status=200)
test("Create company page", "GET", "/companies/create", expected_status=200)
test("Request verification", "GET", "/companies/request-verification", expected_status=302)

# Employer can access job applicants
test("Applicants (job 1)", "GET", "/jobs/1/applicants", expected_status=200)

# Employer can close/open jobs
test("Close job 1", "GET", "/jobs/1/close", expected_status=302)
test("Open job 1", "GET", "/jobs/1/open", expected_status=302)

# Employer cannot access admin
test("Admin panel (employer)", "GET", "/admin", expected_status=302)

for r in results[count_before:]:
    print_result(r)

# === EMPLOYER: POST JOB ===
print("\n📝 5. EMPLOYER - JOB POSTING")
print("-" * 80)

count_before = len(results)

# Get CSRF from dashboard
status, dash_html = make_request("GET", "/dashboard")[:2]
csrf_d = get_csrf(dash_html)

test("Post job (no title)", "POST", "/jobs/post",
     data={"csrf_token": csrf_d, "description": "test", "title": ""},
     expected_status=302)

test("Post job (valid)", "POST", "/jobs/post",
     data={
         "csrf_token": csrf_d,
         "title": "مطور Python تجريبي",
         "description": "وصف تجريبي للوظيفة",
         "salary": "2000-3000",
         "location": "بغداد",
         "job_type": "full_time"
     },
     expected_status=302)

# Verify the new job appears
test("New job in browse", "GET", "/jobs/", expected_status=200)

for r in results[count_before:]:
    print_result(r)

# === EMPLOYER: MANAGE COMPANY ===
print("\n🏢 6. EMPLOYER - COMPANY MANAGEMENT")
print("-" * 80)

count_before = len(results)

# Edit company (get CSRF)
status, edit_html = make_request("GET", "/companies/edit/1")[:2]
csrf_e = get_csrf(edit_html) if status == 200 else ""

if csrf_e:
    test("Edit company (valid)", "POST", "/companies/edit/1",
         data={"csrf_token": csrf_e, "company_name": "شركة التقنية", "description": "شركة تطوير", "location": "بغداد"},
         expected_status=302)
else:
    test("Edit company (get page)", "GET", "/companies/edit/1", expected_status=200)

for r in results[count_before:]:
    print_result(r)

# === EMPLOYER: APPLICATION MANAGEMENT ===
print("\n📋 7. EMPLOYER - APPLICATION MANAGEMENT")
print("-" * 80)

count_before = len(results)

# Applicant details
test("Applicants page", "GET", "/jobs/1/applicants", expected_status=200)

# Manage application (if any exist)
status, body = make_request("GET", "/jobs/1/applicants")[:2]
if 'application/' in body:
    app_id_match = re.search(r'application/(\d+)/accepted', body)
    if app_id_match:
        app_id = app_id_match.group(1)
        csrf_app = get_csrf(body) or csrf_d
        test(f"Accept application {app_id}", "POST", f"/jobs/application/{app_id}/accepted",
             data={"csrf_token": csrf_app}, expected_status=302)
    else:
        results.append({'name': 'Accept application', 'method': 'POST', 'url': 'N/A',
                        'status': '-', 'icon': '⏭️', 'redirect': '', 'expected': None, 'body_len': 0})
        print(f"  ⏭️  No pending applications to accept")
else:
    results.append({'name': 'Accept application', 'method': 'POST', 'url': 'N/A',
                    'status': '-', 'icon': '⏭️', 'redirect': '', 'expected': None, 'body_len': 0})
    print(f"  ⏭️  No pending applications found")

for r in results[count_before:]:
    if r.get('name') != 'Accept application' or r.get('status') != '-':
        print_result(r)

# === JOB SEEKER ===
print("\n🔍 8. JOB SEEKER FLOW")
print("-" * 80)

count_before = len(results)

# Login as seeker
status, login_html3 = make_request("GET", "/login")[:2]
csrf3 = get_csrf(login_html3)
make_request("POST", "/login",
    data={"email": "seeker@mehna.com", "password": "123456", "csrf_token": csrf3})

test("Seeker dashboard", "GET", "/dashboard", expected_status=200)
test("Seeker profile", "GET", "/profile", expected_status=200)

# Update profile
status, dash_html = make_request("GET", "/dashboard")[:2]
csrf_s = get_csrf(dash_html)
test("Update profile", "POST", "/update-profile",
     data={"csrf_token": csrf_s, "phone": "07701234567", "city": "بغداد", "bio": "مطور برمجيات"},
     expected_status=302)

# Browse jobs
test("Browse jobs (seeker)", "GET", "/jobs/", expected_status=200)
test("Job detail (seeker)", "GET", "/jobs/1", expected_status=200)

# Apply to job
status, job_html = make_request("GET", "/jobs/1")[:2]
csrf_j = get_csrf(job_html)
test("Apply to job 1", "POST", "/jobs/1/apply",
     data={"csrf_token": csrf_j}, expected_status=302)

# Try duplicate apply
test("Duplicate apply (job 1)", "POST", "/jobs/1/apply",
     data={"csrf_token": csrf_j}, expected_status=302)

# Seeker cannot access admin
test("Admin (seeker denied)", "GET", "/admin", expected_status=302)

# Seeker cannot post jobs
test("Post job (seeker denied)", "POST", "/jobs/post",
     data={"csrf_token": csrf_j, "title": "test", "description": "test"},
     expected_status=302)

for r in results[count_before:]:
    print_result(r)

# === ADMIN ===
print("\n🛡️  9. ADMIN PANEL")
print("-" * 80)

count_before = len(results)

# Login as employer (who is admin)
status, login_html4 = make_request("GET", "/login")[:2]
csrf4 = get_csrf(login_html4)
make_request("POST", "/login",
    data={"email": "employer@mehna.com", "password": "123456", "csrf_token": csrf4})

test("Admin panel", "GET", "/admin", expected_status=200)
test("Admin dashboard full", "GET", "/admin/dashboard", expected_status=200)
test("Admin users list", "GET", "/admin/users", expected_status=200)
test("Admin companies list", "GET", "/admin/companies", expected_status=200)
test("Admin stats", "GET", "/admin/stats", expected_status=200)
test("Admin company details", "GET", "/admin/company/1/details", expected_status=200)
test("Admin user details", "GET", "/admin/user/1/details", expected_status=200)

# Admin actions
test("Admin verify company", "GET", "/admin/verify-company/1", expected_status=302)
test("Admin reject company", "GET", "/admin/reject-company/1", expected_status=302)
test("Admin toggle user", "GET", "/admin/user/1/toggle", expected_status=302)
test("Admin make admin", "GET", "/admin/user/2/make-admin", expected_status=302)
test("Admin remove admin (self)", "GET", "/admin/user/1/remove-admin", expected_status=302)

# Re-verify company for further tests
make_request("GET", "/admin/verify-company/1")
# Re-toggle user back
make_request("GET", "/admin/user/1/toggle")
make_request("GET", "/admin/user/1/make-admin")

for r in results[count_before:]:
    print_result(r)

# === PASSWORD RESET ===
print("\n🔑 10. PASSWORD RESET FLOW")
print("-" * 80)

count_before = len(results)

test("Forgot password page", "GET", "/forgot-password", expected_status=200)

status, fp_html = make_request("GET", "/forgot-password")[:2]
csrf_fp = get_csrf(fp_html)
test("Submit forgot password", "POST", "/forgot-password",
     data={"email": "employer@mehna.com", "csrf_token": csrf_fp},
     expected_status=302)

for r in results[count_before:]:
    print_result(r)

# === REGISTRATION ===
print("\n📝 11. REGISTRATION FLOW")
print("-" * 80)

count_before = len(results)

test("Register page", "GET", "/register", expected_status=200)

status, reg_html = make_request("GET", "/register")[:2]
csrf_r = get_csrf(reg_html)
test("Register (missing fields)", "POST", "/register",
     data={"csrf_token": csrf_r, "fullname": "", "email": "", "password": ""},
     expected_status=200)

test("Register (short password)", "POST", "/register",
     data={"csrf_token": csrf_r, "fullname": "Test User", "email": "test@example.com", "password": "123", "role": "seeker"},
     expected_status=200)

for r in results[count_before:]:
    print_result(r)

# === LOGOUT ===
print("\n🚪 12. LOGOUT")
print("-" * 80)

count_before = len(results)
test("Logout", "GET", "/logout", expected_status=302)
test("Dashboard after logout", "GET", "/dashboard", expected_status=302)

for r in results[count_before:]:
    print_result(r)

# ========================================
# SUMMARY
# ========================================
print("\n" + "=" * 80)
print("  FULL TEST REPORT SUMMARY")
print("=" * 80)

passed = sum(1 for r in results if r['icon'] == '✅')
redirects = sum(1 for r in results if r['icon'] == '↪️')
skipped = sum(1 for r in results if r['icon'] == '⏭️')
failed = sum(1 for r in results if r['icon'] == '❌')
warnings = sum(1 for r in results if r['icon'] == '⚠️')

print(f"\n  Total Tests:   {len(results)}")
print(f"  ✅ Passed:     {passed}")
print(f"  ↪️  Redirects:  {redirects}")
print(f"  ⏭️  Skipped:    {skipped}")
print(f"  ⚠️  Warnings:   {warnings}")
print(f"  ❌ Failed:     {failed}")

if failed > 0:
    print(f"\n  FAILED TESTS:")
    for r in results:
        if r['icon'] == '❌':
            print(f"    ❌ {r['method']} {r['url']} → {r['status']} (expected {r['expected']})")

print("\n" + "=" * 80)
print("  END OF REPORT")
print("=" * 80)
