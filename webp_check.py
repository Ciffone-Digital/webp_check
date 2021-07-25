#!/usr/bin/env python3

import sys
import os
import requests
import re
from PIL import Image
from requests.exceptions import HTTPError, ConnectTimeout, ReadTimeout, SSLError
from sqlalchemy import create_engine
from wpconfigr.wp_config_file import WpConfigFile


#from config.tokens import CF_PURGE_CACHE,CF_ZONE_ID, CF_API_TOKEN

class wp_database:

    def __init__(self, wp_config):
        wp_conf = WpConfigFile(wp_config)
        hostinfo = wp_conf.get("DB_HOST")
        
        # gather hostname & port
        if ":" in hostinfo:
            hostinfo = hostinfo.split(":")
            self.db_host = hostinfo[0]
            self.db_port = int(hostinfo[1])
        else:
            self.db_host = hostinfo
            self.db_port = 3306 # mysql default
        
        self.db_name = wp_conf.get("DB_NAME")
        self.db_user = wp_conf.get("DB_USER")
        self.db_pass = wp_conf.get("DB_PASSWORD")

        # initialize DB Engine variable
        self.engine = None
        
    def create_db_engine(self):
        if self.engine == None:
            self.engine = create_engine(f"mysql+pymysql://{self.db_user}:{self.db_pass}@{self.db_host}:{str(self.db_port)}/{self.db_name}")

    def test_func(self):
        with self.engine.connect() as conn:
            result = conn.execute(str('SELECT ID, post_content FROM wp_posts'))
            for row in result:
                print(f"{str(row.ID)} = '{row.post_content}'")

    def check_wp_posts_table(self):
        with self.engine.connect() as conn:
            result = conn.execute(str('SELECT ID, post_content FROM wp_posts'))
            img_dict = {}
            incr = 0
            for row in result:
                if '<img' in row.post_content:
                    img_dict[str(incr)] = {'ID' : row.ID, 'post_content' : row.post_content}
                    incr+=1

            return img_dict

    def update_wp_posts_table(self):
        pass 

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

def convert_image_links(post_content):
    # find image links and save to array
    links = re.findall(r'https?://staging\.ciffonedigital\.com[/|.|\w|\s|-]*\.(?:jpe?g|png)', post_content)

    # replace \.(jpg|jpeg|png) w/ .webp
    for l in links:
        ext = l.split('.')[-1:][0]
        new_link = l.replace(ext,'webp')
        post_content = post_content.replace(l, new_link)

    # return post content 
    return post_content


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
        #webp_check(sys.argv[1])
        wp = wp_database(sys.argv[1])
        print(wp.db_host + " " + wp.db_name)
        wp.create_db_engine()
        posts = wp.check_wp_posts_table()

        for key in posts:
            print(posts[key]['ID'])
            print(convert_image_links(posts[key]['post_content']))
            print()
    else:
        print("missing argument...")
        exit(1)
