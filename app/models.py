from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db
from flask_login import UserMixin
from app import login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    r6_user = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    gifs = db.relationship('Gif', backref='author', lazy='dynamic')
    site_admin = db.Column(db.Boolean, unique=False, default=False)

    def __repr__(self):
        return f'<User {self.r6_user}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, salt_length=32)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Gif(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    frame = db.Column(db.String(256))
    mp4 = db.Column(db.String(256))
    webm = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Gif {self.id} for: {self.author}.>'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
