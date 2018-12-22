# memepack: https://archive.org/details/HugeMemePack

from stegano import lsb
from pathlib import Path
import os
import shutil

import string
import random


def id_generator(size=1, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return "".join(random.choice(chars) for _ in range(size))


def distribution_channel(_pictures, _payload):
    payload = _payload
    pictures = _pictures

    if len(payload) < len(pictures):
        payload = payload + "#"
        for i in range(0, len(pictures)-len(payload)-1):
            payload = payload + id_generator()

    # TODO
    # if len(_pictures) > len(_payload):
    # aufteilen

    if len(_pictures) == len(_payload):
        pass

    return pictures, payload

# START
cwd = os.getcwd()
path_source = Path(cwd + "./images")
payload = "payload"
verbose = True

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

# process files
for idx, p in enumerate(files):
    with p.open() as file:
        path_original = file.name
        path_manipulated = "./manipulated/"
        path_manipulated = path_manipulated + str(idx) + ".png"
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

    if idx == 10:
        break
