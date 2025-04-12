from flask import Flask, render_template, request, jsonify
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import base64
import datetime
from datetime import datetime as dt

# ChatterBot imports
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

app = Flask(__name__)

# ------------------------
# Datasets for Company Info and News
# ------------------------

company_dataset = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOG",
    "Amazon": "AMZN",
    "Facebook": "META"  # Facebook is now Meta Platforms.
}

news_dataset = {
    "Apple": [
        {"date": "2023-10-01", "headline": "Apple launches new iPhone with breakthrough features."},
        {"date": "2023-09-25", "headline": "Apple stock hits new high as investors remain bullish."}
    ],
    "Microsoft": [
        {"date": "2023-10-03", "headline": "Microsoft unveils major software update across Windows platforms."},
        {"date": "2023-09-20", "headline": "Microsoft partners with top tech companies for cloud expansion."}
    ],
    "Google": [
        {"date": "2023-10-02", "headline": "Google announces AI breakthrough in search algorithms."},
        {"date": "2023-09-18", "headline": "Google's latest update improves map accuracy globally."}
    ],
    "Amazon": [
        {"date": "2023-10-04", "headline": "Amazon introduces faster delivery with drone technology."},
        {"date": "2023-09-22", "headline": "Amazon's Q3 earnings exceed analyst expectations."}
    ],
    "Facebook": [
        {"date": "2023-10-01", "headline": "Meta focuses on virtual reality innovations with new headset release."},
        {"date": "2023-09-26", "headline": "Meta's ad revenue remains steady despite global market challenges."}
    ]
}

# ------------------------
# Initialize ChatterBot
# ------------------------
chatbot = ChatBot("StockAgentBot")
trainer = ListTrainer(chatbot)
conversation = [
    "Hello",
    "Hi there!",
    "How are you?",
    "I'm good, thank you!",
    "What is your name?",
    "I'm StockAgentBot, your stock and news assistant.",
    "Tell me something about the company",
    "Sure, ask me about a specific company!"
]
trainer.train(conversation)

# ------------------------
# Helper functions for Stock Chart and News
# ------------------------
def fetch_stock_chart(ticker, company_name):
    # Define time range: last 30 days
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    if stock_data.empty:
        return None

    # Create the matplotlib figure
    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor('lightyellow')
    ax.set_facecolor('floralwhite')
    ax.plot(stock_data.index, stock_data['Close'], marker='o', linestyle='-', 
            color='royalblue', linewidth=2)
    ax.set_title(f"{company_name} Stock Closing Prices", fontsize=16, fontweight='bold', color='darkblue')
    ax.set_xlabel("Date", fontsize=12, color='darkred')
    ax.set_ylabel("Closing Price (USD)", fontsize=12, color='darkred')
    ax.grid(True, linestyle='--', linewidth=0.5, color='gray')
    fig.autofmt_xdate()

    # Save the figure to a BytesIO object and encode it to base64
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    return image_base64

def get_latest_news(company_name):
    if company_name in news_dataset:
        latest = max(news_dataset[company_name],
                     key=lambda x: dt.strptime(x["date"], "%Y-%m-%d"))
        return f"{latest['date']} - {latest['headline']}"
    return None

# ------------------------
# Flask Routes
# ------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.form['message']
    response_data = {}
    company_found = None

    # Check if the message contains a company name
    for company in company_dataset.keys():
        if company.lower() in user_message.lower():
            company_found = company
            break

    chart_image = None
    news_text = None

    if company_found:
        ticker = company_dataset[company_found]
        chart_image = fetch_stock_chart(ticker, company_found)
        news_text = get_latest_news(company_found)

    # Generate response using ChatterBot
    bot_response = str(chatbot.get_response(user_message))

    response_data['bot_response'] = bot_response
    response_data['chart_image'] = chart_image
    response_data['news'] = news_text
    response_data['company'] = company_found if company_found else ""
    
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
