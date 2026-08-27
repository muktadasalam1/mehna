import re


def sanitize(value, max_length=255, allow_html=False):
    if not value:
        return ''
    value = str(value).strip()
    value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    if not allow_html:
        value = re.sub(r'<[^>]*>', '', value)
    return value[:max_length]


def validate_email(email):
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))


def escape_html(text):
    if not text:
        return ''
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')


def is_valid_password(pw):
    if len(pw) < 6:
        return False, "كلمة المرور قصيرة"
    return True, ""
