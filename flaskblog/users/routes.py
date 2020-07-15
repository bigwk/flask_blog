# coding: utf-8
# @Author   : wangkui
# @Time     : 2020/07/15 13:07
# @File     : routes
# @Platform : VSCode
from flaskblog.users.utils import reset_email, save_img
from flaskblog.users.forms import LoginForm, RegistrationForm, ResetPasswordForm, ResetRequestEmailForm, UpdateAccountForm
from flask import Blueprint, redirect, url_for, flash, render_template, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from flaskblog.models import User, Post
from flaskblog import bcrypt, db

users = Blueprint('users', __name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
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
			return redirect(url_for('main.index'))
		else:
			flash(f'Account {form.username.data} has been created!', 'success')
			return redirect(url_for('users.login'))
	return render_template('register.html', title='Register', form=form)

@users.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			flash(f'{form.email.data} have been logged in!', 'success')
			return redirect(next_page) if next_page else redirect(url_for('main.index'))
		else:
			flash('Login Unsuccessful. Please check email and password!', 'danger')
	return render_template('login.html', title='Login', form=form)

@users.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('main.index'))

@users.route('/account/<string:user_name>', methods=['GET', 'POST'])
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
				return redirect(url_for('users.account', user_name=current_user.username))
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
			return redirect(url_for('users.account', user_name=current_user.username))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('account.html', title=current_user.username, image_file=image_file, form=form)

@users.route('/posts/<string:user_name>', methods=['GET', 'POST'])
def user_posts(user_name):
	user = User.query.filter_by(username=user_name).first_or_404()
	page = request.args.get('page', 1, type=int)
	posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=2)
	# posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=2)
	return render_template('user_posts.html', posts=posts, user=user)

@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	form = ResetRequestEmailForm()
	if form.validate_on_submit():
		# send reset email
		user = User.query.filter_by(email=form.email.data).first()
		reset_email(user)
		flash('An email has been sent with instructions to reset your password.', 'info')
		return redirect(url_for('users.login'))
	return render_template('reset_request.html', title='Reset Password', form=form)

@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	user = User.verify_user_token(token)
	if user == None:
		flash('Request link has been experied or invalid.', 'warning')
		return redirect(url_for('users.reset_request'))
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
			return redirect(url_for('users.login'))
	return render_template('reset_token.html', title='Reset Password', form=form)
