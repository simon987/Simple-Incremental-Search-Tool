from PIL import Image
import os
from parsing import ContentMimeGuesser


class ThumbnailGenerator:

    def __init__(self, size):
        self.size = (size, size)
        self.mime_guesser = ContentMimeGuesser

    def generate(self, path, dest_path):

        try:
            with open(path, "rb") as image_file:
                with Image.open(image_file) as image:

                    image.thumbnail(self.size, Image.BICUBIC)

                    canvas = Image.new("RGB", image.size, (255, 0, 255))

                    if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
                        canvas.paste(image, mask=image.split()[3])  # 3 is the alpha channel
                    else:
                        canvas.paste(image)

                    canvas.save(dest_path, "JPEG", quality=50, optimize=True)
                    canvas.close()

        except OSError as e:
            print(e)
            print("Not an image " + path)

    def generate_all(self, docs, dest_path):

        os.makedirs(dest_path, exist_ok=True)

        for doc in docs:

            full_path = os.path.join(doc["_source"]["path"], doc["_source"]["name"])

            if os.path.isfile(full_path):
                self.generate(full_path, os.path.join(dest_path, doc["_id"]))