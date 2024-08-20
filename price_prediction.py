import os
import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
from transformers import pipeline
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# Initialize the sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

# Sample news data (replace with real news data in production)
news_data = [
    "Inflation in Russia is expected to rise due to increased fuel prices.",
    "The government announced a subsidy for farmers, which may lower fruit prices.",
    "Economic downturn may lead to higher prices in the coming months."
]

# Analyze sentiment of each news article
sentiment_scores = [sentiment_pipeline(news)[0]['score'] for news in news_data]

# Sample historical price data (replace with real data)
historical_data = {
    "Date": pd.date_range(start="2024-01-01", periods=len(sentiment_scores), freq='M'),
    "Price": [150, 155, 160],  # Example prices
    "Sentiment": sentiment_scores
}

df = pd.DataFrame(historical_data)

# Split data into training and test sets
X = df[['Sentiment']]
y = df['Price']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a simple linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Predict future prices
df['Predicted Price'] = model.predict(X)

# Create a Dash app for visualizing the data
app = dash.Dash(__name__)

fig = px.line(df, x='Date', y=['Price', 'Predicted Price'], title="Price Prediction Over Time")

app.layout = html.Div([
    html.H1("Price Prediction Dashboard"),
    dcc.Graph(id='price-graph', figure=fig)
])

# Add server for deployment
server = app.server

# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run_server(host='0.0.0.0', port=port)
