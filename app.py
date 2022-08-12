from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from cloudipsp import Api, Checkout

# DataBases---------------------------------------------------------------

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id

# Mixins-------------------------------------------------------------------

menu = [{'title': 'Главная', 'url_name': ''},
        {'title': 'Добавить товар', 'url_name': 'product_add'},
        {'title': 'Все товары', 'url_name': 'products_all'},
        {'title': 'Обо мне', 'url_name': 'about'}]

def get_user_data(**kwargs):
    context = kwargs
    menus = menu.copy()
    context['menu'] = menus
    return context

# Functions----------------------------------------------------------------

@app.route(f"/{menu[0]['url_name']}")
def home():
    context = get_user_data(title='Home', body='Home page')
    return render_template('index.html', context=context)


@app.route(f"/{menu[1]['url_name']}", methods=['GET', 'POST'])
def product_add():
    if request.method == 'POST':
        form = request.form
        post = Article(title=form['title'], intro=form['intro'], text=form['text'], price=form['price'])
        try:
            db.session.add(post)
            db.session.commit()
            post = Article.query.order_by(Article.date.desc())
            return redirect(f"/{menu[2]['url_name']}/{post[0].id}")
        except:
            return 'Error'

    context = get_user_data(title='Add product', body='Add product page')
    return render_template('product_add.html', context=context)

@app.route(f"/{menu[2]['url_name']}")
def products_all():
    posts = Article.query.order_by(Article.date.desc()).all()
    context = get_user_data(title='All products', body='All products page')
    context['posts'] = posts
    return render_template('products_all.html', context=context)

@app.route(f"/{menu[2]['url_name']}/<int:pk>")
def product_detail(pk):
    posts = Article.query.get(pk)
    context = get_user_data(title='Detail', body='Detail page')
    context['post'] = posts
    return render_template('product_detail.html', context=context)

@app.route(f"/update/<int:id>", methods=['GET', 'POST'])
def product_update(id):
    context = get_user_data(title='Update product', body='Update product page')
    post = Article.query.get(id)
    context['post'] = post
    if request.method == 'POST':
        post.title = request.form['title']
        post.intro = request.form['intro']
        post.text = request.form['text']
        post.price = request.form['price']
        try:
            db.session.commit()
            return redirect(f"/{menu[2]['url_name']}/{id}")
        except:
            return 'Error update'

    return render_template('product_update.html', context=context)

@app.route(f"/delete/<int:id>")
def product_delete(id):
    context = get_user_data(title='Delete', body='Delete page')
    post = Article.query.get_or_404(id)
    try:
        db.session.delete(post)
        db.session.commit()
        return redirect(f"/{menu[2]['url_name']}")
    except:
        return 'Error delete'

@app.route(f"/product_buy/<int:id>")
def product_bye(id):
    post = Article.query.get(id)
    api = Api(merchant_id=1396424,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "USD",
        "amount": post.price*100
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)

@app.route(f"/{menu[3]['url_name']}")
def about():
    context = get_user_data(title='About', body='About page')
    return render_template('about.html', context=context)


# -------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
