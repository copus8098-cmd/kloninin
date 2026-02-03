import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'bmp',
    'pdf', 'doc', 'docx', 'json', 'txt'
}

MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20MB
