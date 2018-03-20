import os
from storage import Task, LocalStorage
import json
from multiprocessing import Process, Value
from apscheduler.schedulers.background import BackgroundScheduler
from parsing import GenericFileParser, Md5CheckSumCalculator, ExtensionMimeGuesser
from indexer import Indexer
from search import Search


class RunningTask:

    def __init__(self, task: Task):
        self.total_files = Value("i", 0)
        self.parsed_files = Value("i", 0)
        self.task = task
        self.done = Value("i", 0)

    def to_json(self):
        return json.dumps({"parsed": self.parsed_files.value, "total": self.total_files.value, "id": self.task.id})


class Crawler:

    def __init__(self, enabled_parsers: list):
        self.documents = []
        self.enabled_parsers = enabled_parsers

        for parser in self.enabled_parsers:
            if parser.is_default:
                self.default_parser = parser

        self.ext_map = {}

        for parser in self.enabled_parsers:
            for ext in parser.extensions:
                self.ext_map[ext] = parser

    def crawl(self, root_dir: str, counter: Value=None):

        for root, dirs, files in os.walk(root_dir):

            for filename in files:
                full_path = os.path.join(root, filename)

                parser = self.ext_map.get(os.path.splitext(filename)[1], self.default_parser)

                try:
                    if counter:
                        counter.value += 1

                    doc = parser.parse(full_path)

                    self.documents.append(doc)
                except FileNotFoundError:
                    continue  # File was deleted

    def countFiles(self, root_dir: str):
        count = 0

        for root, dirs, files in os.walk(root_dir):
            count += len(files)

        return count


class TaskManager:
    def __init__(self, storage: LocalStorage):
        self.current_task = None
        self.storage = storage
        self.current_process = None
        self.indexer = Indexer("changeme")

        scheduler = BackgroundScheduler()
        scheduler.add_job(self.check_new_task, "interval", seconds=0.5)
        scheduler.start()

    def start_task(self, task: Task):
        self.current_task = RunningTask(task)

        if task.type == Task.INDEX:
            c = Crawler([])
            path = self.storage.dirs()[task.dir_id].path
            self.current_task.total_files.value = c.countFiles(path)

            self.current_process = Process(target=self.execute_crawl, args=(path, self.current_task.parsed_files,
                                                                            self.current_task.done,
                                                                            self.current_task.task.dir_id))
            self.current_process.start()

        elif task.type == Task.GEN_THUMBNAIL:
            self.current_process = Process(target=self.execute_thumbnails, args=(self.current_task.task.dir_id,
                                                                                 self.current_task.total_files,
                                                                                 self.current_task.parsed_files,
                                                                                 self.current_task.done))
            self.current_process.start()

    def execute_crawl(self, path: str, counter: Value, done: Value, directory: int):
        c = Crawler([GenericFileParser([Md5CheckSumCalculator()], ExtensionMimeGuesser())])
        c.crawl(path, counter)

        Indexer("changeme").index(c.documents, directory)
        done.value = 1

    def execute_thumbnails(self, dir_id: int, total_files: Value, counter: Value, done: Value):

        docs = list(Search("changeme").getAllDocuments(dir_id))

        total_files.value = len(docs)

        done.value = 1

    def cancel_task(self):
        self.current_task = None
        self.current_process.terminate()

    def check_new_task(self):

        if self.current_task is None:
            for i in sorted(self.storage.tasks(), reverse=True):
                if not self.storage.tasks()[i].completed:
                    self.start_task(self.storage.tasks()[i])
        else:
            if self.current_task.done.value == 1:

                self.current_process.terminate()
                self.storage.del_task(self.current_task.task.id)
                self.current_task = None


