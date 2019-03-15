from flask import render_template, flash, redirect, url_for, request, session, abort
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Gif
from datetime import datetime


@app.route('/')
@login_required
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    gifs = Gif.query.all()
    return render_template('home.html', gifs=gifs)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
        login_user(user)
        app.logger.info(f'{user} logged in.')
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/gif/inspect/<id>', methods=['GET', 'POST'])
@login_required
def gif_inpect(id):
    gif = Gif.query.get(id)
    user = gif.author
    return render_template('gif_inspect.html', gif=gif, user=user)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been successfully logged out.', 'success')
    return redirect(url_for('login'))


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
