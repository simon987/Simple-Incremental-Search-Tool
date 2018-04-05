from flask import Flask, render_template, request, redirect, flash, session, abort, send_file
from storage import Directory, Option, Task
from storage import LocalStorage, DuplicateDirectoryException
from crawler import RunningTask, TaskManager
import json
import os
import humanfriendly
from search import Search
from PIL import Image
from io import BytesIO

app = Flask(__name__)
app.secret_key = "A very secret key"
storage = LocalStorage("local_storage.db")

tm = TaskManager(storage)
search = Search("changeme")




def get_dir_size(path):

    size = 0

    for root, dirs, files in os.walk(path):
        for filename in files:

            full_path = os.path.join(root, filename)
            size += os.path.getsize(full_path)

    return size


@app.route("/document/<doc_id>")
def document(doc_id):

    doc = search.get_doc(doc_id)["_source"]
    directory = storage.dirs()[doc["directory"]]

    del doc["directory"]

    return render_template("document.html", doc=doc, directory=directory, doc_id=doc_id)


@app.route("/dl/<doc_id>")
def file(doc_id):

    doc = search.get_doc(doc_id)["_source"]
    directory = storage.dirs()[doc["directory"]]

    extension = "" if doc["extension"] is None or doc["extension"] == "" else "." + doc["extension"]
    full_path = os.path.join(directory.path, doc["path"], doc["name"] + extension)

    return send_file(full_path, mimetype=doc["mime"], as_attachment=True, attachment_filename=doc["name"])


@app.route("/file/<doc_id>")
def download(doc_id):

    doc = search.get_doc(doc_id)["_source"]
    directory = storage.dirs()[doc["directory"]]
    extension = "" if doc["extension"] is None or doc["extension"] == "" else "." + doc["extension"]
    full_path = os.path.join(directory.path, doc["path"], doc["name"] + extension)

    return send_file(full_path)


@app.route("/thumb/<doc_id>")
def thumb(doc_id):

    doc = search.get_doc(doc_id)

    if doc is not None:

        tn_path = os.path.join("static/thumbnails/", str(doc["_source"]["directory"]), doc_id)
        print(tn_path)
        if os.path.isfile(tn_path):
            return send_file(tn_path)
        else:
            print("tn not found")
            default_thumbnail = BytesIO()
            Image.new("RGB", (255, 128), (0, 0, 0)).save(default_thumbnail, "JPEG")
            default_thumbnail.seek(0)
            return send_file(default_thumbnail, "image/jpeg")

    else:
        print("doc is none")
        default_thumbnail = BytesIO()
        Image.new("RGB", (255, 128), (0, 0, 0)).save(default_thumbnail, "JPEG")
        default_thumbnail.seek(0)
        return send_file(default_thumbnail, "image/jpeg")


@app.route("/")
def search_page():
    return render_template("search.html")

@app.route("/list")
def search_liste_page():
    return render_template("searchList.html")


@app.route("/search")
def search_route():

    query = request.args.get("q")
    query = "" if query is None else query
    page = search.search(query)

    return json.dumps(page)


@app.route("/scroll")
def scroll_route():

    scroll_id = request.args.get("scroll_id")

    page = search.scroll(scroll_id)

    return json.dumps(page)


@app.route("/directory")
def dir_list():

    return render_template("directory.html", directories=storage.dirs())


@app.route("/directory/add")
def directory_add():

    path = request.args.get("path")
    name = request.args.get("name")

    if path is not None and name is not None:
        d = Directory(path, True, [], name)

        try:
            d.set_default_options()
            storage.save_directory(d)
            flash("<strong>Created directory</strong>", "success")
        except DuplicateDirectoryException:
            flash("<strong>Couldn't create directory</strong> Make sure that the path is unique", "danger")

    return redirect("/directory")


@app.route("/directory/<int:dir_id>")
def directory_manage(dir_id):

    directory = storage.dirs()[dir_id]
    tn_size = get_dir_size("static/thumbnails/" + str(dir_id))
    tn_size_formatted = humanfriendly.format_size(tn_size)

    index_size = search.get_index_size()
    index_size_formatted = humanfriendly.format_size(index_size)

    return render_template("directory_manage.html", directory=directory, tn_size=tn_size,
                           tn_size_formatted=tn_size_formatted, index_size=index_size,
                           index_size_formatted=index_size_formatted, doc_count=search.get_doc_count())


@app.route("/directory/<int:dir_id>/update")
def directory_update(dir_id):

    directory = storage.dirs()[dir_id]

    name = request.args.get("name")
    name = directory.name if name is None else name

    enabled = request.args.get("enabled")
    enabled = directory.enabled if enabled is None else int(enabled)

    path = request.args.get("path")
    path = directory.path if path is None else path

    # Only name and enabled status can be updated
    updated_dir = Directory(path, enabled, directory.options, name)
    updated_dir.id = dir_id
    storage.update_directory(updated_dir)

    flash("<strong>Updated directory</strong>", "success")

    return redirect("/directory/" + str(dir_id))


@app.route("/directory/<int:dir_id>/update_opt")
def directory_update_opt(dir_id):

    opt_id = request.args.get("id")
    opt_key = request.args.get("key")
    opt_value = request.args.get("value")

    storage.update_option(Option(opt_key, opt_value, dir_id, opt_id))

    return redirect("/directory/" + str(dir_id))


@app.route("/directory/<int:dir_id>/del")
def directory_del(dir_id):

    storage.remove_directory(dir_id)
    flash("<strong>Deleted directory</strong>", "success")

    return redirect("/directory")


@app.route("/directory/<int:dir_id>/reset")
def directory_reset(dir_id):
    directory = storage.dirs()[dir_id]

    for opt in directory.options:
        storage.del_option(opt.id)

    directory.set_default_options()

    for opt in directory.options:
        opt.dir_id = dir_id
        storage.save_option(opt)

    storage.dir_cache_outdated = True

    flash("<strong>Reset directory options to default settings</strong>", "success")
    return redirect("directory/" + str(dir_id))


@app.route("/task")
def task():

    return render_template("task.html", tasks=storage.tasks(), directories=storage.dirs(),
                           task_list=json.dumps(list(storage.tasks().keys())))
    # return render_template("task.html", tasks=storage.tasks(), directories=storage.dirs())


@app.route("/task/current")
def get_current_task():

    if tm and tm.current_task:
        return tm.current_task.to_json()
    else:
        return ""


@app.route("/task/current/cancel")
def cancel_current_task():

    tm.cancel_task()
    return redirect("/task")


@app.route("/task/add")
def task_add():
    type = request.args.get("type")
    directory = request.args.get("directory")

    storage.save_task(Task(type, directory))

    return redirect("/task")


@app.route("/task/<int:task_id>/del")
def task_del(task_id):
    storage.del_task(task_id)

    return redirect("/task")


@app.route("/dashboard")
def dashboard():

    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run("0.0.0.0", 8080, threaded=True)
