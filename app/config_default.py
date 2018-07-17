#coding:utf-8
import os

class Config(object):
    DEBUG = False
    SECRET_KEY = 'this is secret string'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://froot:password@localhost/beibq?charset=utf8'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD =  os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[JieWenShe]'
    FLASKY_MAIL_SENDER = os.environ.get('MAIL_USERNAME')
    FLASKY_ADMIN = os.environ.get('MAIL_USERNAME')

	
	
    # catalog max depth
    CATALOG_DEEP = 3
    ERROR_LOG = "../logs/error.log"
    INFO_LOG = "../logs/info.log"

    DB_PREFIX = "bb_"
    PER_PAGE = 20

    STATIC_IMG_PATH = "img"

    AVATAR_PATH = "resource/image/avatar"
    TMP_PATH = "resource/tmp"
    IMAGE_PATH = "resource/image/image"

    BOOK_COVER_PATH = "resource/image/cover"



