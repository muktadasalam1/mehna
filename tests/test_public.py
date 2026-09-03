def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'مهنة' in response.data.decode('utf-8')


def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert 'تسجيل الدخول' in response.data.decode('utf-8')


def test_register_page(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert 'حساب جديد' in response.data.decode('utf-8')


def test_jobs_page(client):
    response = client.get('/jobs')
    assert response.status_code == 200


def test_pricing_page(client):
    response = client.get('/pricing')
    assert response.status_code == 200


def test_about_page(client):
    response = client.get('/about')
    assert response.status_code == 200


def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'


def test_404_page(client):
    response = client.get('/nonexistent-page')
    assert response.status_code == 404


def test_dashboard_redirect(client):
    response = client.get('/dashboard')
    assert response.status_code == 302
