class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = b'your-secret-key'

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True