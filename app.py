# coding: utf-8

import sys
import os
from flask import Flask, render_template, session, redirect, url_for
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

reload(sys)
sys.setdefaultencoding('utf-8')
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def inter_server_error(e):
    return render_template('500.html'), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    text = None
    filedata = None
    form = TextForm()
    keywords = {}
    if form.validate_on_submit():
        if form.upload.data:
            filedata = form.upload.data
            text = "".join([line.decode(chardet.detect(line)['encoding']) for line in filedata.readlines()])
            #session['text'] = text
            print secure_filename(form.upload.data.filename)
            #form.upload.data.save()
        else:
            text = form.text.data
        num = form.num.data
        method = form.method.data
        #num = session['text'].count('\n') + 1
        keywords = analysis.text_processing(text, method=method, num=num, pos=['n'])
        result = "'" + json.dumps(keywords, ensure_ascii=False) + "'"
        return redirect(url_for('result', resultstr=result))
    return render_template('index.html', form=form)

@app.route('/result/<resultstr>', methods=['GET', 'POST'])
def result(resultstr):
    return render_template('result.html', keywords=resultstr)

if __name__ == '__main__':
    manager.run()
