from PIL import Image
import os
from multiprocessing import Value, Process
import ffmpeg
import cairosvg


class ThumbnailGenerator:

    def __init__(self, size, quality=85, color="FF00FF"):
        self.size = (size, size)
        self.quality = quality
        self.color = tuple(bytes.fromhex(color))

    def generate(self, path, dest_path, mime):

        if mime is None:
            return

        if mime == "image/svg+xml":

            try:
                p = Process(target=cairosvg.svg2png, kwargs={"url": path, "write_to": "tmp"})
                p.start()
                p.join(1.5)

                if p.is_alive():
                    p.terminate()
                    print("Timed out: " + path)
                else:
                    self.generate_image("tmp", dest_path)
            except Exception:
                print("Couldn't make thumbnail for " + path)

            if os.path.exists("tmp"):
                os.remove("tmp")

        elif mime.startswith("image"):

            try:
                self.generate_image(path, dest_path)
            except Exception:
                print("Couldn't make thumbnail for " + path)

        elif mime.startswith("video"):
            try:
                (ffmpeg.
                 input(path)
                 .output("tmp", vframes=1, f="image2", loglevel="error")
                 .run()
                 )
                self.generate_image("tmp", dest_path)
            except Exception as e:
                print(e)
                print("Couldn't make thumbnail for " + path)

            if os.path.exists("tmp"):
                os.remove("tmp")

    def generate_all(self, docs, dest_path,  counter: Value=None, directory=None):

        os.makedirs(dest_path, exist_ok=True)

        for doc in docs:
            extension = "" if doc["_source"]["extension"] == "" else "." + doc["_source"]["extension"]
            full_path = os.path.join(directory.path, doc["_source"]["path"], doc["_source"]["name"] + extension)

            if os.path.isfile(full_path) and "mime" in doc["_source"]:
                self.generate(full_path, os.path.join(dest_path, doc["_id"]), doc["_source"]["mime"])

            if counter is not None:
                counter.value += 1

    def generate_image(self, path, dest_path):

        with open(path, "rb") as image_file:
            with Image.open(image_file) as image:

                # https://stackoverflow.com/questions/43978819
                if image.mode == "I;16":
                    image.mode = "I"
                    image.point(lambda i: i * (1. / 256)).convert('L')

                image.thumbnail(self.size, Image.BICUBIC)
                canvas = Image.new("RGB", image.size, self.color)

                if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):

                    try:
                        canvas.paste(image, mask=image.split()[-1])
                    except ValueError:
                        canvas.paste(image)
                else:
                    canvas.paste(image)

                canvas.save(dest_path, "JPEG", quality=self.quality, optimize=True)
                canvas.close()
