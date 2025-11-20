import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'skardu-ai-tourism-secret-key-2024'
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # AI Model Configurations
    SIMILARITY_THRESHOLD = 0.6
    MAX_RECOMMENDATIONS = 10
    
    # Chatbot Configurations
    CHATBOT_MAX_HISTORY = 10
    CHATBOT_RESPONSE_TIMEOUT = 30