import json
import os
import shutil
from io import BytesIO

import bcrypt
import humanfriendly
from PIL import Image
from flask import Flask, render_template, request, redirect, flash, session, abort, send_file

import config
from crawler import TaskManager
from search import Search
from storage import Directory, Option, Task, User
from storage import LocalStorage, DuplicateDirectoryException, DuplicateUserException
from thumbnail import ThumbnailGenerator

app = Flask(__name__)
app.secret_key = "A very secret key"
storage = LocalStorage(config.db_path)

tm = TaskManager(storage)
search = Search("changeme")


def get_dir_size(path):
    size = 0

    for root, dirs, files in os.walk(path):
        for filename in files:
            full_path = os.path.join(root, filename)
            size += os.path.getsize(full_path)

    return size


@app.route("/user/<user>")
def user_manage(user):
    if "admin" in session and session["admin"]:
        return render_template("user_manage.html", directories=storage.dirs(), user=storage.users()[user])
    flash("You are not authorized to access this page", "warning")
    return redirect("/")


@app.route("/logout")
def logout():
    session.pop("username")
    session.pop("admin")
    flash("Successfully logged out", "success")
    return redirect("/")


@app.route("/login", methods=['POST'])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if storage.auth_user(username, password):
        session["username"] = username
        session["admin"] = storage.users()[username].admin

        flash("Successfully logged in", "success")
    else:
        flash("Invalid username or password", "danger")

    return redirect("/")


@app.route("/user")
def user_page():
    admin_account_present = False

    for user in storage.users():
        if storage.users()[user].admin:
            admin_account_present = True
            break

    if not admin_account_present or ("admin" in session and session["admin"]):
        return render_template("user.html", users=storage.users(), admin_account_present=admin_account_present)
    flash("You are not authorized to access this page", "warning")
    return redirect("/")


@app.route("/user/<username>/set_access")
def user_set_access(username):
    if "admin" in session and session["admin"]:
        dir_id = request.args["dir_id"]
        user = storage.users()[username]

        if request.args["access"] == "1":
            user.readable_directories.add(int(dir_id))
        else:
            if int(dir_id) in user.readable_directories:
                user.readable_directories.remove(int(dir_id))

        storage.update_user(user)

        flash("Permissions mises à jour", "success")
        return redirect("/user/" + username)
    flash("You are not authorized to access this page", "warning")
    return redirect("/")


@app.route("/user/<username>/set_admin")
def user_set_admin(username):
    if "admin" in session and session["admin"]:

        user = storage.users()[username]

        if user.username == session["username"]:
            flash("You cannot modifiy your own account", "warning")
        else:
            user.admin = request.args["admin"] == "1"
            storage.update_user(user)

            flash("Permissions updated", "success")

        return redirect("/user/" + username)


@app.route("/user/add", methods=['POST'])
def user_add():
    admin_account_present = False

    for user in storage.users():
        if storage.users()[user].admin:
            admin_account_present = True
            break

    if not admin_account_present or ("admin" in session and session["admin"]):
        username = request.form["username"]
        password = bcrypt.hashpw(request.form["password"].encode("utf-8"), bcrypt.gensalt(config.bcrypt_rounds))
        is_admin = True if "is_admin" in request.form else False

        try:
            storage.save_user(User(username, password, is_admin))
            flash("Created new user", "success")
        except DuplicateUserException:
            flash("<strong>Couldn't create user</strong> "
                  "Make sure that the username is unique", "danger")

        return redirect("/user")
    flash("You are not authorized to access this page", "warning")
    return redirect("/")


@app.route("/user/<username>/del")
def user_del(username):
    if "admin" in session and session["admin"]:

        if session["username"] == username:
            flash("You cannot delete your own account", "warning")
            return redirect("/user/" + username)
        storage.remove_user(username)
        flash("User deleted", "success")
        return redirect("/user")
    flash("You are not authorized to access this page", "warning")
    return redirect("/")


@app.route("/suggest")
def suggest():
    return json.dumps(search.suggest(request.args.get("prefix")))


@app.route("/document/<doc_id>")
def document(doc_id):
    doc = search.get_doc(doc_id)["_source"]
    directory = storage.dirs()[doc["directory"]]

    del doc["directory"]

    return render_template("document.html", doc=doc, directory=directory, doc_id=doc_id)


@app.route("/dl/<doc_id>")
def serve_file(doc_id):
    doc = search.get_doc(doc_id)["_source"]
    directory = storage.dirs()[doc["directory"]]

    extension = "" if doc["extension"] is None or doc["extension"] == "" else "." + doc["extension"]
    full_path = os.path.join(directory.path, doc["path"], doc["name"] + extension)

    if not os.path.exists(full_path):
        return abort(404)

    return send_file(full_path, mimetype=doc["mime"], as_attachment=True, attachment_filename=doc["name"] + extension)


@app.route("/file/<doc_id>")
def download(doc_id):
    doc = search.get_doc(doc_id)["_source"]
    directory = storage.dirs()[doc["directory"]]
    extension = "" if doc["extension"] is None or doc["extension"] == "" else "." + doc["extension"]
    full_path = os.path.join(directory.path, doc["path"], doc["name"] + extension)

    if not os.path.exists(full_path):
        return abort(404)

    return send_file(full_path, mimetype=doc["mime"], conditional=True)


@app.route("/thumb/<doc_id>")
def thumb(doc_id):
    doc = search.get_doc(doc_id)

    if doc is not None:
        dest_path = "static/thumbnails/" + str(doc["_source"]["directory"])
        os.makedirs(dest_path, exist_ok=True)
        tn_path = os.path.join(dest_path, doc_id)
        if os.path.isfile(tn_path):
            return send_file(tn_path)

        directory = storage.dirs()[doc["_source"]["directory"]]
        extension = "" if doc["_source"]["extension"] is None or doc["_source"]["extension"] == "" else \
            "." + doc["_source"]["extension"]
        full_path = os.path.join(directory.path,
                                 doc["_source"]["path"],
                                 doc["_source"]["name"] + extension)
        tn_generator = ThumbnailGenerator(int(directory.get_option("ThumbnailSize")),
                                          int(directory.get_option("ThumbnailQuality")),
                                          directory.get_option("ThumbnailColor"))
        tn_generator.generate(full_path, tn_path, doc["_source"]["mime"])
        if os.path.isfile(tn_path):
            return send_file(tn_path)

    default_thumbnail = BytesIO()
    Image.new("RGB", (255, 128), (0, 0, 0)).save(default_thumbnail, "JPEG")
    default_thumbnail.seek(0)
    return send_file(default_thumbnail, "image/jpeg")


@app.route("/")
def search_page():
    mime_map = search.get_mime_map()
    mime_map.append({"id": "any", "text": "All"})

    directories = [storage.dirs()[x] for x in get_allowed_dirs(session["username"] if "username" in session else None)]

    return render_template("search.html",
                           directories=directories,
                           mime_map=mime_map)


@app.route("/list")
def search_liste_page():
    return render_template("searchList.html")


def get_allowed_dirs(username):
    if config.allow_guests:
        return [x for x in storage.dirs() if storage.dirs()[x].enabled]
    if username:
        user = storage.users()[username]
        return [x for x in storage.dirs() if storage.dirs()[x].enabled and x in user.readable_directories]
    return list()


@app.route("/search", methods=['POST'])
def search_route():
    query = request.json["q"]
    query = "" if query is None else query

    size_min = request.json["size_min"]
    size_max = request.json["size_max"]
    mime_types = request.json["mime_types"]
    must_match = request.json["must_match"]
    directories = request.json["directories"]

    # Remove disabled & non-existing directories
    allowed_dirs = get_allowed_dirs(session["username"] if "username" in session else None)
    directories = [x for x in directories if x in allowed_dirs]

    path = request.json["path"]

    page = search.search(query, size_min, size_max, mime_types, must_match, directories, path)

    return json.dumps(page)


@app.route("/scroll")
def scroll_route():
    scroll_id = request.args.get("scroll_id")

    page = search.scroll(scroll_id)

    return json.dumps(page)


@app.route("/directory")
def dir_list():
    if "admin" in session and session["admin"]:
        return render_template("directory.html", directories=storage.dirs())
    flash("You are not authorized to access this page", "warning")
    return redirect("/")


@app.route("/directory/add")
def directory_add():
    if "admin" in session and session["admin"]:
        path = request.args.get("path")
        name = request.args.get("name")

        if path is not None and name is not None:
            d = Directory(path, True, [], name)

            try:
                d.set_default_options()
                storage.save_directory(d)
                flash("<strong>Directory created</strong>", "success")
            except DuplicateDirectoryException:
                flash("<strong>The directory couldn't be created</strong> Make sure to chose a unique name",
                      "danger")

        return redirect("/directory")
    flash("You are not authorized to access this page", "warning")
    return redirect("/")


@app.route("/directory/<int:dir_id>")
def directory_manage(dir_id):
    if "admin" in session and session["admin"]:
        directory = storage.dirs()[dir_id]
        tn_size = get_dir_size("static/thumbnails/" + str(dir_id))
        tn_size_formatted = humanfriendly.format_size(tn_size)

        return render_template("directory_manage.html", directory=directory, tn_size=tn_size,
                               tn_size_formatted=tn_size_formatted)
    flash("You are not authorized to access this page", "warning")
    return redirect("/")


@app.route("/directory/<int:dir_id>/update")
def directory_update(dir_id):
    if "admin" in session and session["admin"]:
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

        try:
            storage.update_directory(updated_dir)
            flash("<strong>Updated directory</strong>", "success")

        except DuplicateDirectoryException:
            flash("<strong>The directory couldn't be updated</strong> Make the that the path is unique",
                  "danger")

        return redirect("/directory/" + str(dir_id))
    flash("You are not authorized to access this page", "warning")
    return redirect("/")


@app.route("/directory/<int:dir_id>/update_opt")
def directory_update_opt(dir_id):
    if "admin" in session and session["admin"]:
        opt_id = request.args.get("id")
        opt_key = request.args.get("key")
        opt_value = request.args.get("value")

        storage.update_option(Option(opt_key, opt_value, dir_id, opt_id))

        return redirect("/directory/" + str(dir_id))
    flash("You are not authorized to access this page", "warning")
    return redirect("/")


@app.route("/directory/<int:dir_id>/del")
def directory_del(dir_id):
    if "admin" in session and session["admin"]:
        search.delete_directory(dir_id)
        if os.path.exists("static/thumbnails/" + str(dir_id)):
            shutil.rmtree("static/thumbnails/" + str(dir_id))

        storage.remove_directory(dir_id)
        flash("<strong>Deleted folder</strong>", "success")

        return redirect("/directory")
    flash("You are not authorized to access this page", "warning")
    return redirect("/")


@app.route("/directory/<int:dir_id>/reset")
def directory_reset(dir_id):
    if "admin" in session and session["admin"]:
        directory = storage.dirs()[dir_id]

        for opt in directory.options:
            storage.del_option(opt.id)

        directory.set_default_options()

        for opt in directory.options:
            opt.dir_id = dir_id
            storage.save_option(opt)

        storage.dir_cache_outdated = True

        search.delete_directory(dir_id)

        flash("<strong>Reset directory options</strong>", "success")
        return redirect("directory/" + str(dir_id))
    flash("You are not authorized to access this page", "warning")
    return redirect("/")


@app.route("/task")
def task():
    if "admin" in session and session["admin"]:
        return render_template("task.html", tasks=storage.tasks(), directories=storage.dirs(),
                               task_list=json.dumps(list(storage.tasks().keys())))
    flash("You are not authorized to access this page", "warning")
    return redirect("/")


@app.route("/task/current")
def get_current_task():
    if "admin" in session and session["admin"]:

        if tm and tm.current_task:
            return tm.current_task.to_json()
        return ""
    flash("You are not authorized to access this page", "warning")
    return redirect("/")


@app.route("/task/add")
def task_add():
    if "admin" in session and session["admin"]:
        task_type = request.args.get("type")
        directory = request.args.get("directory")

        if task_type not in ("1", "2"):
            flash("Please choose a task type", "danger")
            return redirect("/task")

        if directory.isdigit() and int(directory) in storage.dirs():
            storage.save_task(Task(task_type, directory))
        else:
            flash("You must choose a directory", "danger")

        return redirect("/task")
    flash("You are not authorized to access this page", "warning")
    return redirect("/")


@app.route("/task/<int:task_id>/del")
def task_del(task_id):
    if "admin" in session and session["admin"]:
        storage.del_task(task_id)

        if tm.current_task is not None and task_id == tm.current_task.task.id:
            tm.cancel_task()

        return redirect("/task")
    flash("You are not authorized to access this page", "warning")
    return redirect("/")


@app.route("/reset_es")
def reset_es():
    if "admin" in session and session["admin"]:
        flash("Elasticsearch index has been reset. Modifications made in <b>config.py</b> have been applied.",
              "success")

        tm.indexer.init()
        if os.path.exists("static/thumbnails"):
            shutil.rmtree("static/thumbnails")

        return redirect("/dashboard")
    flash("You are not authorized to access this page", "warning")
    return redirect("/")


@app.route("/dashboard")
def dashboard():
    if "admin" in session and session["admin"]:
        tn_sizes = {}
        tn_size_total = 0
        for directory in storage.dirs():
            tn_size = get_dir_size("static/thumbnails/" + str(directory))
            tn_size_formatted = humanfriendly.format_size(tn_size)

            tn_sizes[directory] = tn_size_formatted
            tn_size_total += tn_size

        tn_size_total_formatted = humanfriendly.format_size(tn_size_total)

        return render_template("dashboard.html", version=config.VERSION, tn_sizes=tn_sizes,
                               tn_size_total=tn_size_total_formatted,
                               doc_size=humanfriendly.format_size(search.get_doc_size()),
                               doc_count=search.get_doc_count(),
                               db_path=config.db_path,
                               elasticsearch_url=config.elasticsearch_url,
                               index_size=humanfriendly.format_size(search.get_index_size()))

    flash("You are not authorized to access this page", "warning")
    return redirect("/")


if __name__ == "__main__":
    app.run("0.0.0.0", 8080, threaded=True)
