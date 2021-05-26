import telebot     # run telegram bot
from datetime import datetime # generate log
import os.path
import subprocess
import pickle
from scipy.io.wavfile import read
import numpy as np
from vad import get_vad_segments
from vad import get_max_duration
from vad import sec2samples
import librosa
welcome_letter = "Здравствуйте, запишите аудио, произнося числа и разделяя их небольшой паузой\n"

with open("creds2.txt", "r") as f:
    audio_digits_dataset_creds = f.read().strip() # "  hello world \t\n" -> "hello world"
bot = telebot.TeleBot(audio_digits_dataset_creds)
print(audio_digits_dataset_creds)
numbers = {}

def log(text):
    time_stamp = datetime.now().strftime("%Y.%m.%d-%H:%M:%S")
    print(time_stamp + ' ' + text)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    log_text = "User ({0}): {1}".format(user_name, message.text)
    log(log_text)
    bot.send_message(message.from_user.id, welcome_letter)   

@bot.message_handler()
def get_text_message(message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    log_text = "User ({0}): {1}".format(user_name, message.text)
    log(log_text)
    bot.send_message(message.from_user.id, "Запишите аудио")

@bot.message_handler(content_types=['voice'])
def get_voice_message(message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    log_text = "User ({0}): {1}".format(user_name, str(message.voice))
    log(log_text)
    tele_file = bot.get_file(message.voice.file_id)
    ogg_data = bot.download_file(tele_file.file_path)
    file_name = "dataset/tmp/" + str(user_id) + ".ogg"
    with open(file_name, "wb") as f:
        f.write(ogg_data)
    print("FILE SAVED: ", file_name)
    
    subprocess.call(["ffmpeg", "-n", "-i", file_name, "dataset/tmp/" + str(user_id) + '.wav'])
    subprocess.call(["rm", file_name])
    wav_file_path = "dataset/tmp/" + str(user_id) + '.wav'

    sample_rate, audio = read(wav_file_path)
    
    segments = get_vad_segments(audio, sample_rate, 0.1, 0.02)
    
    audios = []
    segment_hop_samples = sec2samples(0.1, sample_rate)
    for segment in segments:
        start_samples = segment.start * segment_hop_samples
        stop_samples = segment.stop * segment_hop_samples
        audios.append(audio[start_samples:stop_samples])

    max_duration_sec = get_max_duration(segments, sample_rate, 0.1)
    if max_duration_sec > 0.6:
        bot.send_message(message.from_user.id, "Мыши перегрызли провод, по которому шел ваш сигнал. Повторите еще раз")
        subprocess.call(["rm", wav_file_path])
        return

    with open("models/model.pkl", "rb") as f:
        model = pickle.load(f)
    features_flatten = []
    max_duration = round(0.6 * sample_rate)
    for audio in audios:
        audio = np.pad(audio, (0, max_duration - len(audio)), constant_values=0)
        # audio := (audio - mean) / std
        feature = librosa.feature.melspectrogram(audio.astype(float), sample_rate, n_mels=16, fmax=1000)
        # feature := amplitude_to_db(feature)
        features_flatten.append(feature.reshape(-1))

    labels_test_predicted = model.predict(X=features_flatten)
    prediction_string = ""
    for i in labels_test_predicted.tolist():
        prediction_string += str(i) + ' '
    
    bot.send_message(message.from_user.id, prediction_string)
    subprocess.call(["rm", wav_file_path])

bot.polling()


