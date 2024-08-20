import dash
from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import os

# Flask часть
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Указание абсолютного пути к базе данных
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'instance', 'users.db')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                            'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Создание данных для графиков
data = {
    "Fruit": ["Apples", "Bananas", "Oranges", "Tomatoes",
            "Apples", "Bananas", "Oranges", "Tomatoes",
            "Apples", "Bananas", "Oranges", "Tomatoes",
            "Apples", "Bananas", "Oranges", "Tomatoes"],
    "Price per kg (RUB)": [125, 136, 160, 303,
                        110, 120, 150, 280,
                        115, 130, 155, 290,
                        135, 140, 170, 315],
    "City": ["Moscow", "Moscow", "Moscow", "Moscow",
            "Krasnodar", "Krasnodar", "Krasnodar", "Krasnodar",
            "Ufa", "Ufa", "Ufa", "Ufa",
            "Irkutsk", "Irkutsk", "Irkutsk", "Irkutsk"]
}

df = pd.DataFrame(data)

# Подготовка данных для 3D графика
fruit_types = df['Fruit'].unique()
cities = df['City'].unique()

# Создание сетки для 3D графика
z_data = np.zeros((len(fruit_types), len(cities)))

for i, fruit in enumerate(fruit_types):
    for j, city in enumerate(cities):
        z_data[i, j] = df[(df['City'] == city) & (df['Fruit'] == fruit)]['Price per kg (RUB)'].values[0]

# Создание 3D поверхности
fig_3d = go.Figure(data=[go.Surface(z=z_data, x=np.arange(len(cities)), 
                                    y=np.arange(len(fruit_types)),
                                    colorscale='Viridis')])

fig_3d.update_layout(title='3D модель цен на фрукты в городах России (Август 2024)',
                    autosize=False,
                    width=800, height=800,
                    margin=dict(l=65, r=50, b=65, t=90),
                    scene=dict(
                        xaxis=dict(title='Города', tickvals=np.arange(len(cities)), ticktext=cities),
                        yaxis=dict(title='Фрукты', tickvals=np.arange(len(fruit_types)), ticktext=fruit_types),
                        zaxis_title='Цена (RUB)',
                    ))

# Создание столбчатого графика с использованием Plotly Express
fig_bar = px.bar(df, x="Fruit", y="Price per kg (RUB)", color="City", barmode="group",
                title="Цены на фрукты в разных городах России (Август 2024)")

# Dash часть
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash/')
dash_app.layout = html.Div(children=[
    html.Img(src='/static/AI_USM_AppIcon_circle (1).png', style={'width': '150px'}),
    html.H1(children='AI USM разработал: Анализ цен на фрукты в городах России с использованием 3D моделей и интерактивных графиков'),

    dcc.Tabs([
        dcc.Tab(label='Столбчатый График', children=[
            dcc.Graph(
                id='bar-price-graph',
                figure=fig_bar
            )
        ]),
        dcc.Tab(label='3D Модель', children=[
            dcc.Graph(
                id='3d-price-graph',
                figure=fig_3d
            )
        ])
    ])
])

# Объявление объекта server
server = app

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
