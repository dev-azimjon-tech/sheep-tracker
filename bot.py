import telebot
from telebot import types
import datetime
import json

API_TOKEN = '7711704091:AAGxNLAn563uLGWymFvK9rkiwWQn2391p4o'
bot = telebot.TeleBot(API_TOKEN)

DATA_FILE = 'sheep_data.json'


def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []


def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=5)


user_states = {}
user_inputs = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('➕ Qo‘y qo‘shish', '📋 Qo‘ylarni ko‘rish')
    markup.add('🗑 Oxirgini o‘chirish', '📊 Statistika')
    bot.send_message(message.chat.id,
                     "🐑 Qo‘ylar nazorati botiga xush kelibsiz!\nIltimos, amalni tanlang:",
                     reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == '➕ Qo‘y qo‘shish')
def add_sheep(message):
    user_states[message.chat.id] = 'awaiting_date'
    user_inputs[message.chat.id] = {}
    bot.send_message(message.chat.id, "📅 Xarid sanasini kiriting (kun-oy-yil formatida, masalan 01-07-2025):")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_date')
def handle_date(message):
    user_inputs[message.chat.id]['date'] = message.text
    user_states[message.chat.id] = 'awaiting_price'
    bot.send_message(message.chat.id, "💰 Qo‘y narxini kiriting (masalan: 1200):")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_price')
def handle_price(message):
    user_inputs[message.chat.id]['price'] = message.text
    user_states[message.chat.id] = 'awaiting_weight'
    bot.send_message(message.chat.id, "⚖️ Qo'y vaznini kiriting (kg):")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_weight')
def handle_weight(message):
    user_inputs[message.chat.id]['weight'] = message.text
    user_states[message.chat.id] = 'awaiting_source'
    bot.send_message(message.chat.id, "📍 Sotuvchi yoki bozor nomini kiriting:")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_source')
def handle_source(message):
    user_inputs[message.chat.id]['source'] = message.text
    user_inputs[message.chat.id]['timestamp'] = str(datetime.datetime.now())

    data = load_data()
    data.append(user_inputs[message.chat.id])
    save_data(data)

    bot.send_message(message.chat.id, "✅ Qo‘y muvaffaqiyatli saqlandi!")
    user_states.pop(message.chat.id)
    user_inputs.pop(message.chat.id)


@bot.message_handler(func=lambda m: m.text == '📋 Qo‘ylarni ko‘rish')
def view_sheep(message):
    data = load_data()
    if not data:
        bot.send_message(message.chat.id, "📭 Hozircha hech qanday qo‘y yozuvi yo‘q.")
        return
    text = "📋 So‘nggi qo‘y yozuvlari:\n\n"
    for i, entry in enumerate(data[-5:], 1):
        text += f"{i}. 🗓 {entry['date']} | 💰 {entry['price']} TJS | ⚖️ {entry['weight']} kg | 📍 {entry['source']}\n"
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == '🗑 Oxirgini o‘chirish')
def delete_last(message):
    data = load_data()
    if not data:
        bot.send_message(message.chat.id, "❌ O‘chirish uchun hech qanday yozuv yo‘q.")
        return
    removed = data.pop()
    save_data(data)
    bot.send_message(
        message.chat.id,
        f"🗑 Oxirgi qo‘y yozuvi o‘chirildi:\n🗓 {removed['date']} | 💰 {removed['price']} TJS | ⚖️ {removed['weight']} kg"
    )


@bot.message_handler(func=lambda m: m.text == '📊 Statistika')
def summary(message):
    data = load_data()
    total = len(data)

    # Only include records with both price and weight
    valid_data = [item for item in data if 'price' in item and 'weight' in item]

    total_price = sum(float(item['price']) for item in valid_data)
    total_weight = sum(float(item['weight']) for item in valid_data)

    avg_price = total_price / total if total else 0
    avg_weight = total_weight / total if total else 0

    bot.send_message(
        message.chat.id,
        f"📊 Statistika:\n"
        f"🐑 Jami qo‘ylar: {total}\n"
        f"💸 Jami sarflangan: {total_price:.2f} TJS\n"
        f"⚖️ O'rtacha vazn: {avg_weight:.2f} kg\n"
        f"📈 O‘rtacha narx: {avg_price:.2f} TJS"
    )


@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(message.chat.id, "❗ Noma’lum buyruq. Iltimos, menyudan foydalaning.")

bot.polling()
