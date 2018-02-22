from flask import Flask, render_template, send_file, request, redirect
from indexer import Indexer
from storage import Directory, Option

# indexer = Indexer("fse")

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
from storage import LocalStorage
storage = LocalStorage("local_storage.db")


@app.route("/")
def tmp_route():
    return "huh"


@app.route("/directory")
def directory():

    directories = storage.dirs()
    print(directories)

    return render_template("directory.html", directories=directories)


@app.route("/directory/add")
def directory_add():

    path = request.args.get("path")
    name = request.args.get("name")

    print(name)

    if path is not None and name is not None:
        d = Directory(path, True, [], name)
        storage.save_directory(d)

        return redirect("/directory")

    return "Error"  # todo better message


@app.route("/directory/<int:dir_id>")
def directory_manage(dir_id):

    directory = storage.dirs()[dir_id]

    return render_template("directory_manage.html", directory=directory)


@app.route("/directory/<int:dir_id>/add_opt")
def directory_add_opt(dir_id):

    key = request.args.get("key")
    value = request.args.get("value")

    if key is not None and value is not None:
        storage.save_option(Option(key, value, dir_id))

    return redirect("/directory/" + str(dir_id))


@app.route("/directory/<int:dir_id>/del_opt/<int:opt_id>")
def directory_del_opt(dir_id, opt_id):

    storage.del_option(opt_id)

    return redirect("/directory/" + str(dir_id))


@app.route("/directory/<int:dir_id>/del")
def directory_del(dir_id):

    storage.remove_directory(dir_id)

    return redirect("/directory")


@app.route("/task")
def task():

    tasks = storage.tasks()
    directories = storage.dirs()

    return render_template("task.html", tasks=tasks, directories=directories)


@app.route("/dashboard")
def dashboard():

    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run("0.0.0.0", 8080)
