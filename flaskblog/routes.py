import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required

from datetime import datetime

from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, CreatePostForm
from flaskblog.models import User, Post
from flaskblog import app, bcrypt, db

post = [
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
	posts = Post.query.all()
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
	if current_user.image_file != 'default.jpg':
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
	

@app.route('/account/<string:user_name>', methods=['GET', 'POST'])
@login_required
def account(user_name):
	if user_name != current_user.username:
		abort(403)
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.image.data:
			image_file = save_img(form.image.data)
			if image_file == None:
				flash('Upload image failed. Please try again!', 'danger')
				return redirect(url_for('account', user_name=current_user.username))
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
			return redirect(url_for('account', user_name=current_user.username))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('account.html', title=current_user.username, image_file=image_file, form=form)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
	form = CreatePostForm()
	if form.validate_on_submit():
		title = form.title.data
		content = form.content.data
		author = current_user
		post = Post(title=title, date_posted=datetime.today().ctime(), content=content, author=author)
		try:
			db.session.add(post)
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			flash(f'create post error {e}', 'danger')
		else:
			flash(f'Post {form.title.data} has been created!', 'success')
			return redirect(url_for('index'))
	return render_template('create_post.html', title='New Post', form=form, legend='New Post')

@app.route('/post/<int:post_id>')
@login_required
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html', title=post.title, post=post)


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form = CreatePostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			flash(f'update post error {e}', 'danger')
		else:
			flash(f'update post success', 'success')
		finally:
			return redirect(url_for('post', post_id=post.id))

	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
	return render_template('create_post.html', title=post.title, form=form, legend='Update Post')

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)

	try:
		db.session.delete(post)
		db.session.commit()
	except Exception as e:
		db.session.rollback()
		flash(f'delete post error {e}', 'danger')
	else:
		flash(f'delete post success', 'success')
	finally:
		return redirect(url_for('index'))
