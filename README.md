# Simple incremental search tool


Portable search tool for local files using Elasticsearch.

### Features
* Incremental search (Search as you type)
* Extracts text from common file types (Mp3 tags, picture sizes, content of docx, pdf, xlsx files etc.)
* Portable installation
* Generate thumbnails for images and videos
* Once indexed, no access to the files is required to search (useful for cold storage)
* Consult videos/GIFs/Images/audio directly in the search result page
* Can be configured to take very low disk space or to store maximum metadata/content

# Screenshots
### Search page
![search](https://user-images.githubusercontent.com/7120851/39211116-aa886db4-47d8-11e8-84a7-1b880ac7802b.png)
### Search results
![results](https://user-images.githubusercontent.com/7120851/39211532-edf617e4-47d9-11e8-9b14-825e46636576.png)


# Installation
Java and python3 are required.    
Once the web server is running, you can connect to the search interface by typing `localhost:8080` in your browser.

## Setup on Windows/Mac/linux (Python 3.5+)

* Download and install [Elasticsearch](https://www.elastic.co/downloads/elasticsearch)

```bash
git clone https://github.com/simon987/Simple-Incremental-Search-Tool

sudo pip3 install -r requirements.txt    
python3 run.py
```

## Running unit tests
```bash
python3 -m unittest
```