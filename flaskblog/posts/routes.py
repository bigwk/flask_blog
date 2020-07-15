# coding: utf-8
# @Author   : wangkui
# @Time     : 2020/07/15 13:08
# @File     : routes
# @Platform : VSCode
from datetime import datetime
from flaskblog.posts.forms import CreatePostForm
from flaskblog import db
from flask import Blueprint, flash, redirect, render_template, url_for, abort, request
from flask_login import login_required, current_user
from flaskblog.models import Post

posts = Blueprint('posts', __name__)

@posts.route('/post/new', methods=['GET', 'POST'])
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
			return redirect(url_for('main.index'))
	return render_template('create_post.html', title='New Post', form=form, legend='New Post')

@posts.route('/post/<int:post_id>')
@login_required
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html', title=post.title, post=post)


@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
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
			return redirect(url_for('posts.post', post_id=post.id))

	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
	return render_template('create_post.html', title=post.title, form=form, legend='Update Post')

@posts.route('/post/<int:post_id>/delete', methods=['POST'])
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
		return redirect(url_for('main.index'))
