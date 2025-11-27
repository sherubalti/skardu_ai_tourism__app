import os

# Flask configuration
SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'

# Session configuration
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = False
SESSION_USE_SIGNER = True

# File upload configuration
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# CORS configuration
CORS_HEADERS = 'Content-Type'
