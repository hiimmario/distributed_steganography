# memepack: https://archive.org/details/HugeMemePack

from stegano import lsb
from pathlib import Path
import os
import shutil

import string
import random


def id_generator(size=6, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))


cwd = os.getcwd()
path_source = Path(cwd + "./images")

payload = "# payload"
verbose = True

directory_manipulated = "./manipulated"
if os.path.exists(directory_manipulated):
    shutil.rmtree(directory_manipulated)
os.makedirs(directory_manipulated)

files = [p for p in path_source.iterdir() if p.is_file()]

for idx, p in enumerate(files):
    with p.open() as file:
        path_original = file.name
        path_manipulated = "./manipulated/"
        path_manipulated = path_manipulated + str(idx) + ".png"
        print(path_manipulated)
        payload = str(idx) + "#" + id_generator(20)
        secret = lsb.hide(path_original, payload)
        secret.save(path_manipulated)
        clear_message = lsb.reveal(path_manipulated)

        if verbose:
            print("original\t " + path_original)
            print("manipulated\t " + path_manipulated)
            print("clear message\t " + clear_message + "\n")
