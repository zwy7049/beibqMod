#coding: utf-8
from datetime import datetime
from app.models.model import *
from flask_login import UserMixin,AnonymousUserMixin
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.includes import file 
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

PREFIX = ""


class User(UserMixin, db.Model):
    """ user table """
    __tablename__ = db.PREFIX + PREFIX + "user"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8"
    }

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False, index=True, default="")
    nickname = db.Column(db.String(255), nullable = False, default="")
    password =  db.Column(db.String(255), default="")
    avatar = db.Column(db.String(255),  default="")
	
    confirmed = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(64), unique=True, index=True)
	
    updatetime = db.Column(db.DateTime, default = datetime.now, nullable=False)
    timestamp = db.Column(db.DateTime, default = datetime.now, nullable=False)
    books = db.relationship("Book", backref="user", lazy="dynamic")
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
  
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
		
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    @staticmethod
    def add(username, password):
        user = User.query.filter_by(username=username).first()
        if user is not None:
            return
        user = User()
        user.username = username
        user.nickname = username
        user.password = generate_password_hash(password)
        user.avatar = file.new_avatar()
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get(id):
        return User.query.filter_by(id=id).first()

    @staticmethod
    def getbyname(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def page(page, per_page):
        return User.query.paginate(page, 
            per_page=per_page, error_out = False)

    def setting(self, nickname):
        self.nickname = nickname

    def change_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def page_book(self, page, per_page):
        from .book import Book
        books = Book.query.filter_by(user_id=self.id)\
            .options(db.Load(Book).undefer("brief"))\
            .order_by(Book.publish_timestamp.desc())\
            .paginate(page, per_page=per_page, error_out=False)
        return books

    def page_draft(self, page, per_page):
        from .book import Book
        books = Book.query.filter_by(user_id=self.id)\
                .filter(Book.updatetime>Book.publish_timestamp)\
                .options(db.Load(Book).undefer("brief"))\
                .order_by(Book.publish_timestamp.desc())\
                .paginate(page, per_page=per_page, error_out=False)
        return books

    def count_book(self):
        return self.books.count()

    def count_draft(self):
        from .book import Book
        num = Book.query.filter_by(user_id=self.id)\
                .filter(Book.updatetime>Book.publish_timestamp)\
                .count()
        return num

    def _20px_avatar(self):
        image_path = current_app.config["AVATAR_PATH"]
        return "/".join([image_path, "20_20_{}".format(self.avatar)])
    
    def _50px_avatar(self):
        image_path = current_app.config["AVATAR_PATH"]
        return "/".join([image_path, "50_50_{}".format(self.avatar)])

    def origin_avatar(self):
        image_path = current_app.config["AVATAR_PATH"]
        return "/".join([image_path, self.avatar])

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)
        return True



		
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser
		
		
@login_manager.user_loader
def load_user(id):
    if current_app.start:
        return User.query.get(int(id))
    return



