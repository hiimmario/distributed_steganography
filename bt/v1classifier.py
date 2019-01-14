from keras.layers import Input, Dense, Conv2D, MaxPooling2D, UpSampling2D
from keras.models import Model
import shutil
from PIL import Image
import os
from pathlib import Path
from random import shuffle
from keras.layers import Conv2D, MaxPooling2D
import numpy as np
from PIL import ImageFile

Image.MAX_IMAGE_PIXELS = 1000000000
ImageFile.LOAD_TRUNCATED_IMAGES = True

def get_image_size_statistics(dir):
    heights = []
    widths = []
    img_count = 0

    files = [p for p in dir.iterdir() if p.is_file()]

    for idx, p in enumerate(files):
        with p.open() as file:
            data = np.array(Image.open(file.name))
            heights.append(data.shape[0])
            widths.append(data.shape[1])
            img_count += 1

    avg_height = sum(heights) / len(heights)
    avg_width = sum(widths) / len(widths)
    print("Average Height: " + str(avg_height))
    print("Max Height: " + str(max(heights)))
    print("Min Height: " + str(min(heights)))
    print("Average Width: " + str(avg_width))
    print("Max Width: " + str(max(widths)))
    print("Min Width: " + str(min(widths)))
    print("Count: " + str(img_count))


def load_training_data(path_original, path_manipulated):

    manipulated_files = [p for p in path_manipulated.iterdir() if p.is_file()]
    original_files = [p for p in path_original.iterdir() if p.is_file()]

    train_data = []

    for idx, img in enumerate(manipulated_files):
        img = Image.open(img)
        img = img.convert('L')
        img = img.resize((IMG_SIZE, IMG_SIZE), Image.ANTIALIAS)
        train_data.append([np.array(img), np.array([1, 0])])

        # plt.imshow(img)
        # plt.show()

    for idx, img in enumerate(original_files):
        img = Image.open(img)
        img = img.convert('L')
        img = img.resize((IMG_SIZE, IMG_SIZE), Image.ANTIALIAS)
        train_data.append([np.array(img), np.array([0, 1])])

        # plt.imshow(img)
        # plt.show()

    shuffle(train_data)

    return train_data


# move images from rt to proper bt folder for cwd usage
def move_images():
    target_directory_original = "./data/originals"
    target_directory_manipulated = "./data/manipulated"

    source_directory_original = "../rt/originals"
    source_directory_manipulated = "../rt/manipulated"

    if os.path.exists(target_directory_manipulated):
        shutil.rmtree(target_directory_manipulated)

    if os.path.exists(target_directory_original):
        shutil.rmtree(target_directory_original)

    shutil.copytree(source_directory_original, target_directory_original)
    shutil.copytree(source_directory_manipulated, target_directory_manipulated)


# move images from rt to bt folder forced overwrite!
# move_images()

IMG_SIZE = 300
# get image size statistics manipulated
cwd = os.getcwd()
path_source_originals = Path(cwd + "/data/originals")
path_source_manipulated = Path(cwd + "/data/manipulated")

# originals == manipulated
#print("size statistics images:")
#get_image_size_statistics(path_source_originals)

# prepare container for keras
training_data = load_training_data(path_source_originals, path_source_manipulated)

# print(training_data)

trainImages = np.array([i[0] for i in training_data]).reshape(-1, IMG_SIZE, IMG_SIZE, 1)
trainLabels = np.array([i[1] for i in training_data])

validationImages = trainImages[:]
input_shape = (IMG_SIZE, IMG_SIZE, 1)

print("count of images/labels overall:")
print(len(trainImages))
print(len(trainLabels))


x_test = trainImages[-250:]
y_test = trainLabels[-250:]
x_train = trainImages[0:len(trainImages)-250:]
y_train = trainLabels[0:len(trainImages)-250:]

print("train images/labels:")
print(len(x_train))
print(len(y_train))

print("validation images/labels:")
print(len(x_test))
print(len(y_test))

input_img = Input(shape=(IMG_SIZE, IMG_SIZE, 1))  # adapt this if using `channels_first` image data format

x = Conv2D(16, (3, 3), activation='relu', padding='same')(input_img)
x = MaxPooling2D((2, 2), padding='same')(x)
x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
x = MaxPooling2D((2, 2), padding='same')(x)
x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
encoded = MaxPooling2D((2, 2), padding='same')(x)

# at this point the representation is (4, 4, 8) i.e. 128-dimensional

x = Conv2D(8, (3, 3), activation='relu', padding='same')(encoded)
x = UpSampling2D((2, 2))(x)
x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
x = UpSampling2D((2, 2))(x)
x = Conv2D(16, (3, 3), activation='relu')(x)
x = UpSampling2D((2, 2))(x)
decoded = Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x)

model = Model(input_img, decoded)
model.compile(optimizer='adadelta', loss='binary_crossentropy')

model.fit(x_train, y_train, batch_size=32, epochs=200, verbose=1)
score = model.evaluate(x_test, y_test, batch_size=32)

print(score)