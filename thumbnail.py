from PIL import Image


class ThumbnailGenerator:

    def __init__(self, size):
        self.size = (size, size)

    def generate(self, path, dest_path):

        image = Image.open(path)
        image.thumbnail(self.size, Image.BICUBIC)
        image.save(dest_path)
        image.close()
