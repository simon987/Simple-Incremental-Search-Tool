from flask import Flask, render_template, send_file, request
import pysolr
import mimetypes
import requests
import json
from PIL import Image
import os

SOLR_URL = "http://localhost:8983/solr/test/"

solr = pysolr.Solr(SOLR_URL, timeout=10)

app = Flask(__name__)

#
# class Document:
#     def __init__(self, doc_id, name, path, size, md5):
#         self.doc_id = doc_id
#         self.name = name
#         self.path = path
#         self.size = size
#         self.md5 = md5
#
#
# class ImageDocument(Document):
#     def __init__(self, doc_id, name, path, size, md5):
#         super().__init__(doc_id, name, path, size, md5)
#         self.type = "image"
#
#
# class AudioClipDocument(Document):
#     def __init__(self, doc_id, name, path, size, md5):
#         super().__init__(doc_id, name, path, size, md5)
#         self.type = "audio"
#
#
# def get_document(id):
#
#     response = requests.get(SOLR_URL + "get?id=" + id)
#
#     return json.loads(response.text)["doc"]
#
#
# def make_thumb(doc):
#     size = (1024, 1024)
#
#     thumb_path = "thumbnails/" + doc["id"]
#
#     if not os.path.exists(thumb_path):
#
#         file_path = doc["path"][0] + "/" + doc["name"][0]
#
#         if doc["width"][0] > size[0]:
#
#             image = Image.open(file_path)
#             image.thumbnail(size, Image.ANTIALIAS)
#
#             if image.mode == "RGB":
#                 image.save(thumb_path, "JPEG")
#             elif image.mode == "RGBA":
#                 image.save(thumb_path, "PNG")
#             else:
#                 image = image.convert("RGB")
#                 image.save(thumb_path, "JPEG")
#         else:
#             print("Skipping thumbnail")
#             os.symlink(file_path, thumb_path)
#
#     return "thumbnails/" + doc["id"]
#
#
# @app.route("/search/")
# def search():
#
#     query = request.args.get("query")
#     page = int(request.args.get("page"))
#     per_page = int(request.args.get("per_page"))
#
#     results = solr.search(query, None, rows=per_page, start=per_page * page)
#
#     docs = []
#     for r in results:
#
#         if "mime" in r:
#             mime_type = r["mime"][0]
#         else:
#             mime_type = ""
#
#         if mime_type.startswith("image"):
#             docs.append(ImageDocument(r["id"], r["name"][0], r["path"][0], r["size"], r["md5"]))
#
#         elif mime_type.startswith("audio"):
#             docs.append(AudioClipDocument(r["id"], r["name"][0], r["path"][0], r["size"], r["md5"]))
#
#     return render_template("search.html", docs=docs)
#
#
# @app.route("/")
# def index():
#     return render_template("index.html")
#
#
# @app.route("/files/<id>/")
# def files(id):
#
#     doc = get_document(id)
#
#     if doc is not None:
#         file_path = doc["path"][0] + "/" + doc["name"][0]
#         return send_file(file_path, mimetype=mimetypes.guess_type(file_path)[0])
#     else:
#         return "File not found"
#
#
# @app.route("/thumbs/<doc_id>/")
# def thumbs(doc_id):
#
#     doc = get_document(doc_id)
#
#     if doc is not None:
#
#         thumb_path = make_thumb(doc)
#
#         return send_file("thumbnails/" + doc_id, mimetype=mimetypes.guess_type(thumb_path)[0])
#     else:
#         return "File not found"


@app.route("/")
def tmp_route():
    return "test"


if __name__ == "__main__":
    app.run("0.0.0.0", 8080)
