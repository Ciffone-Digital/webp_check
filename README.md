# webp_check

A Python script to check if images on a website have a Webp equivalent. If none is found, the script will create one in the same directory as the discovered jpeg/jpg/png with the same filename.

This script is ideally configured to be run on a cron.

In order to actually serve the WebP images to users, you configure a webworker to handle requests. If your site is on Cloudflare, worker.js can be copied and pasted directly into a new Cloudflare worker.

If not, modify the code as needed to work with your application.
