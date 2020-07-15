# coding: utf-8
# @Author   : wangkui
# @Time     : 2020/07/15 15:19
# @File     : handler
# @Platform : VSCode
from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
def handler_404(error):
    return render_template('errors/404.html', error=error), 404

@errors.app_errorhandler(403)
def handler_403(error):
    return render_template('errors/403.html', error=error), 403

@errors.app_errorhandler(500)
def handler_500(error):
    return render_template('errors/500.html', error=error), 500