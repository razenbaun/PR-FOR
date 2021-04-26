from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.Column(db.String(64), nullable=False)
    rank = db.Column(db.String, nullable=False)

    def __repr__(self):
        return 'Article %r' % self.id


class Users(db.Model):
    nickname = db.Column(db.String(64), nullable=False, primary_key=True)
    password = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return 'Users %r' % self.nickname


@app.route('/')  # главная страница
def index():
    return render_template('index.html')


flag = 0  # флаг проверяющий зарегистрирован пользователь или нет


@app.route('/about')
def about():
    global flag
    if flag == 0:
        return render_template('about.html', flag=flag)
    else:
        global nick
        return render_template('about.html', flag=flag, nick=nick)


@app.route('/my-posts', methods=['POST', 'GET'])
def my_posts():
    global nick
    try:
        if request.method == "POST":
            fl1 = request.form['fl1']
            fl2 = request.form['fl2']
            # articles = Article.query.filter(Article.rank == "игры").order_by(Article.date.desc()).all()
            if fl1 == "сначала старые":
                if fl2 == "все":
                    articles = Article.query.filter(Article.author == nick).all()
                else:
                    articles = Article.query.filter(Article.rank == fl2).all()
            else:
                if fl2 == "все":
                    articles = Article.query.filter(Article.author == nick).order_by(Article.date.desc()).all()
                else:  # магия, не трогать
                    articles = Article.query.filter(Article.rank == fl2,
                                                    Article.author == nick).order_by(Article.date.desc()).all()
            return render_template('my-posts.html', articles=articles)
        else:
            articles = Article.query.filter(Article.author == nick).order_by(Article.date.desc()).all()
            return render_template('my-posts.html', articles=articles)
    except:
        articles = Article.query.filter(Article.author == nick).order_by(Article.date.desc()).all()
        return render_template('my-posts.html', articles=articles)


@app.route('/sign-in', methods=['POST', 'GET'])
def sign_in():
    if request.method == "POST":
        nickname = request.form['nickname']
        password = request.form['password']

        global nick
        nick = nickname

        flag_there = True

        try:
            con = sqlite3.connect("users.db")
            cur = con.cursor()
            result = cur.execute("""SELECT * FROM users""").fetchall()
            for item in result:
                if nickname == item[0] and password == item[1]:
                    global flag
                    flag = 1
                    flag_there = False  # флаг - ложь если пользователь найден
                    con.close()
                    return redirect('/about')
            if flag_there:
                con.close()
                return redirect('/sign-in-error')
        except:
            return "123"
    else:
        return render_template('sign-in.html')


@app.route('/sign-in-error', methods=['POST', 'GET'])  # вызывается если пароль введён неверно или имени нет в дб
def sign_in_error():
    if request.method == "POST":
        nickname = request.form['nickname']
        password = request.form['password']

        global nick
        nick = nickname

        flag_there = True

        try:
            con = sqlite3.connect("users.db")
            cur = con.cursor()
            result = cur.execute("""SELECT * FROM users""").fetchall()
            for item in result:
                if nickname == item[0] and password == item[1]:
                    global flag
                    flag = 1
                    flag_there = False
                    con.close()
                    return redirect('/about')
            if flag_there:
                return redirect('/sign-in-error')
                con.close()
        except:
            return "123"
    else:
        return render_template('sign-in-error.html')


@app.route('/sign-out')
def sign_out():
    global flag
    flag = 0
    return redirect('/about')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        nickname = request.form['nickname']
        password = request.form['password']

        global nick
        nick = nickname

        user = Users(nickname=nickname, password=password)

        try:
            db.session.add(user)
            db.session.commit()
            global flag
            flag = 1
            return redirect('/about')

        except:
            return redirect('/register-error')
    else:
        return render_template('register.html')


@app.route('/register-error', methods=['POST', 'GET'])  # +- что и sign-error
def register_error():
    if request.method == "POST":
        nickname = request.form['nickname']
        password = request.form['password']

        global nick
        nick = nickname

        user = Users(nickname=nickname, password=password)

        try:
            db.session.add(user)
            db.session.commit()
            global flag
            flag = 1
            return redirect('/about')

        except:
            return redirect('/register-error')
    else:
        return render_template('register-error.html')


@app.route('/posts', methods=['POST', 'GET'])
def posts():
    try:
        if request.method == "POST":
            fl1 = request.form['fl1']
            fl2 = request.form['fl2']
            # articles = Article.query.filter(Article.rank == "игры").order_by(Article.date.desc()).all()
            if fl1 == "сначала старые":
                if fl2 == "все":
                    articles = Article.query.all()
                else:
                    articles = Article.query.filter(Article.rank == fl2).all()
            else:
                if fl2 == "все":
                    articles = Article.query.order_by(Article.date.desc()).all()
                else:
                    articles = Article.query.filter(Article.rank == fl2).order_by(Article.date.desc()).all()
            return render_template('posts.html', articles=articles)
        else:
            articles = Article.query.order_by(Article.date.desc()).all()
            return render_template('posts.html', articles=articles)
    except:
        articles = Article.query.order_by(Article.date.desc()).all()
        return render_template('posts.html', articles=articles)


@app.route('/posts/<int:id>')
def post_id(id):
    global flag
    article = Article.query.get(id)
    return render_template('post-id.html', article=article, flag=flag)


@app.route('/posts/<int:id>/delete')
def post_id_delete(id):
    global flag
    article = Article.query.get(id)
    global nick
    if flag == 1 and nick == article.author:
        try:
            db.session.delete(article)
            db.session.commit()
            return redirect("/posts")
        except:
            return "При удалении статьи произошла ошибка!"
    return render_template('post-id-delete.html', article=article, flag=flag, nick=nick)


@app.route('/posts/<int:id>/update', methods=['POST', 'GET'])
def post_id_update(id):
    try:
        article = Article.query.get(id)
        global flag
        global nick
        if flag == 1 and nick == article.author:
            if request.method == "POST":
                article.title = request.form['title']
                article.intro = request.form['intro']
                article.text = request.form['text']
                article.rank = request.form['rank']

                try:
                    db.session.commit()
                    return redirect('/posts')
                except:
                    return "При редактировании статьи произошла ошибка!"
    except:
        return "Укажите категорию!"

    return render_template('post-id-update.html', article=article, flag=flag, nick=nick)


@app.route('/create-article', methods=['POST', 'GET'])
def create_article():
    try:
        if request.method == "POST":
            global flag
            global nick
            author = nick
            title = request.form['title']
            intro = request.form['intro']
            text = request.form['text']
            rank = request.form['rank']
            # if len(str(title)) == 0 or len(str(intro)) == 0 or len(str(text)) == 0 or len(str(rank)) == 0:
            #     return render_template('error-1.html')

            article = Article(author=author, title=title, intro=intro, text=text, rank=rank)

            try:
                db.session.add(article)
                db.session.commit()
                return redirect('/posts')

            except:
                return "При добавлении статьи произошла ошибка"
        else:
            return render_template('create-article.html', flag=flag)
    except:
        return render_template('create-article-error.html', flag=flag)


@app.route('/create-article-error', methods=['POST', 'GET'])
def create_article_error():
    try:
        if request.method == "POST":
            global flag
            global nick
            author = nick
            title = request.form['title']
            intro = request.form['intro']
            text = request.form['text']
            rank = request.form['rank']
            # if len(str(title)) == 0 or len(str(intro)) == 0 or len(str(text)) == 0 or len(str(rank)) == 0:
            #     return render_template('error-1.html')

            article = Article(author=author, title=title, intro=intro, text=text, rank=rank)

            try:
                db.session.add(article)
                db.session.commit()
                return redirect('/posts')

            except:
                return "При добавлении статьи произошла ошибка"
        else:
            return render_template('create-article-error.html', flag=flag)
    except:
        return render_template('create-article-error.html', flag=flag)


if __name__ == "__main__":
    app.run(debug=False)
