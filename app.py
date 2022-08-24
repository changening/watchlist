import os
import sys
import click

from flask import Flask,render_template, request, url_for, redirect, flash
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy


# SQLite URI 兼容配置
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'   # 如果是 Windows 系统，使用三个斜线
else:
    prefix = 'sqlite:////'  # 否则使用四个斜线

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev' # 设置签名所需的密钥
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)

# 表名将会是 user（自动生成，小写处理）
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


# 表名将会是 movie
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


# 自定义命令来自动执行创建数据库表操作
@app.cli.command()    # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    if drop:          # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.') # 输出提示信息


# 生成虚拟数据到数据库
@app.cli.command()
def forge():
    db.create_all()
    name = 'changing'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    # 定义user的名字后提交到数据库
    user = User(name=name)
    db.session.add(user)

    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('data were created')


# 上下文处理函数
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)


# 处理表单数据
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 获取表单数据
        title = request.form.get('title')
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60 or year < 1900:
            flash('Invalid input') # 显示错误提示
            return redirect(url_for('index')) # 重定向回主页
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year) # 创建记录
        db.session.add(movie) # 添加到数据库
        db.session.commit()   # 提交数据会话
        return redirect(url_for('index')) # 重定向回主页

    movies = Movie.query.all()
    return render_template('index.html', movies=movies)


# 编辑电影条目
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    # 使用了get_or_404()方法，它会返回对应主键的记录，如果没有找到，则返回404错误响应
    movie = Movie.query.get_or_404(movie_id)
    if request.method == 'POST':
        # 获取表单数据
        title = request.form.get('title')
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60 or year < 1900:
            flash('Invalid input') # 显示错误提示
            return redirect(url_for('edit', movie_id=movie_id)) # 重定向回对应的编辑页面
        # 保存表单数据到数据库
        movie.title = title # 更新标题
        movie.year = year   # 更新年份
        db.session.commit()   # 提交数据会话
        return redirect(url_for('index')) # 重定向回主页

    return render_template('index.html', movie=movie)


# 错误处理函数
@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    return render_template('404.html'), 404  # 返回模板和状态码


# 删除电影条目
@app.route('/movie/delote/<int:movie_id>', methods=['POST']) # 限定只接受POST请求
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id) # 获取电影记录
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index')) # 重定向回主页

