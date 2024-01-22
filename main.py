import os
import requests
import json
import flask_cors
import threading
import zipfile
import re
from xmlschema import XMLSchema, etree_tostring
from tqdm import tqdm
from flask import Flask, request, jsonify

SAVE_DIR = "data/"
MAX_RETRIES = 5

PACK_AS_CBZ = True
SAVE_SEPERATE_FOLDER = True
CBZ_DIR = "cbz/"
XSD_FILE = "ComicInfo.xsd"


def download(url, save_path=""):
    filename = url.split("/")[-1]
    response = requests.get(url, stream=True)
    with open(os.path.join(save_path, filename), "wb") as f:
        for data in response.iter_content(1024):
            f.write(data)


def preview2download(url):
    filename = url.split("/")[-1]
    domain = url.split("/")[2]
    subdomain = domain.split(".")[0]
    url = url.replace(subdomain, subdomain.replace("t", "i"))
    url = url.replace(filename, filename.replace("t.", "."))
    return url


def compressFolder(folder_path, zip_path):
    with zipfile.ZipFile("./tmp", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=os.path.relpath(
                    file_path, folder_path))
    zipf.close()
    os.rename("./tmp", zip_path)


def packAsCbz(gallery_id):
    gallery_id = str(gallery_id)
    with open(f"{SAVE_DIR}/{gallery_id}/info.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    schema = XMLSchema(XSD_FILE)
    comicInfo = {
        "Title": data["title"]["pretty"],
        "Summary": "",
        "Writer": ",".join(data["artists"]),
        "Genre": ",".join(data["categories"]),
        "Tags": "",
        "Characters": ",".join(data["characters"]),
        "SeriesGroup": ",".join(data["groups"])
    }
    if data["subtitle"]["pretty"] != "":
        comicInfo["Title"] = data["subtitle"]["pretty"]
    comicInfo["Summary"] = f"{data['title']['before']}{data['title']['pretty']}{data['title']['after']}\n{data['subtitle']['before']}{data['subtitle']['pretty']}{data['subtitle']['after']}"
    tags = []
    tags.extend(data["parodies"])
    tags.extend(data["characters"])
    tags.extend(data["tags"])
    comicInfo["Tags"] = ",".join(tags)
    root = schema.to_etree(comicInfo)
    xmlFile = f"{SAVE_DIR}/{gallery_id}/ComicInfo.xml"
    with open(xmlFile, "wb") as f:
        f.write(etree_tostring(root, xml_declaration=True, encoding="utf-8"))
    if SAVE_SEPERATE_FOLDER:
        title = re.sub(r'[\/:*?"<>|]', '', comicInfo["Title"])
        folderPath = f"{CBZ_DIR}/{title}"
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        compressFolder(f"{SAVE_DIR}/{gallery_id}", f"{folderPath}/{gallery_id}.cbz")
        return
    compressFolder(f"{SAVE_DIR}/{gallery_id}", f"{CBZ_DIR}/{gallery_id}.cbz")


def downloadProcess(data):
    imgs = data['imgs']
    gallery_id = data['id']
    gallery_dir = SAVE_DIR + "/" + gallery_id
    if not os.path.exists(gallery_dir):
        os.makedirs(gallery_dir)
    with open(gallery_dir + "/info.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    for img in tqdm(imgs, f"Downloading {gallery_id}"):
        for _ in range(MAX_RETRIES):
            try:
                download(preview2download(img), gallery_dir)
                break
            except:
                continue
    if PACK_AS_CBZ:
        packAsCbz(gallery_id)


app = Flask(__name__)
flask_cors.CORS(app)


@app.route("/", methods=["POST"])
def download_doujinshi():
    data = request.get_json()
    threading.Thread(target=downloadProcess, args=(data,)).start()
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    if not os.path.exists(CBZ_DIR) and PACK_AS_CBZ:
        os.makedirs(CBZ_DIR)
    app.run(port=8901, debug=False)
