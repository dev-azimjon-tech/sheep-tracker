import telebot
from telebot import types
import datetime
import json
import re

API_TOKEN = '7711704091:AAGxNLAn563uLGWymFvK9rkiwWQn2391p4o'
bot = telebot.TeleBot(API_TOKEN)

DATA_FILE = 'sheep_data.json'


def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=5)


def validate_date(date_str):
    """Validate date in format dd-mm-yyyy"""
    pattern = r'^\d{2}-\d{2}-\d{4}$'
    if not re.match(pattern, date_str):
        return False
    try:
        day, month, year = map(int, date_str.split('-'))
        datetime.datetime(year, month, day)
        return True
    except ValueError:
        return False


def format_date(date_str):
    """Format date by adding dashes if missing. Returns formatted date or None if invalid"""
    date_str = date_str.replace('-', '')
    
    if len(date_str) == 8 and date_str.isdigit():
        formatted = f"{date_str[0:2]}-{date_str[2:4]}-{date_str[4:8]}"
        if validate_date(formatted):
            return formatted
    
    
    if validate_date(date_str):
        return date_str
    
    return None


def validate_price(price_str):
    """Validate price as a positive number"""
    try:
        price = float(price_str)
        return price > 0
    except ValueError:
        return False


def validate_weight(weight_str):
    """Validate weight as a positive number"""
    try:
        weight = float(weight_str)
        return weight > 0
    except ValueError:
        return False


def validate_text(text):
    """Validate text field (not empty and reasonable length)"""
    return text and len(text.strip()) > 0 and len(text) <= 100


user_states = {}
user_inputs = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Qo'y qo'shish", "📋 Qo'ylarni ko'rish")
    markup.add("🗑 Qo'y o'chirish", "📊 Statistika")
    bot.send_message(message.chat.id,
                     "🐑 Qo'ylar nazorati botiga xush kelibsiz!\nIltimos, amalni tanlang:",
                     reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "➕ Qo'y qo'shish")
def add_sheep(message):
    user_states[message.chat.id] = 'awaiting_name'
    user_inputs[message.chat.id] = {}
    bot.send_message(message.chat.id, "🐑 Qo'y nomini kiriting (masalan: Oqquyon, Qora qo'y):")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_name')
def handle_name(message):
    if not validate_text(message.text):
        bot.send_message(message.chat.id, "❌ Noto'g'ri kiritish! Iltimos, bo'sh bo'lmagan va 100 belgigacha matn kiriting:")
        return
    user_inputs[message.chat.id]['name'] = message.text
    user_states[message.chat.id] = 'awaiting_date'
    bot.send_message(message.chat.id, "📅 Xarid sanasini kiriting (kun-oy-yil formatida, masalan 01-07-2025):")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_date')
def handle_date(message):
    formatted_date = format_date(message.text)
    if not formatted_date:
        bot.send_message(message.chat.id, "❌ Noto'g'ri sana! Iltimos, dd-mm-yyyy formatida kiriting (masalan: 01-07-2025) yoki ddmmyyyy (masalan: 01072025):")
        return
    user_inputs[message.chat.id]['date'] = formatted_date
    user_states[message.chat.id] = 'awaiting_price'
    bot.send_message(message.chat.id, "💰 Qo'y narxini kiriting (raqam, masalan: 1200):")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_price')
def handle_price(message):
    if not validate_price(message.text):
        bot.send_message(message.chat.id, "❌ Noto'g'ri narx! Iltimos, ijobiy raqam kiriting (masalan: 1200):")
        return
    user_inputs[message.chat.id]['price'] = message.text
    user_states[message.chat.id] = 'awaiting_weight'
    bot.send_message(message.chat.id, "⚖️ Qo'y vaznini kiriting (kg, masalan: 25.5):")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_weight')
def handle_weight(message):
    if not validate_weight(message.text):
        bot.send_message(message.chat.id, "❌ Noto'g'ri vazn! Iltimos, ijobiy raqam kiriting (masalan: 25.5):")
        return
    user_inputs[message.chat.id]['weight'] = message.text
    user_states[message.chat.id] = 'awaiting_source'
    bot.send_message(message.chat.id, "📍 Sotuvchi yoki bozor nomini kiriting (100 belgigacha):")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_source')
def handle_source(message):
    if not validate_text(message.text):
        bot.send_message(message.chat.id, "❌ Noto'g'ri kiritish! Iltimos, bo'sh bo'lmagan va 100 belgigacha matn kiriting:")
        return
    user_inputs[message.chat.id]['source'] = message.text
    user_inputs[message.chat.id]['timestamp'] = str(datetime.datetime.now())

    data = load_data()
    data.append(user_inputs[message.chat.id])
    save_data(data)

    bot.send_message(message.chat.id, "✅ Qo'y muvaffaqiyatli saqlandi!")
    user_states.pop(message.chat.id)
    user_inputs.pop(message.chat.id)


@bot.message_handler(func=lambda m: m.text == "📋 Qo'ylarni ko'rish")
def view_sheep(message):
    data = load_data()
    if not data:
        bot.send_message(message.chat.id, "📭 Hozircha hech qanday qo'y yozuvi yo'q.")
        return
    text = "📋 So'nggi qo'y yozuvlari:\n\n"
    for i, entry in enumerate(data[-5:], 1):
        name = entry.get('name', 'N/A')
        date = entry.get('date', 'N/A')
        price = entry.get('price', 'N/A')
        weight = entry.get('weight', 'N/A')
        source = entry.get('source', 'N/A')
        text += f"{i}. 🐑 {name} | 🗓 {date} | 💰 {price} TJS | ⚖️ {weight} kg | 📍 {source}\n"
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "🗑 Qo'y o'chirish")
def delete_sheep(message):
    data = load_data()
    if not data:
        bot.send_message(message.chat.id, "❌ O'chirish uchun hech qanday yozuv yo'q.")
        return
    
    user_states[message.chat.id] = 'awaiting_delete_index'
    
    text = "📋 O'chirish uchun qo'y raqamini tanlang:\n\n"
    for i, entry in enumerate(data, 1):
        name = entry.get('name', 'N/A')
        date = entry.get('date', 'N/A')
        price = entry.get('price', 'N/A')
        weight = entry.get('weight', 'N/A')
        source = entry.get('source', 'N/A')
        text += f"{i}. 🐑 {name} | 🗓 {date} | 💰 {price} TJS | ⚖️ {weight} kg | 📍 {source}\n"
    
    text += "\n📝 Raqamni kiriting (1 dan {} gacha):".format(len(data))
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_delete_index')
def handle_delete_index(message):
    data = load_data()
    try:
        index = int(message.text)
        if 1 <= index <= len(data):
            removed = data.pop(index - 1)
            save_data(data)
            name = removed.get('name', 'N/A')
            date = removed.get('date', 'N/A')
            price = removed.get('price', 'N/A')
            weight = removed.get('weight', 'N/A')
            bot.send_message(
                message.chat.id,
                f"✅ Qo'y muvaffaqiyatli o'chirildi:\n🐑 {name} | 🗓 {date} | 💰 {price} TJS | ⚖️ {weight} kg"
            )
        else:
            bot.send_message(message.chat.id, f"❌ Noto'g'ri raqam! Iltimos, 1 dan {len(data)} gacha raqam kiriting:")
            return
    except ValueError:
        bot.send_message(message.chat.id, "❌ Iltimos, raqam kiriting!")
        return
    
    user_states.pop(message.chat.id)


@bot.message_handler(func=lambda m: m.text == '📊 Statistika')
def summary(message):
    data = load_data()
    total = len(data)

    valid_data = [item for item in data if 'price' in item and 'weight' in item]

    total_price = sum(float(item['price']) for item in valid_data)
    total_weight = sum(float(item['weight']) for item in valid_data)

    valid_count = len(valid_data)
    avg_price = total_price / valid_count if valid_count else 0
    avg_weight = total_weight / valid_count if valid_count else 0

    bot.send_message(
        message.chat.id,
        f"📊 Statistika:\n"
        f"🐑 Jami qo'ylar: {total}\n"
        f"💸 Jami sarflangan: {total_price:.2f} TJS\n"
        f"⚖️ O'rtacha vazn: {avg_weight:.2f} kg\n"
        f"📈 O'rtacha narx: {avg_price:.2f} TJS"
    )


@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(message.chat.id, "❗ Noma'lum buyruq. Iltimos, menyudan foydalaning.")

if __name__ == '__main__':
    try:
        print("before call to IP")
        bot.delete_webhook()
        bot.infinity_polling()
        print("after call to IP")
    except (KeyboardInterrupt, SystemExit):
        pass
