from app import db
from app.models import User
from datetime import datetime, timedelta


def active_this_week():
    week = datetime.now() - timedelta(days=7)
    users = [u for u in User.query.all() if u.last_seen >= week]
    return(len(users))