from flask import Flask, render_template, send_file, request, redirect, flash, session
from indexer import Indexer
from storage import Directory, Option, Task
from storage import LocalStorage, DuplicateDirectoryException
from crawler import RunningTask, TaskManager
import json

# indexer = Indexer("fse")

app = Flask(__name__)
app.secret_key = "A very secret key"
storage = LocalStorage("local_storage.db")


tm = TaskManager(storage)

@app.route("/")
def tmp_route():
    return "huh"


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
            storage.save_directory(d)
            flash("<strong>Created directory</strong>", "success")
        except DuplicateDirectoryException:
            flash("<strong>Couldn't create directory</strong> Make sure that the path is unique", "danger")

    return redirect("/directory")


@app.route("/directory/<int:dir_id>")
def directory_manage(dir_id):

    directory = storage.dirs()[dir_id]

    return render_template("directory_manage.html", directory=directory)


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


@app.route("/directory/<int:dir_id>/add_opt")
def directory_add_opt(dir_id):

    key = request.args.get("key")
    value = request.args.get("value")

    if key is not None and value is not None:
        storage.save_option(Option(key, value, dir_id))
        flash("<strong>Added option</strong>", "success")

    return redirect("/directory/" + str(dir_id))


@app.route("/directory/<int:dir_id>/del_opt/<int:opt_id>")
def directory_del_opt(dir_id, opt_id):

    storage.del_option(opt_id)
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


for t in storage.tasks():
    a_task = t
    break

# tm = None

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
    app.run("0.0.0.0", 8080)
