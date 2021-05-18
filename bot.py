import telebot     # run telegram bot
from datetime import datetime # generate log
import random
import os.path

text_of_numbers = ["ноль", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"]

with open("creds.txt", "r") as f:
    audio_digits_dataset_creds = f.read().strip() # "  hello world \t\n" -> "hello world"
bot = telebot.TeleBot(audio_digits_dataset_creds)
print(audio_digits_dataset_creds)
numbers = {}

def log(text):
    time_stamp = datetime.now().strftime("%Y.%m.%d-%H:%M:%S")
    print(time_stamp + ' ' + text)

def generate_numbers():
    result = ""
    for i in range(5):
        result += str(random.randint(0, 9)) + ' '
    return result

def generate_prompt(user_name):
    global numbers
    numbers[user_name] = generate_numbers()
    number_text = ""
    for i in numbers[user_name].strip().split(' '):
        number_text += text_of_numbers[int(i)] + ' '
    return "Пожалуйста, прочтите следующие 5 цифр, разделяя их паузой в 1 секунду\n" + number_text + "\n"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.username
    log_text = "User ({0}): {1}".format(user_name, message.text)
    log(log_text)
    
    bot.send_message(message.from_user.id, generate_prompt(user_name))

@bot.message_handler()
def get_text_message(message):
    user_name = message.from_user.username
    log_text = "User ({0}): {1}".format(user_name, message.text)
    log(log_text)
 
    bot.send_message(message.from_user.id, "Запишите аудио")

@bot.message_handler(content_types=['voice'])
def get_voice_message(message):
    user_name = message.from_user.username
    log_text = "User ({0}): {1}".format(user_name, str(message.voice))
    log(log_text)

    tele_file = bot.get_file(message.voice.file_id)
    ogg_data = bot.download_file(tele_file.file_path)
    global numbers
    file_name = "data/" + numbers[user_name].strip().replace(' ', '_') + ".ogg"
    while os.path.exists(file_name):
        file_name = file_name[:-4] + "_1" + ".ogg"
    with open(file_name, "wb") as f:
        f.write(ogg_data)
    print("FILE SAVED: ", file_name)

    bot.send_message(message.from_user.id, generate_prompt(user_name))

bot.polling()


