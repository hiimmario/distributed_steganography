from stegano import lsb

payload = "# payload"
path_original = "./original.png"
path_manipulated = "./result.png"

secret = lsb.hide(path_original, payload)
secret.save(path_manipulated)
clear_message = lsb.reveal(path_manipulated)

print(clear_message)