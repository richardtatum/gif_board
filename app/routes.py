from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Gif
from werkzeug.urls import url_parse
from datetime import datetime
from scripts import active_this_week


@app.route('/')
@login_required
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    gifs = Gif.query.all()
    users = len(User.query.all())
    active = active_this_week()
    return render_template('home.html', gifs=gifs, users=users, active=active)


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
        if not user.site_admin:
            flash('Access forbidden.', 'danger')
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
def gif_inspect(id):
    gif = Gif.query.get(id)
    user = gif.author
    return render_template('gif_inspect.html', gif=gif, user=user)


@app.route('/gif/delete/<id>')
@login_required
def gif_delete(id):
    gif = Gif.query.filter_by(id=id).first_or_404()
    db.session.delete(gif)
    db.session.commit()
    flash(f'Clip {id} deleted.', 'success')
    return redirect(url_for('home'))


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
