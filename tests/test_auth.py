def test_login_success(client, seed_users):
    response = client.post('/login', data={
        'email': 'seeker@test.com',
        'password': 'Password1'
    }, follow_redirects=False)
    assert response.status_code == 302


def test_login_wrong_password(client, seed_users):
    response = client.post('/login', data={
        'email': 'seeker@test.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'بيانات خاطئة' in response.data.decode('utf-8')


def test_login_nonexistent_user(client, seed_users):
    response = client.post('/login', data={
        'email': 'nonexistent@test.com',
        'password': 'Password1'
    }, follow_redirects=True)
    assert response.status_code == 200


def test_register_success(client, seed_users):
    response = client.post('/register', data={
        'email': 'newuser@test.com',
        'password': 'Password1',
        'fullname': 'New User',
        'role': 'seeker'
    }, follow_redirects=False)
    assert response.status_code == 302


def test_register_duplicate_email(client, seed_users):
    response = client.post('/register', data={
        'email': 'seeker@test.com',
        'password': 'Password1',
        'fullname': 'Duplicate',
        'role': 'seeker'
    }, follow_redirects=True)
    assert response.status_code == 200


def test_register_weak_password(client, seed_users):
    response = client.post('/register', data={
        'email': 'weak@test.com',
        'password': '123',
        'fullname': 'Weak Pass',
        'role': 'seeker'
    }, follow_redirects=True)
    assert response.status_code == 200


def test_logout(client, seed_users):
    client.post('/login', data={
        'email': 'seeker@test.com',
        'password': 'Password1'
    })
    response = client.get('/logout', follow_redirects=False)
    assert response.status_code == 302


def test_dashboard_seeker(client, seed_users):
    client.post('/login', data={
        'email': 'seeker@test.com',
        'password': 'Password1'
    })
    response = client.get('/dashboard')
    assert response.status_code == 200


def test_dashboard_employer(client, seed_users):
    client.post('/login', data={
        'email': 'employer@test.com',
        'password': 'Password1'
    })
    response = client.get('/dashboard')
    assert response.status_code == 200


def test_unauthenticated_dashboard(client):
    response = client.get('/dashboard')
    assert response.status_code == 302
