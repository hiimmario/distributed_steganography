from PIL import Image
import os
from pathlib import Path
from random import shuffle
from keras.models import Sequential
from keras.layers import Dense, Flatten
from keras.layers import Conv2D, MaxPooling2D
import numpy as np

from time import time
from keras.callbacks import TensorBoard

tensorboard = TensorBoard(log_dir="./logs/{}".format(time()), histogram_freq=0,
                          write_graph=True, write_images=False)

# tensorboard --logdir=logs


def load_training_data(path_original, path_manipulated):
    manipulated_files = [p for p in path_manipulated.iterdir() if p.is_file()]
    original_files = [p for p in path_original.iterdir() if p.is_file()]

    train_data = []

    for idx, img in enumerate(manipulated_files):
        img = Image.open(img)
        # img = img.convert('L')
        img = img.resize((IMG_WIDTH, IMG_HEIGHT))
        train_data.append([np.array(img), np.array([1, 0])])

        # img.show()

        # if idx == 10:
        #     break

    for idx, img in enumerate(original_files):
        img = Image.open(img)
        # img = img.convert('L')
        img = img.resize((IMG_WIDTH, IMG_HEIGHT))
        train_data.append([np.array(img), np.array([0, 1])])

        # img.show()

        # if idx == 10:
        #     break

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

print("count of images/labels overall:")
print(len(trainImages))
print(len(trainLabels))

x_test = trainImages[-50:]
y_test = trainLabels[-50:]
x_train = trainImages[0:len(trainImages)-50:]
y_train = trainLabels[0:len(trainImages)-50:]

print("train images/labels:")
print(len(x_train))
print(len(y_train))

print("validation images/labels:")
print(len(x_test))
print(len(y_test))


# Convolution network
model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3), strides=(1, 1),
                 activation='relu',
                 input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)))
model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
model.add(Conv2D(64, (5, 5), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Flatten())
model.add(Dense(1000, activation='relu'))
model.add(Dense(2, activation='softmax'))

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=["acc"])

model.fit(x_train, y_train, batch_size=32, epochs=10, verbose=1, callbacks=[tensorboard])
score = model.evaluate(x_test, y_test, batch_size=32)

print(score)
