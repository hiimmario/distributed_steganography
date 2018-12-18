from stegano import lsb
import os

directory = os.fsencode("./images/Huge Meme Pack/Meme pack by LiquidIllusion/")

payload = "# payload"
verbose = False

for idx, subdir, dirs, files in enumerate(os.walk(directory)):
    for file in files:
        path_original = "./" + file + ".png"
        path_manipulated = "./manipulated/" + idx + ".png"

        secret = lsb.hide(path_original, payload)
        secret.save(path_manipulated)
        clear_message = lsb.reveal(path_manipulated)
        if verbose:
            print("original\t " + path_original)
            print("manipulated\t " + path_original)
            print("clear message\t " + clear_message)



