class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = b'"\xe4\x7fTsrn[\xb7Vl\x94\xde\xaeQG'


class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True