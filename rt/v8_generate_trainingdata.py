# START
#
# https://github.com/ragibson/Steganography (with slight adjustments to automatize the stego process)
#
# The MIT License (MIT)
#
# Copyright (c) 2015 Ryan Gibson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from bit_manipulation import lsb_interleave_list, lsb_deinterleave_list
from bit_manipulation import roundup
import os
from PIL import Image
import sys
from time import time
import string
import random

import shutil

def show_lsb(input_image_path, output_image_path, n):
    """Shows the n least significant bits of image"""
    start = time()
    image = Image.open(input_image_path)

    # Used to set everything but the least significant n bits to 0 when
    # using bitwise AND on an integer
    mask = ((1 << n) - 1)

    color_data = [(255 * ((rgb[0] & mask) + (rgb[1] & mask) + (rgb[2] & mask))
                   // (3 * mask),) * 3 for rgb in image.getdata()]

    image.putdata(color_data)
    print("Runtime: {0:.2f} s".format(time() - start))
    file_name, file_extension = os.path.splitext(output_image_path)
    image.save(file_name + "_{}LSBs".format(n) + file_extension)

def prepare_hide(input_image_path, input_file_path):
    """Prepare files for reading and writing for hiding data."""
    image = Image.open(input_image_path)
    input_file = open(input_file_path, "rb")
    return image, input_file


def prepare_recover(steg_image_path, output_file_path):
    """Prepare files for reading and writing for recovering data."""
    steg_image = Image.open(steg_image_path)
    output_file = open(output_file_path, "wb+")
    return steg_image, output_file


def get_filesize(path):
    """Returns the file size in bytes of the file at path"""
    return os.stat(path).st_size


def max_bits_to_hide(image, num_lsb):
    """Returns the number of bits we're able to hide in the image using
    num_lsb least significant bits."""
    # 3 color channels per pixel, num_lsb bits per color channel.
    return int(3 * image.size[0] * image.size[1] * num_lsb)


def bytes_in_max_file_size(image, num_lsb):
    """Returns the number of bits needed to store the size of the file."""
    return roundup(max_bits_to_hide(image, num_lsb).bit_length() / 8)


def hide_data(input_image_path, input_file_path, steg_image_path, num_lsb,
              compression_level):
    """Hides the data from the input file in the input image."""
    print("Reading files...".ljust(35), end='', flush=True)
    start = time()
    image, input_file = prepare_hide(input_image_path, input_file_path)
    num_channels = len(image.getdata()[0])
    flattened_color_data = [v for t in image.getdata() for v in t]

    # We add the size of the input file to the beginning of the payload.
    file_size = get_filesize(input_file_path)
    file_size_tag = file_size.to_bytes(bytes_in_max_file_size(image, num_lsb),
                                       byteorder=sys.byteorder)

    data = file_size_tag + input_file.read()
    print("Done in {:.2f} s".format(time() - start))

    if 8 * len(data) > max_bits_to_hide(image, num_lsb):
        print("Only able to hide", max_bits_to_hide(image, num_lsb) // 8,
              "B in image. PROCESS WILL FAIL!")

    print("Hiding {} bytes...".format(file_size).ljust(35), end='', flush=True)
    start = time()
    flattened_color_data = lsb_interleave_list(flattened_color_data, data,
                                               num_lsb)
    print("Done in {:.2f} s".format(time() - start))

    print("Writing to output image...".ljust(35), end='', flush=True)
    start = time()
    # PIL expects a sequence of tuples, one per pixel
    image.putdata(list(zip(*[iter(flattened_color_data)] * num_channels)))
    image.save(steg_image_path, compress_level=compression_level)
    print("Done in {:.2f} s".format(time() - start))


def recover_data(steg_image_path, output_file_path, num_lsb):
    """Writes the data from the steganographed image to the output file"""
    print("Reading files...".ljust(35), end='', flush=True)
    start = time()
    steg_image, output_file = prepare_recover(steg_image_path,
                                              output_file_path)

    color_data = [v for t in steg_image.getdata() for v in t]

    file_size_tag_size = bytes_in_max_file_size(steg_image, num_lsb)
    tag_bit_height = roundup(8 * file_size_tag_size / num_lsb)

    bytes_to_recover = int.from_bytes(
        lsb_deinterleave_list(color_data[:tag_bit_height],
                              8 * file_size_tag_size, num_lsb),
        byteorder=sys.byteorder)
    print("Done in {:.2f} s".format(time() - start))

    print("Recovering {} bytes...".format(bytes_to_recover).ljust(35),
          end='', flush=True)
    start = time()
    data = lsb_deinterleave_list(color_data[tag_bit_height:],
                                 8 * bytes_to_recover, num_lsb)
    print("Done in {:.2f} s".format(time() - start))

    print("Writing to output file...".ljust(35), end='', flush=True)
    start = time()
    output_file.write(data)
    output_file.close()
    print("Done in {:.2f} s".format(time() - start))


def analysis(image_file_path, input_file_path, num_lsb):
    """Print how much data we can hide and the size of the data to be hidden"""
    image = Image.open(image_file_path)
    print("Image resolution: ({}, {})\n"
          "Using {} LSBs, we can hide:\t{} B\n"
          "Size of input file:\t\t{} B\n"
          "File size tag:\t\t\t{} B"
          "".format(image.size[0], image.size[1], num_lsb,
                    max_bits_to_hide(image, num_lsb) // 8,
                    get_filesize(input_file_path),
                    bytes_in_max_file_size(image, num_lsb)))


# https://github.com/ragibson/Steganography
# END

def id_generator(size=1, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return "".join(random.choice(chars) for _ in range(size))

input_fp = "payload.txt"
num_bits = 2
compression = 1

raw_images_path = "./raw_originals/"
cover_images_path = "./training_data/cover/"

if os.path.exists(cover_images_path):
    shutil.rmtree(cover_images_path)
os.makedirs(cover_images_path)

for idx, image_file_name in enumerate(os.listdir(raw_images_path)):
    if image_file_name.endswith(".png"):
        im = Image.open(raw_images_path + image_file_name)
        new_width = 400
        new_height = 200
        im = im.resize((new_width, new_height))
        im.save(cover_images_path + image_file_name)

    if idx == 10:
        break

stego_images_path = "./training_data/stego/"
if os.path.exists(stego_images_path):
    shutil.rmtree(stego_images_path)
os.makedirs(stego_images_path)

revealed_files_path = "./training_data/revealed_files/"
if os.path.exists(revealed_files_path):
    shutil.rmtree(revealed_files_path)
os.makedirs(revealed_files_path)

for idx, image_file_name in enumerate(os.listdir(cover_images_path)):
    if image_file_name.endswith(".png"):

        input_file = open(input_fp, "w+")
        input_file.write(id_generator(random.randint(100, 59000)))
        input_file.close()

        analysis(cover_images_path + image_file_name, input_fp, num_bits)
        hide_data(cover_images_path + image_file_name, input_fp, stego_images_path + image_file_name, num_bits, compression)

        recover_data(stego_images_path + image_file_name, revealed_files_path + image_file_name + ".txt", num_bits)

    if idx == 20:
        break


lsb_extracted_cover_images_path = "./training_data/cover_lsb_extracted/"
if os.path.exists(lsb_extracted_cover_images_path):
    shutil.rmtree(lsb_extracted_cover_images_path)
os.makedirs(lsb_extracted_cover_images_path)

lsb_extracted_stego_images_path = "./training_data/stego_lsb_extracted/"
if os.path.exists(lsb_extracted_stego_images_path):
    shutil.rmtree(lsb_extracted_stego_images_path)
os.makedirs(lsb_extracted_stego_images_path)


for idx, image_file_name in enumerate(os.listdir(cover_images_path)):
    if image_file_name.endswith(".png"):
        show_lsb(cover_images_path + image_file_name, lsb_extracted_cover_images_path + image_file_name, num_bits)

    # if idx == 250:
    #     break


for idx, image_file_name in enumerate(os.listdir(stego_images_path)):
    if image_file_name.endswith(".png"):
        show_lsb(stego_images_path + image_file_name, lsb_extracted_stego_images_path + image_file_name, num_bits)

    # if idx == 250:
    #     break
