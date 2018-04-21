# Do not change option names
default_options = {
    "ThumbnailQuality": "85",
    "ThumbnailSize": "272",
    "ThumbnailColor": "FF00FF",
    "TextFileContentLength": "2000",
    "PdfFileContentLength": "2000",
    "SpreadsheetContentLength": "2000",
    "EbookContentLength": "2000",
    "MimeGuesser": "extension",  # extension, content
    "CheckSumCalculators": "",  # md5, sha1, sha256
    "FileParsers": "media, text, picture, font, pdf, docx, spreadsheet, ebook"
}

# Index documents after every X parsed files (Larger number will use more memory)
index_every = 10000

# See https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-ngram-tokenizer.html#_configuration_16
nGramMin = 3
nGramMax = 3
elasticsearch_url = "http://localhost:9200"

# Password hashing
bcrypt_rounds = 14
# sqlite3 database path
db_path = "./local_storage.db"

VERSION = "1.0a"
