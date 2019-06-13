import os

if not os.path.exists("tika"):
    os.mkdir("tika")
os.putenv("TIKA_PATH", os.path.join(__name__, "tika/"))
os.putenv("TIKA_LOG_PATH", os.path.join(__name__, "tika/"))

from tika import parser as tika, config

config.getMimeTypes()
