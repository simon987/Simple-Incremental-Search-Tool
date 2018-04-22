# Simple incremental search tool

Work in progress: probably won't work without some tweaking

## Running on linux
```bash
git clone https://github.com/simon987/Projet-Web-2018
cd Projet-Web-2018
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.2.4.zip
unzip elasticsearch-6.2.4.zip
rm elasticsearch-6.2.4.zip
mv elasticsearch-6.2.4 elasticsearch

sudo pip3 install -r requirements.txt

python3 run.py
```

## Running tests
```
python3 -m unittest discover
```
