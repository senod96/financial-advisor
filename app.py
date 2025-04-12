import tkinter as tk
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from datetime import datetime as dt

# ChatterBot imports
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

# ------------------------
# Datasets for Company and News
# ------------------------

# Company dataset: mapping company names to ticker symbols.
company_dataset = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOG",
    "Amazon": "AMZN",
    "Facebook": "META"  # Facebook is now Meta Platforms.
}

# News dataset: mapping company names to news items.
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
# Chatbot Class with ChatterBot Integration
# ------------------------
class StockAgentChatbotChatterBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Agent Chatbot with ChatterBot")
        self.root.configure(bg='lightblue')
        
        # Initialize the ChatterBot and train it with a basic conversation.
        self.chatbot = ChatBot("StockAgentBot")
        self.trainer = ListTrainer(self.chatbot)
        
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
        self.trainer.train(conversation)
        # Note: To train with PDF content, you can extract the text using a PDF library (e.g., PyPDF2)
        # and feed the resulting text into the trainer.
        
        self.create_widgets()
    
    def create_widgets(self):
        # Create chat frame with a scrollbar.
        self.chat_frame = tk.Frame(self.root, bg='lightblue')
        self.chat_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.chat_display = tk.Text(self.chat_frame, height=15, width=60, wrap='word',
                                     bg='white', fg='black', font=("Helvetica", 12))
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.chat_scrollbar = tk.Scrollbar(self.chat_frame, orient="vertical", command=self.chat_display.yview)
        self.chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_display.config(yscrollcommand=self.chat_scrollbar.set)
        
        # Entry widget for user input.
        self.user_input = tk.Entry(self.root, width=45, font=("Helvetica", 12))
        self.user_input.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.user_input.bind("<Return>", self.handle_enter)
        
        # Send button.
        self.send_button = tk.Button(self.root, text="Send", command=self.handle_send,
                                     font=("Helvetica", 12), bg='darkblue', fg='white')
        self.send_button.grid(row=1, column=1, padx=10, pady=10, sticky="e")
        
        # Frame to hold the stock chart and news.
        self.graph_frame = tk.Frame(self.root, bg='lightblue')
        self.graph_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
    
    def handle_enter(self, event):
        self.handle_send()
    
    def handle_send(self):
        user_text = self.user_input.get().strip()
        if user_text == "":
            return
        
        self.append_chat("User: " + user_text)
        
        # Check if the query mentions a company.
        company_found = None
        for company in company_dataset.keys():
            if company.lower() in user_text.lower():
                company_found = company
                break
        
        if company_found:
            ticker = company_dataset[company_found]
            self.append_chat(f"Bot: Fetching stock data for {company_found} ({ticker})...")
            self.fetch_and_display_stock(ticker, company_found)
        
        # Generate response using ChatterBot.
        bot_response = str(self.chatbot.get_response(user_text))
        self.append_chat("Bot: " + bot_response)
        
        self.user_input.delete(0, tk.END)
    
    def append_chat(self, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
    
    def fetch_and_display_stock(self, ticker, company_name):
        # Define a time range (last 30 days).
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=30)
        try:
            stock_data = yf.download(ticker, start=start_date, end=end_date)
            if stock_data.empty:
                self.append_chat("Bot: No stock data found for " + company_name + ".")
                return
            self.plot_stock_data(stock_data, company_name)
            self.append_chat("Bot: Displaying stock graph and latest news for " + company_name + ".")
        except Exception as e:
            self.append_chat("Bot: Error retrieving stock data: " + str(e))
    
    def get_latest_news(self, company_name):
        if company_name in news_dataset:
            latest = max(news_dataset[company_name],
                         key=lambda x: dt.strptime(x["date"], "%Y-%m-%d"))
            return f"{latest['date']} - {latest['headline']}"
        return None

    def plot_stock_data(self, stock_data, company_name):
        # Clear previous graph/news from the display frame.
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        # Create a styled matplotlib figure.
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
        
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        
        # Display the latest news.
        latest_news = self.get_latest_news(company_name)
        if latest_news:
            news_label = tk.Label(self.graph_frame, text="Latest News: " + latest_news,
                                  bg='lightblue', fg='darkgreen',
                                  font=("Helvetica", 12, "italic"),
                                  wraplength=500, justify="left")
            news_label.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = StockAgentChatbotChatterBot(root)
    root.mainloop()
