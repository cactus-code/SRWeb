from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, GameForm, RegistrationForm, EditProfileForm
from app.models import User, Game
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index/')
def index():
    return render_template('index.html', title='Home')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/submit/', methods=['GET', 'POST'])
@login_required
def submit():
    form = GameForm()
    if form.validate_on_submit():
        game = Game(map=form.map.data, sr_after_game=int(form.sr_after_game.data),
                    match_outcome=form.match_outcome.data,
                    author=User.query.filter_by(
                        username=current_user.username).first_or_404())
        db.session.add(game)
        db.session.commit()
        flash('Game has been added to your records.')
    return render_template('submit.html', title='Submit Game', form=form)

@app.route('/profile/')
@login_required
def default_profile():
    return redirect(url_for('profile', username=current_user.username))

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    games = user.games.all()

    return render_template('profile.html', title=current_user.username,
                           user=user, games=games)

@app.route('/edit_profile/', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html', title='Edit Profile', form=form)
