# pywiki
useful scripts for working with wikipedia dumps

# Install and Setup
To install, run
```
make create-install
```

You will need to activate the virtual environment before running any given command by running
```
source env/bin/activate
```

# Wordcount
Download the latest version of simple english wikipedia from https://dumps.wikimedia.org/simplewiki/20210101/simplewiki-20210101-pages-meta-current.xml.bz2 (you will have to update the date).  Run the
```
python script/count.py -m 5  simple-wiki.xml.bz2 simple-wiki-count.csv.gz
bck-i-search: python
```
