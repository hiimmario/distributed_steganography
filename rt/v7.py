from stegano import lsb
from pathlib import Path
import os
import shutil
import math
import string
import random
from PIL import Image
Image.MAX_IMAGE_PIXELS = 1000000000


def id_generator(size=1, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return "".join(random.choice(chars) for _ in range(size))

def distribution_channel(ctnpic, payload, distribute):
    lenpl = len(payload)

    if not distribute:
        return [payload] * ctnpic

    if lenpl < ctnpic:
        if verbose:
            print("payload gets padded")
        payload = payload + id_generator(ctnpic-lenpl)

    if lenpl > ctnpic:
        divider = lenpl/ctnpic
        ceiled_divider = math.ceil(divider)
        plsplit = [payload[i:i + ceiled_divider] for i in range(0, len(payload), ceiled_divider)]
        last_element = plsplit[-1]
        filler = id_generator(ceiled_divider - len(last_element))
        fullend = last_element + filler
        plsplit[-1] = fullend
        payload = plsplit

        if verbose:
            print("payload gets distributed")
            print("divider:\t" + str(divider))
            print("rounded_divider:\t" + str(ceiled_divider))
            print("last_element:\t" + str(last_element))
            print("len last element:\t" + str(len(last_element)))
            print("filler:\t" + str(filler))
            print("len filler:\t" + str(len(filler)))
            print("fullend:\t" + str(fullend))
            print("len payload chunks:\t" + str(len(payload[0])))

    if ctnpic == lenpl:
        if verbose:
            print("wow")

    return payload


# start
payload = open("payload.txt", "r").read()
verbose = True
file_type = ".png"

original_images_path = Path("./originals")
manipulated_images_path = "./training_data/manipulated/"
resized_gray_originals_path = "./training_data/originals/"

# forced overwrite
if os.path.exists(manipulated_images_path):
    shutil.rmtree(manipulated_images_path)
os.makedirs(manipulated_images_path)

if os.path.exists(resized_gray_originals_path):
    shutil.rmtree(resized_gray_originals_path)
os.makedirs(resized_gray_originals_path)

# loop all files IMPORTANT only pictures in directory

original_images = [Image.open(p) for p in Path(original_images_path).iterdir() if p.is_file()]

# TODO alle original_images nach trainingdata originals resized und grayscale speichern
for idx, image in enumerate(original_images):
    # make the picture grayscale but save it as rgb for steghide
    image = image.resize((200, 100), Image.ANTIALIAS).convert("LA").convert("RGB")
    image.save(resized_gray_originals_path + str(idx) + file_type)

original_images_paths = [p for p in Path(resized_gray_originals_path).iterdir() if p.is_file()]

# distribute payload on files
payload = distribution_channel(len(original_images_paths), payload, False)

if verbose:
    print("count chunks payload:\t" + str(len(payload)))
    print("count files:\t" + str(len(original_images_paths)))
    print("fully sepperated payload:")
    print(payload)
    print("starting steganography\n")

concat_clear_message = ""

# process files
for idx, p in enumerate(original_images_paths):
    with p.open() as file:
        original_image_name = file.name
        manipulated_image_path = manipulated_images_path + str(idx) + file_type
        pl = payload[idx]
        secret = lsb.hide(original_image_name, pl)
        secret.save(manipulated_image_path)
        clear_message = lsb.reveal(manipulated_image_path)
        concat_clear_message += clear_message

        if verbose:
            print(str(idx + 1) + "/" + str(len(original_images_paths)))
            print("payload\t " + payload[idx])
            print("original\t " + original_image_name)
            print("manipulated\t " + manipulated_image_path)
            print("clear message\t " + clear_message + "\n")

print(concat_clear_message)
