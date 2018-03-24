import os
from storage import Task, LocalStorage
import json
from multiprocessing import Process, Value
from apscheduler.schedulers.background import BackgroundScheduler
from parsing import GenericFileParser, Md5CheckSumCalculator, ExtensionMimeGuesser, MediaFileParser, TextFileParser, \
    PictureFileParser, Sha1CheckSumCalculator, Sha256CheckSumCalculator, ContentMimeGuesser, MimeGuesser
from indexer import Indexer
from search import Search
from thumbnail import ThumbnailGenerator
from storage import Directory
import shutil


class RunningTask:

    def __init__(self, task: Task):
        self.total_files = Value("i", 0)
        self.parsed_files = Value("i", 0)
        self.task = task
        self.done = Value("i", 0)

    def to_json(self):
        return json.dumps({"parsed": self.parsed_files.value, "total": self.total_files.value, "id": self.task.id})


class Crawler:

    def __init__(self, enabled_parsers: list, mime_guesser: MimeGuesser=ContentMimeGuesser()):
        self.documents = []
        self.enabled_parsers = enabled_parsers

        for parser in self.enabled_parsers:
            if parser.is_default:
                self.default_parser = parser

        self.ext_map = {}

        for parser in self.enabled_parsers:
            for ext in parser.mime_types:
                self.ext_map[ext] = parser

        self.mime_guesser = mime_guesser

    def crawl(self, root_dir: str, counter: Value=None):

        for root, dirs, files in os.walk(root_dir):

            for filename in files:
                full_path = os.path.join(root, filename)

                mime = self.mime_guesser.guess_mime(full_path)

                parser = self.ext_map.get(mime, self.default_parser)

                try:
                    if counter:
                        counter.value += 1

                    doc = parser.parse(full_path)
                    doc["mime"] = mime

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

        directory = self.storage.dirs()[task.dir_id]

        if task.type == Task.INDEX:
            c = Crawler([])
            self.current_task.total_files.value = c.countFiles(directory.path)

            self.current_process = Process(target=self.execute_crawl, args=(directory, self.current_task.parsed_files,
                                                                            self.current_task.done))

        elif task.type == Task.GEN_THUMBNAIL:
            self.current_process = Process(target=self.execute_thumbnails, args=(directory,
                                                                                 self.current_task.total_files,
                                                                                 self.current_task.parsed_files,
                                                                                 self.current_task.done))
        self.current_process.start()

    def execute_crawl(self, directory: Directory, counter: Value, done: Value):

        chksum_calcs = []

        for arg in directory.get_option("CheckSumCalculators").split(","):

            if arg.strip() == "md5":
                chksum_calcs.append(Md5CheckSumCalculator())
            elif arg.strip() == "sha1":
                chksum_calcs.append(Sha1CheckSumCalculator())
            elif arg.strip() == "sha256":
                chksum_calcs.append(Sha256CheckSumCalculator())

        mime_guesser = ExtensionMimeGuesser() if directory.get_option("MimeGuesser") == "extension" \
            else ContentMimeGuesser()

        c = Crawler([GenericFileParser(chksum_calcs),
                     MediaFileParser(chksum_calcs),
                     TextFileParser(chksum_calcs, int(directory.get_option("TextFileContentLenght"))),
                     PictureFileParser(chksum_calcs)],
                    mime_guesser)
        c.crawl(directory.path, counter)

        # todo: create indexer inside the crawler and index every X files
        Indexer("changeme").index(c.documents, directory.id)
        done.value = 1

    def execute_thumbnails(self, directory: Directory, total_files: Value, counter: Value, done: Value):

        dest_path = os.path.join("thumbnails", str(directory.id))
        shutil.rmtree(dest_path)

        docs = list(Search("changeme").get_all_documents(directory.id))

        total_files.value = len(docs)

        tn_generator = ThumbnailGenerator(int(directory.get_option("ThumbnailSize")),
                                          int(directory.get_option("ThumbnailQuality")),
                                          directory.get_option("ThumbnailColor"))
        tn_generator.generate_all(docs, dest_path, counter)

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


