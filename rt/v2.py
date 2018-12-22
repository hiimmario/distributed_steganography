# https://archive.org/details/HugeMemePack
# works
from stegano import lsb
from pathlib import Path
import os
import shutil

cwd = os.getcwd()
directory_source = Path(cwd + "./images/Huge Meme Pack/Meme pack by LiquidIllusion")
payload = "# payload"
verbose = True

directory_manipulated = "./manipulated"
if os.path.exists(directory_manipulated):
    shutil.rmtree(directory_manipulated)
os.makedirs(directory_manipulated)

files = [p for p in directory_source.iterdir() if p.is_file()]
for idx, p in enumerate(files):
    with p.open() as file:
        path_original = file.name
        path_manipulated = "./manipulated/" + str(idx) + ".png"
        secret = lsb.hide(path_original, payload)
        secret.save(path_manipulated)
        clear_message = lsb.reveal(path_manipulated)

        if verbose:
            print("original\t " + path_original)
            print("manipulated\t " + path_manipulated)
            print("clear message\t " + clear_message + "\n")
