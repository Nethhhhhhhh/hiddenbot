import os
import sys
import telebot
from flask import Flask, request, jsonify

# Add the parent directory to sys.path so we can import bot.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the bot instance and handlers from bot.py
from bot import bot

app = Flask(__name__)

# The secret token from environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8699325575:AAHotYf2PFRS9UVZLWfQPdZXWrcpWAiSaYw")

@app.route('/', methods=['GET'])
def index():
    return "Bot is running on Vercel Serverless Function!"

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return jsonify({"error": "Invalid request"}), 400

# Vercel Serverless requires the application to be exposed
# No `app.run()` is needed since Vercel uses WSGI to serve the Flask app
