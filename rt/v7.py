from stegano import lsb
from pathlib import Path
import os
import shutil
import math
import string
import random


# source: https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
def id_generator(size=1, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return "".join(random.choice(chars) for _ in range(size))


# https://stackoverflow.com/questions/22571259/split-a-string-into-n-equal-parts
def split_str(seq, chunk):
    return [seq[i:i + chunk] for i in range(0, len(seq), chunk)]


def distribution_channel(_pictures, _payload):
    payload = _payload
    pictures = _pictures
    lenpl = len(payload)
    ctnpic = len(pictures)

    if lenpl < ctnpic:
        if verbose:
            print("payload gets padded")
        payload = payload + id_generator(ctnpic-lenpl)

    if lenpl > ctnpic:
        divider = lenpl/ctnpic
        ceiled_divider = math.ceil(divider)
        plsplit = split_str(payload, ceiled_divider)
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

    return pictures, payload


# start

path_source = Path("./originals")

# todo binary data encoding https://stackoverflow.com/questions/4911440/filess-binary-data-stored-as-variable-inside-python-file

payload = open("payload.txt", "r").read()
verbose = True
filetype = ".png"

# forced overwrite of destination folder
directory_manipulated = "./manipulated"
if os.path.exists(directory_manipulated):
    shutil.rmtree(directory_manipulated)
os.makedirs(directory_manipulated)

# loop all files
files = [p for p in path_source.iterdir() if p.is_file()]

# distribute payload on files
files, payload = distribution_channel(files, payload)

if verbose:
    print("count chunks payload:\t" + str(len(payload)))
    print("count files:\t" + str(len(files)))
    print("fully sepperated payload:")
    print(payload)
    print("starting stenography\n")

concat_clear_message = ""


# process files
for idx, p in enumerate(files):
    with p.open() as file:
        path_original = file.name
        path_manipulated = "./manipulated/"
        path_manipulated = path_manipulated + str(idx) + filetype
        pl = payload[idx]
        secret = lsb.hide(path_original, pl)
        secret.save(path_manipulated)
        clear_message = lsb.reveal(path_manipulated)

        concat_clear_message += clear_message

        if verbose:
            print(str(idx + 1) + "/" + str(len(files)))
            print("payload\t " + payload[idx])
            print("original\t " + path_original)
            print("manipulated\t " + path_manipulated)
            print("clear message\t " + clear_message + "\n")

        # if idx == 1:
        #     break

    # if idx == 1:
    #     break

print(concat_clear_message)
