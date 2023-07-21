import os
import requests
import bs4 as bs
import json
import re
import flask_cors
from tqdm import tqdm
from flask import Flask, request, jsonify

SAVE_DIR = "data/"
MAX_RETRIES = 5


def download(url, save_path=""):
    filename = url.split("/")[-1]
    response = requests.get(url, stream=True)
    file_size = int(response.headers.get("Content-Length", 0))
    progress = tqdm(response.iter_content(
        1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    with open(os.path.join(save_path, filename), "wb") as f:
        for data in progress:
            f.write(data)
            progress.update(len(data))


def preview2download(url):
    filename = url.split("/")[-1]
    domain = url.split("/")[2]
    subdomain = domain.split(".")[0]
    url = url.replace(subdomain, subdomain.replace("t", "i"))
    url = url.replace(filename, filename.replace("t.", "."))
    return url


app = Flask(__name__)
flask_cors.CORS(app)


@app.route("/", methods=["POST"])
def download_doujinshi():
    data = request.get_json()
    imgs = data['imgs']
    gallery_id = data['id']
    gallery_dir = SAVE_DIR + "/" + gallery_id
    if not os.path.exists(gallery_dir):
        os.makedirs(gallery_dir)
    with open(gallery_dir + "/info.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    for img in tqdm(imgs, "Downloading images"):
        for _ in range(MAX_RETRIES):
            try:
                download(preview2download(img), gallery_dir)
                break
            except:
                continue
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    app.run(port=8901, debug=False)
