import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required

from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flaskblog.models import User, Post
from flaskblog import app, bcrypt, db

posts = [
	{
		'title': 'first post - 1',
		'author': 'bigwk',
		'date_posted': 'May 13, 2020',
		'content': 'this is the first post'
	},
		{
		'title': 'first post - 2',
		'author': 'bigwk',
		'date_posted': 'May 12, 2020',
		'content': 'this is the second post'
	},
		{
		'title': 'first post - 3',
		'author': 'bigwk',
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

def save_img(form_pic):
	if not del_img():
		return None
	random_hex = secrets.token_hex(8)
	_, file_ext = os.path.splitext(form_pic.filename)
	img = random_hex + file_ext
	img_path = os.path.join(app.root_path, 'static/profile_pics', img)

	output_size = (250, 250)
	i = Image.open(form_pic)
	i.thumbnail(output_size)

	i.save(img_path)
	return img

def del_img():
	current_user_img = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)
	try:
		os.remove(current_user_img)
	except Exception as e:
		if type(e) is FileNotFoundError:
			return True
		return False
	else:
		return True
	

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.image.data:
			image_file = save_img(form.image.data)
			if image_file == None:
				flash('Upload image failed. Please try again!', 'danger')
				return redirect(url_for('account'))
			current_user.image_file = image_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			flash(f'update account error {e}', 'danger')
		else:
			flash(f'update account success', 'success')
		finally:
			return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('account.html', title=current_user.username, image_file=image_file, form=form)
