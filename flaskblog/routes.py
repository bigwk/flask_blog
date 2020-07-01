from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required

from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post
from flaskblog import app, bcrypt, db

posts = [
	{
		'title': 'first post - 1',
		'author': 'wangkui',
		'date_posted': 'May 13, 2020',
		'content': 'this is the first post'
	},
		{
		'title': 'first post - 2',
		'author': 'wangkui',
		'date_posted': 'May 12, 2020',
		'content': 'this is the second post'
	},
		{
		'title': 'first post - 3',
		'author': 'wangkui',
		'date_posted': 'May 11, 2020',
		'content': 'this is the third post'
	}
]

@app.route('/')
def index():
	return render_template('home.html', posts=posts)

@app.route('/about')
def about():
	return render_template('about.html', title='About')

@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		username = form.username.data
		email = form.email.data
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=username, email=email, password=hashed_password)
		try:
			db.session.add(user)
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			flash(f'db commit error {e}', 'danger')
			return redirect(url_for('index'))
		else:
			flash(f'Account {form.username.data} has been created!', 'success')
			return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			flash(f'{form.email.data} have been logged in!', 'success')
			return redirect(next_page) if next_page else redirect(url_for('index'))
		else:
			flash('Login Unsuccessful. Please check email and password!', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/account')
@login_required
def account():
	return render_template('account.html', title=current_user.username)
