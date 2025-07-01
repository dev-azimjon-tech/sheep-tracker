import telebot
from telebot import types
import datetime
import json

API_TOKEN = '7711704091:AAGxNLAn563uLGWymFvK9rkiwWQn2391p4o'
bot = telebot.TeleBot(API_TOKEN)

DATA_FILE = 'sheep_data.json'


# Load data from file
def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []


# Save data to file
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)


user_states = {}
user_inputs = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('➕ Add Sheep', '📋 View Sheep')
    markup.add('🗑 Delete Last', '📊 Summary')
    bot.send_message(message.chat.id,
                     "🐑 Welcome to Sheep Tracker Bot!\nChoose an action:",
                     reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == '➕ Add Sheep')
def add_sheep(message):
    user_states[message.chat.id] = 'awaiting_date'
    user_inputs[message.chat.id] = {}
    bot.send_message(message.chat.id, "📅 Enter purchase date (DD-MM-YYYY):")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_date')
def handle_date(message):
    user_inputs[message.chat.id]['date'] = message.text
    user_states[message.chat.id] = 'awaiting_price'
    bot.send_message(message.chat.id, "💰 Enter sheep price (e.g. 1200):")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_price')
def handle_price(message):
    user_inputs[message.chat.id]['price'] = message.text
    user_states[message.chat.id] = 'awaiting_source'
    bot.send_message(message.chat.id, "📍 Enter seller or market name:")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_source')
def handle_source(message):
    user_inputs[message.chat.id]['source'] = message.text
    user_inputs[message.chat.id]['timestamp'] = str(datetime.datetime.now())

    data = load_data()
    data.append(user_inputs[message.chat.id])
    save_data(data)

    bot.send_message(message.chat.id, "✅ Sheep saved successfully!")
    user_states.pop(message.chat.id)
    user_inputs.pop(message.chat.id)


@bot.message_handler(func=lambda m: m.text == '📋 View Sheep')
def view_sheep(message):
    data = load_data()
    if not data:
        bot.send_message(message.chat.id, "No sheep recorded yet.")
        return
    text = "📋 Latest Sheep Entries:\n\n"
    for i, entry in enumerate(data[-5:], 1):
        text += f"{i}. 🗓 {entry['date']} | 💰 {entry['price']} | 📍 {entry['source']}\n"
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == '🗑 Delete Last')
def delete_last(message):
    data = load_data()
    if not data:
        bot.send_message(message.chat.id, "❌ No entries to delete.")
        return
    removed = data.pop()
    save_data(data)
    bot.send_message(message.chat.id, f"❌ Deleted last sheep: {removed['date']} | {removed['price']} TJS")


@bot.message_handler(func=lambda m: m.text == '📊 Summary')
def summary(message):
    data = load_data()
    total = len(data)
    total_price = sum(float(item['price']) for item in data)
    avg_price = total_price / total if total else 0
    bot.send_message(
        message.chat.id,
        f"📊 Summary:\nTotal Sheep: {total}\nTotal Spent: {total_price:.2f} TJS\nAvg Price: {avg_price:.2f} TJS"
    )


@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(message.chat.id, "❗ Unknown command. Please use the menu.")

bot.polling()
