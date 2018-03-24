from PIL import Image
import os
from parsing import ContentMimeGuesser, ExtensionMimeGuesser
from multiprocessing import Value
import ffmpeg


class ThumbnailGenerator:

    def __init__(self, size, quality=85, color="FF00FF"):
        self.size = (size, size)
        self.mime_guesser = ContentMimeGuesser()
        self.quality = quality
        self.color = tuple(bytes.fromhex(color))

    def generate(self, path, dest_path):

        mime = self.mime_guesser.guess_mime(path)

        if mime.startswith("image"):
            try:
                self.generate_image(path, dest_path)
                pass
            except OSError:
                print("Not an image " + path)

        elif mime.startswith("video"):
            try:
                (ffmpeg.
                 input(path)
                 .output("tmp", vframes=1, f="image2", loglevel="error")
                 .run()
                 )
                self.generate_image("tmp", dest_path)
                os.remove("tmp")
            except Exception as e:
                print("Couldn't make thumbnail for " + path)

    def generate_all(self, docs, dest_path, counter: Value=None):

        os.makedirs(dest_path, exist_ok=True)

        for doc in docs:

            full_path = os.path.join(doc["_source"]["path"], doc["_source"]["name"])

            if os.path.isfile(full_path):
                self.generate(full_path, os.path.join(dest_path, doc["_id"]))

            if counter is not None:
                counter.value += 1

    def generate_image(self, path, dest_path):
        with open(path, "rb") as image_file:
            with Image.open(image_file) as image:

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

