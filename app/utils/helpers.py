import secrets
import string

def generate_random_string(length=20):
    """Generate a random string for unique IDs"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def validate_file_suffix(suffix):
    """Validate file suffix/extension"""
    allowed_suffixes = {'exe', 'zip', 'rar', 'png', 'doc', 'docx', 'xls', 'xlsx', 'txt'}
    return suffix.lower() in allowed_suffixes