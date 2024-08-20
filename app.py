import os
import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Шаг 1: Создание DataFrame с данными о ценах на фрукты
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

# Шаг 2: Подготовка данных для 3D графика
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

# Создание Dash-приложения для визуализации данных
app = dash.Dash(__name__)

# Определение макета приложения
app.layout = html.Div(children=[
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

# Добавляем эту строку для работы с gunicorn
server = app.server

# Указание на использование порта, который задает Heroku
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run_server(host='0.0.0.0', port=port)
