import os
import hashlib
import mimetypes
from PIL import Image
import simplejson

rootDir = "/home/simon/Documents"


# https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
def md5sum(filename, block_size=65536):
    hash = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            hash.update(block)
    return hash.hexdigest()


def crawl(root_dir):

    docs = []

    for root, subdirs, files in os.walk(root_dir):

        print(root)

        for filename in files:
            full_path = os.path.join(root, filename)

            doc = dict()

            doc["md5"] = md5sum(os.path.join(root, filename))
            doc["path"] = root
            doc["name"] = filename
            doc["size"] = os.path.getsize(full_path)
            doc["mtime"] = int(os.path.getmtime(full_path))

            mime_type = mimetypes.guess_type(full_path)[0]

            if mime_type is not None:

                doc["mime"] = mime_type

                if mime_type.startswith("image"):
                    try:
                        width, height = Image.open(full_path).size

                        doc["width"] = width
                        doc["height"] = height
                    except OSError:
                        doc.pop('mime', None)
                        pass
                    except ValueError:
                        doc.pop('mime', None)
                        pass

            docs.append(doc)

    file = open("crawler.json", "w")
    file.write(simplejson.dumps(docs))
    file.close()


crawl(rootDir)