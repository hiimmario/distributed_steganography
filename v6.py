# memepack: https://archive.org/details/HugeMemePack

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

# RecursionError: maximum recursion depth exceeded while calling a Python object (~25k chars)
# source: https://stackoverflow.com/questions/22571259/split-a-string-into-n-equal-parts
def split_str(seq, chunk, skip_tail=False):
    lst = []
    if chunk <= len(seq):
        lst.extend([seq[:chunk]])
        lst.extend(split_str(seq[chunk:], chunk, skip_tail))
    elif not skip_tail and seq:
        lst.extend([seq])
    return lst


def distribution_channel(_pictures, _payload):
    payload = _payload
    pictures = _pictures
    lenpl = len(payload)
    ctnpic = len(pictures)

    if lenpl < ctnpic:
        for i in range(0, ctnpic-lenpl):
            payload = payload + id_generator()

    # todo len pic > len payload
    if lenpl > ctnpic:

        divider = lenpl/ctnpic
        print(divider)
        print(math.ceil(divider)) # WORKS
        print(split_str(payload, math.ceil(divider)))

        # todo auffüllen am ende der liste

    # without len pic > len payload implemented and lenpl > ctpic input
    # PIL.Image.DecompressionBombError: Image size (200900000 pixels) exceeds limit of 178956970 pixels, could be decompression bomb DOS attack.


    if ctnpic == lenpl:
        pass

    return pictures, payload

# start
cwd = os.getcwd()
path_source = Path(cwd + "./images")
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
    print("payload distributed")
    print("payload\t" + payload)
    print("start stenography")

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

        if verbose:
            print(str(idx) + "/" + str(len(files)))
            print("payload\t " + payload[idx])
            print("original\t " + path_original)
            print("manipulated\t " + path_manipulated)
            print("clear message\t " + clear_message + "\n")

        # only for dev
        if idx == 10:
            break

    # only for dev
    if idx == 10:
        break
