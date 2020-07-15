# coding: utf-8
# @Author   : wangkui
# @Time     : 2020/07/15 13:32
# @File     : forms
# @Platform : VSCode
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

class CreatePostForm(FlaskForm):
	"""docstring for CreatePostForm"""
	title = StringField('Title', validators=[DataRequired(), Length(min=1, max=50)])
	content = TextAreaField('Content', validators=[DataRequired()])
	submit = SubmitField('Submit')
