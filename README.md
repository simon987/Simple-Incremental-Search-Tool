# Simple incremental search tool

Work in progress! Shouldn't be used in production environnments.

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

## Setup on Windows
```bash
git clone https://github.com/simon987/Simple-Incremental-Search-Tool
cd Projet-Web-2018
```
[Download latest elasticsearch version](https://www.elastic.co/downloads/elasticsearch) and extract to `Simple-Incremental-Search-Tool\elasticsearch`

```bash
sudo pip3 install -r requirements.txt

python3 run.py
```

## Setup on Mac/linux
```bash
git clone https://github.com/simon987/Simple-Incremental-Search-Tool
cd Projet-Web-2018
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.2.4.zip
unzip elasticsearch-6.2.4.zip
rm elasticsearch-6.2.4.zip
mv elasticsearch-6.2.4 elasticsearch    

sudo pip3 install -r requirements.txt    

python3 run.py
```

## Running unit tests
```bash
python3 -m unittest
```
