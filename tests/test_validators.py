from utils.validators import validate_email, is_valid_password, sanitize


def test_validate_email_valid():
    assert validate_email('test@example.com') is True
    assert validate_email('user.name@domain.co') is True


def test_validate_email_invalid():
    assert validate_email('') is False
    assert validate_email('notanemail') is False
    assert validate_email('@domain.com') is False
    assert validate_email('user@') is False


def test_is_valid_password_strong():
    valid, msg = is_valid_password('StrongPass1')
    assert valid is True
    assert msg == ''


def test_is_valid_password_too_short():
    valid, msg = is_valid_password('Ab1')
    assert valid is False
    assert '8 أحرف' in msg


def test_is_valid_password_no_uppercase():
    valid, msg = is_valid_password('lowercase1')
    assert valid is False
    assert 'كبير' in msg


def test_is_valid_password_no_number():
    valid, msg = is_valid_password('NoNumberHere')
    assert valid is False
    assert 'رقم' in msg


def test_sanitize_normal():
    assert sanitize('hello') == 'hello'
    assert sanitize('  hello  ') == 'hello'


def test_sanitize_max_length():
    result = sanitize('a' * 300, max_length=100)
    assert len(result) == 100


def test_sanitize_html_removal():
    result = sanitize('<script>alert("xss")</script>')
    assert '<script>' not in result


def test_sanitize_empty():
    assert sanitize('') == ''
    assert sanitize(None) == ''
