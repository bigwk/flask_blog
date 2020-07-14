import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from datetime import datetime

from flask_wtf import form

from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm, CreatePostForm,
								ResetRequestEmailForm, ResetPasswordForm)
from flaskblog.models import User, Post
from flaskblog import app, bcrypt, db, mail


@app.route('/')
def index():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=2)
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

@app.route('/posts/<string:user_name>', methods=['GET', 'POST'])
def user_posts(user_name):
	user = User.query.filter_by(username=user_name).first_or_404()
	page = request.args.get('page', 1, type=int)
	posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=2)
	# posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=2)
	return render_template('user_posts.html', posts=posts, user=user)


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

def reset_email(user):
	token = user.generate_user_token()
	msg = Message(subject='Reset Password', recipients=[user.email], sender='noreply@demo.com')
	msg.body = f'''
To reset your password, visit the following link:
{url_for('reset_request', token=token, _external=True)}

If you did not make this request then simply ignore this emial.
'''
	mail.send(msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = ResetRequestEmailForm()
	if form.validate_on_submit():
		# send reset email
		user = User.query.filter_by(email=form.email.data).first()
		reset_email(user)
		flash('An email has been sent with instructions to reset your password.', 'info')
		return redirect(url_for('login'))
	return render_template('reset_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	user = User.verify_user_token(token)
	if user == None:
		flash('Request link has been experied or invalid.', 'warning')
		return redirect(url_for('reset_request'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		# change password
		password = form.password.data
		hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
		user.password = hashed_password
		try:
			db.session.commit()
		except:
			flash('Reset password error!', 'danger')
		else:
			flash('Reset password success!', 'success')
			return redirect(url_for('login'))
	return render_template('reset_token.html', title='Reset Password', form=form)
