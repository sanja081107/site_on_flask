from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# -------------------------------------------------------------------

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id

# -------------------------------------------------------------------

menu = [{'title': 'Главная', 'url_name': ''},
        {'title': 'Добавить статью', 'url_name': 'add_article'},
        {'title': 'Все статьи', 'url_name': 'all_articles'},
        {'title': 'Обо мне', 'url_name': 'about'}]

def get_user_data(**kwargs):
    context = kwargs
    menus = menu.copy()
    context['menu'] = menus
    return context

# -------------------------------------------------------------------

@app.route(f"/{menu[0]['url_name']}")
def home():
    context = get_user_data(title='Home', body='Home page')
    return render_template('index.html', context=context)


@app.route(f"/{menu[1]['url_name']}", methods=['GET', 'POST'])
def add_article():
    if request.method == 'POST':
        form = request.form
        post = Article(title=form['title'], intro=form['intro'], text=form['text'])
        try:
            db.session.add(post)
            db.session.commit()
            post = Article.query.order_by(Article.date.desc())
            return redirect(f"/{menu[2]['url_name']}/{post[0].id}")
        except:
            return 'Error'

    context = get_user_data(title='Add', body='Add article page')
    return render_template('add_article.html', context=context)

@app.route(f"/{menu[2]['url_name']}")
def all_articles():
    posts = Article.query.order_by(Article.date.desc()).all()
    context = get_user_data(title='All', body='All articles page')
    context['posts'] = posts
    return render_template('posts.html', context=context)

@app.route(f"/{menu[2]['url_name']}/<int:pk>")
def post_detail(pk):
    posts = Article.query.get(pk)
    context = get_user_data(title='Detail', body='Detail page')
    context['post'] = posts
    return render_template('post_detail.html', context=context)

@app.route(f"/{menu[3]['url_name']}")
def about():
    context = get_user_data(title='About', body='About page')
    return render_template('about.html', context=context)

@app.route(f"/update/<int:id>", methods=['GET', 'POST'])
def post_update(id):
    context = get_user_data(title='Update', body='Update page')
    post = Article.query.get(id)
    context['post'] = post
    if request.method == 'POST':
        post.title = request.form['title']
        post.intro = request.form['intro']
        post.text = request.form['text']
        try:
            db.session.commit()
            return redirect(f"/{menu[2]['url_name']}/{id}")
        except:
            return 'Error update'

    return render_template('post_update.html', context=context)

@app.route(f"/delete/<int:id>")
def post_delete(id):
    context = get_user_data(title='Delete', body='Delete page')
    post = Article.query.get_or_404(id)
    try:
        db.session.delete(post)
        db.session.commit()
        return redirect(f"/{menu[2]['url_name']}")
    except:
        return 'Error delete'

# -------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
