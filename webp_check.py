#!/usr/bin/env python3

import sys
import os
from PIL import Image

def webp_check(file_dir):
    if os.path.exists(file_dir) and os.path.isdir(file_dir):
        if not file_dir[-1] == "/":
            file_dir = file_dir + "/"
        files = os.listdir(file_dir)
        for f in files:
            f_path = file_dir + f
            if os.path.isfile(f_path):
                if f_path.split('.')[-1] == "jpg" or f_path.split('.')[-1] == "jpeg" or f_path.split('.')[-1] == "png":
                    # check if webp equivalent exists
                    ext = f_path.split('.')[-1:][0]
                    w_path = f_path.replace(ext,'webp')
                    if not os.path.exists(w_path):
                        convert2webp(f_path,w_path)
                        print(f"'{f_path}' Converted to '{w_path}'")
            elif os.path.isdir(f_path):
                webp_check(f_path)


    else:
        print(f"'{file_dir}' either doesn't exist, or is not a dir...")

def convert2webp(f_image,webp_image):
    im = Image.open(f_image).convert("RGB")
    im.save(webp_image,"webp")
    im.close()

def fix_permissions(f_image,webp_image):
    return 0

if __name__ == '__main__':
    if len(sys.argv) > 1:
        webp_check(sys.argv[1])
    else:
        print("missing argument...")
        exit(1)
