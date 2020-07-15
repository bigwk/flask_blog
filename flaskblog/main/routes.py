# coding: utf-8
# @Author   : wangkui
# @Time     : 2020/07/15 13:08
# @File     : routes
# @Platform : VSCode

from flask import Blueprint, request, render_template
from flaskblog.models import Post

main = Blueprint('main', __name__)

@main.route('/')
def index():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=2)
	return render_template('home.html', posts=posts)

@main.route('/about')
def about():
	return render_template('about.html', title='About')
