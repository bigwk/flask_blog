# coding: utf-8
# @Author   : wangkui
# @Time     : 2020/07/15 13:07
# @File     : utils
# @Platform : VSCode
from flaskblog import mail
import os
import secrets
from PIL import Image
from flask import current_app, url_for
from flask_mail import Message
from flask_login import current_user

def save_img(form_pic):
	if current_user.image_file != 'default.jpg':
		if not del_img():
			return None
	random_hex = secrets.token_hex(8)
	_, file_ext = os.path.splitext(form_pic.filename)
	img = random_hex + file_ext
	img_path = os.path.join(current_app.root_path, 'static/profile_pics', img)

	output_size = (250, 250)
	i = Image.open(form_pic)
	i.thumbnail(output_size)

	i.save(img_path)
	return img

def del_img():
	current_user_img = os.path.join(current_app.root_path, 'static/profile_pics', current_user.image_file)
	try:
		os.remove(current_user_img)
	except Exception as e:
		if type(e) is FileNotFoundError:
			return True
		return False
	else:
		return True

def reset_email(user):
	token = user.generate_user_token()
	msg = Message(subject='Reset Password', recipients=[user.email], sender='noreply@demo.com')
	msg.body = f'''
To reset your password, visit the following link:
{url_for('users.reset_request', token=token, _external=True)}

If you did not make this request then simply ignore this emial.
'''
	mail.send(msg)
