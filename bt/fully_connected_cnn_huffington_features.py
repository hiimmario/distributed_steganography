from PIL import Image
import os
from pathlib import Path
from random import shuffle
from keras.models import Sequential
from keras.layers import Dense
import numpy as np
from keras.layers import Activation
from keras.optimizers import SGD

from time import time
from keras.callbacks import TensorBoard

tensorboard = TensorBoard(log_dir="./logs/{}".format(time()), histogram_freq=0,
                          write_graph=True, write_images=False)

# tensorboard --logdir=logs

# extracting first feature set of huffington encoding for pixel values
def load_training_data(path_original, path_manipulated):
    manipulated_files = [p for p in path_manipulated.iterdir() if p.is_file()]
    original_files = [p for p in path_original.iterdir() if p.is_file()]

    train_data = []

    print("stego images:")

    for idx, img in enumerate(manipulated_files):
        img = Image.open(img)
        # img = img.convert('L')
        img = img.resize((IMG_WIDTH, IMG_HEIGHT))

        img_list = np.array(img).ravel().tolist()
        input = []

        for i in range(0, 256):
            input.append(img_list.count(i))

        train_data.append([input, np.array([1, 0])])

        print(idx)

    print("originals:")

    for idx, img in enumerate(original_files):
        img = Image.open(img)
        # img = img.convert('L')
        img = img.resize((IMG_WIDTH, IMG_HEIGHT))
        img_list = np.array(img).ravel().tolist()
        input = []

        for i in range(0, 256):
            input.append(img_list.count(i))

        train_data.append([input, np.array([0, 1])])

        print(idx)


    shuffle(train_data)

    return train_data

IMG_WIDTH = 400
IMG_HEIGHT = 200

cwd = os.getcwd()
path_source_originals = Path("../rt/training_data/cover_lsb_extracted")
path_source_manipulated = Path("../rt/training_data/stego_lsb_extracted")

# prepare container for keras
training_data = load_training_data(path_source_originals, path_source_manipulated)

# print(training_data)

trainImages = np.array([i[0] for i in training_data])
trainLabels = np.array([i[1] for i in training_data])

x_test = trainImages[-50:]
y_test = trainLabels[-50:]
x_train = trainImages[0:len(trainImages)-50:]
y_train = trainLabels[0:len(trainImages)-50:]

model = Sequential()
model.add(Dense(600, input_dim=256, activation="relu"))
# model.add(Dense(6000, activation="relu"))
model.add(Dense(2, activation="sigmoid"))

model.compile(loss="binary_crossentropy", optimizer='adam', metrics=["accuracy"])

print(model.summary())

model.fit(x_train, y_train, epochs=50, batch_size=16, verbose=1, callbacks=[tensorboard])

score = model.evaluate(x_test, y_test, batch_size=16)

print(score)
