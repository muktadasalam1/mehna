import re


def sanitize(text, max_length=500):
    if not text:
        return ''
    text = text.strip()
    text = re.sub(r'<[^>]+>', '', text)
    text = text[:max_length]
    return text


def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def escape_html(text):
    if not text:
        return ''
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    return text


def is_valid_password(pw):
    if len(pw) < 8:
        return False, "كلمة المرور يجب أن تكون 8 أحرف على الأقل"
    if not re.search(r'[A-Z]', pw):
        return False, "كلمة المرور يجب أن تحتوي حرف كبير واحد على الأقل"
    if not re.search(r'[0-9]', pw):
        return False, "كلمة المرور يجب أن تحتوي رقم واحد على الأقل"
    return True, ""
