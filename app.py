from flask import Flask
from markupsafe import escape
from flask import url_for


app = Flask(__name__)

@app.route('/')
# @app.route('/home')
# @app.route('/index')
def hello():
    return '<h1>你好小屁孩</h1><img src="https://up.54fcnr.com/pic_source/72/c8/f0/72c8f01c9b417bf07708e0373c645a12.gif">'


@app.route('/user/<name>')
def user_page(name):
    return f'user: {escape(name)}'


@app.route('/test')
def test_url_for():
    print(url_for('hello'))
    print(url_for('user_page', name='greyli'))  # 输出：/user/greyli
    # 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到 URL 后面。
    print(url_for('test_url_for', num=2))  # 输出：/test?num=2
    return '你好呀'