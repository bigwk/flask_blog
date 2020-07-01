from flask import render_template, url_for, flash, redirect
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
	form = RegistrationForm()
	if form.validate_on_submit():
		username = form.username.data
		email = form.email.data
		hashed_password = bcrypt.generate_password_hash(form.username.data).decode('utf-8')
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
	form = LoginForm()
	if form.validate_on_submit():
		if form.email.data == '1111@hotmail.com' and form.password.data == 'password':
			flash(f'{form.email.data} have been logged in!', 'success')
			return redirect(url_for('index'))
		else:
			flash('Login Unsuccessful. Please check username and password!', 'danger')
	return render_template('login.html', title='Login', form=form)
