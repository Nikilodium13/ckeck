import os
import  time
import telebot
import db_tg
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Здравствуйте! Я бот для записей к врачу.\n"
        "Используйте /add чтобы записаться.\n"
        "Используйте /list чтобы посмотреть записи.\n"
        "Используйте /edit чтобы изменить время приёма."
    )

@bot.message_handler(commands=["add"])
def add_patients(message):
    bot.send_message(message.chat.id, "Имя папациента: ")
    bot.register_next_step_handler(message, add_surname)

def add_surname(message):
    name = message.text
    bot.send_message(message.chat.id, "Фамилия папациента: ")
    bot.register_next_step_handler(message, add_age, name)

def add_age(message, name):
    surname = message.text
    bot.send_message(message.chat.id, "Возраст папациента: ")
    bot.register_next_step_handler(message, add_date, name, surname)

def add_date(message, name, surname):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Возраст должен быть числом!")
        return
    age = int(message.text)
    bot.send_message(message.chat.id, "Введите дату приёма: ")
    bot.register_next_step_handler(message, save_patients, name, surname, age)

def save_patients(message, name, surname, age):
    date = message.text
    db_tg.add_patients(name, surname, age, date)
    bot.send_message(message.chat.id, "✅ Пациент записан!")

@bot.message_handler(commands=["list"])
def list_patients(message):
    patients = db_tg.get_patients()

    if not patients:
        bot.send_message(message.chat.id, "Net zapisej")
        return
    for patient_id, name, surname, age, date in patients:
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("Change date", callback_data=f"edit_{patient_id}")
        markup.add(btn)

        bot.send_message(message.chat.id, f"{patient_id}. {name} {surname}, {age}   — date: {date}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_"))
def edit_date_inline(call):
    patient_id = int(call.data.split("_")[1])
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"Введите новую дату приема для пациента ID {patient_id}:")
    bot.register_next_step_handler(call.message, save_new_date, patient_id)

def save_new_date(message, patient_id):
    new_date = message.text
    db_tg.update_date(patient_id, new_date)
    bot.send_message(message.chat.id, "✅ Дата обновлена!")

@bot.message_handler(commands=["edit"])
def edit_manual(message):
    bot.send_message(message.chat.id, "Введите ID пациента: ")
    bot.register_next_step_handler(message, edit_manual_2)

def edit_manual_2(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "ID должен быть числом!")
        return

    patient_id = int(message.text)
    bot.send_message(message.chat.id, "Введите новую дату: ")
    bot.register_next_step_handler(message, edit_manual_3, patient_id)

def edit_manual_3(message, patient_id):
    db_tg.update_date(patient_id, message.text)
    bot.send_message(message.chat.id, "✅ Дата приема обновлена!")

if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as ex:
            print("Ошибка:", ex)
            time.sleep(2)