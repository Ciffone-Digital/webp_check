#!/usr/bin/env python3

import sys
import os
import requests
from PIL import Image
from config.tokens import CF_PURGE_CACHE,CF_ZONE_ID, CF_API_TOKEN
from requests.exceptions import HTTPError, ConnectTimeout, ReadTimeout, SSLError

def webp_check(file_dir):
    if os.path.exists(file_dir) and os.path.isdir(file_dir):
        purge_cache = False
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
                        purge_cache = True
            elif os.path.isdir(f_path):
                webp_check(f_path)

        if purge_cache and CF_PURGE_CACHE:
            purge_cloudflare_cache()
    else:
        print(f"'{file_dir}' either doesn't exist, or is not a dir...")

def convert2webp(f_image,webp_image):
    im = Image.open(f_image).convert("RGB")
    im.save(webp_image,"webp")
    im.close()

def purge_cloudflare_cache():
    URL = f'https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/purge_cache'
    cf_headers = {"Content-Type": "Application/json", "Authorization": f"Bearer {CF_API_TOKEN}"}
    cf_data = '{"purge_everything":true}'

    try:
        response = requests.post(URL,headers=cf_headers,data=cf_data)
    except Exception as err:
        print("There was an issue calling cloudflare.")
    else:
        if response.status_code == 200 and response.json()['success']:
            print("cache has been purged.")
        else:
            print("cache has NOT been purged.")
            print(f"{response.json()}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        webp_check(sys.argv[1])
    else:
        print("missing argument...")
        exit(1)
