# coding: utf-8

import sys
import os
from flask import Flask, render_template, session, redirect, url_for, request
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import TextAreaField, SubmitField, IntegerField, SelectField, BooleanField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import Required, Optional
from werkzeug import secure_filename
import analysis
import json
import chardet
import cPickle as pickle
import hashlib
import random
import string
import time

reload(sys)
sys.setdefaultencoding('utf-8')
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = set(['txt'])

app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class TextForm(Form):
    text = TextAreaField('请输入需要提取关键词的文本')
    upload = FileField('文件上传', validators=[
        Optional(), FileAllowed(['txt'], '只能上传txt格式的文件！')
        ])
    num = IntegerField('关键词个数', validators=[Required()])
    method = SelectField('提取方法', choices=[('tfidf', 'tfidf'), ('textrank', 'textrank')])
    #pos_n = BooleanField('名词')
    #pos_v = BooleanField('动词')
    #pos_a = BooleanField('名词')
    #pos_ad = BooleanField('副词')
    submit = SubmitField('提交')

def get_salt(chars = string.letters + string.digits):
    return "".join([random.choice(chars) for t in range(16)])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def generate_flag():
    salt = get_salt()
    now = str(int(time.time() * 1000000))
    flag = hashlib.md5(now+salt).hexdigest()
    return flag

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def inter_server_error(e):
    return render_template('500.html'), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    form = TextForm()
    return render_template('index.html', form=form)

#@app.route('/result/<flag>', methods=['GET', 'POST'])
@app.route('/result/', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        uploadfile = request.files['upload']
        if uploadfile:
            if allowed_file(uploadfile.filename):
                text = "".join([line.decode(chardet.detect(line)['encoding']) for line in uploadfile.readlines()])
            else:
                return rediect(url_for('index'))
        else:
            text = request.form['text']
            if not text:
                return rediect(url_for('index'))
        num = int(request.form['num'])
        method = request.form['method']
        keywords, network, vertice = analysis.text_processing(text, method=method, num=num, pos=['n'])
        result = "'" + json.dumps(keywords, ensure_ascii=False) + "'"
        print result
    return render_template('result.html', keywords=result, vertice=vertice, network=network)

if __name__ == '__main__':
    manager.run()
