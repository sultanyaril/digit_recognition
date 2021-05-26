from scipy.io.wavfile import read
from IPython.display import Audio, display

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

import numpy as np
import librosa
import os

dataset = "dataset/splitted/"
num_labels = 10

labels = []
audios = []
for label in range(num_labels):
    label_path = f"{dataset}/{label}"
    for file in sorted(os.listdir(label_path)):
        file_path = label_path + "/" + file
        sample_rate, audio = read(file_path)
        labels.append(label)
        audios.append(audio)

max_duration_sec = 0.6
max_duration = round(max_duration_sec * sample_rate)

features = []
features_flatten = []
labels_flatten = []
for audio, label in zip(audios, labels):
    if len(audio) < max_duration:
        audio = np.pad(audio, (0, max_duration - len(audio)), constant_values=0)
    if len(audio) > max_duration:
        continue
    # audio := (audio - mean) / std
    feature = librosa.feature.melspectrogram(audio.astype(float), sample_rate, n_mels=16, fmax=1000)
    # feature := amplitude_to_db(feature)
    features.append(feature)
    features_flatten.append(feature.reshape(-1))
    labels_flatten.append(label)

features_train, features_test, labels_train, labels_test = train_test_split(features_flatten, labels_flatten, random_state=1755)

model = RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1)
model = MLPClassifier(hidden_layer_sizes=(100, 75, 50), )
model.fit(X=features_train, y=labels_train)

import pickle

with open("models/model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("models/model.pkl", "rb") as f:
    model = pickle.load(f)

labels_train_predicted = model.predict(X=features_train)
print((labels_train_predicted == labels_train).mean())

labels_test_predicted = model.predict(X=features_test)
print((labels_test_predicted == labels_test).mean())
print(labels_test)
print(labels_test_predicted.tolist())
