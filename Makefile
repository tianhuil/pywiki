SHELL := /bin/bash

# set variables
export NAME = pywiki
export PYTHON = python3
export PIP = pip3
export ROOT_DIR = $(shell pwd)

create:
	$$PYTHON -m venv env

install:
	source env/bin/activate && $$PIP install -r requirements.txt
	echo "$$ROOT_DIR/" > $(shell ls -d env/lib/python*/site-packages)/local.pth

create-install: create install
	source env/bin/activate && ipython kernel install --user --name=$$NAME

# from https://stackoverflow.com/a/3452888/8930600
upgrade:
	source env/bin/activate && pip3 list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U

ipython:
	source env/bin/activate && ipython --pdb

jupyter:
	source env/bin/activate && jupyter notebook

cloud-function:
	source env/bin/activate && functions-framework --target=summarize --source=./main.py --port 8081

call-cloud-function:
	source env/bin/activate && python script/call_cloud_function.py 8081

qa:
	source env/bin/activate && python script/qa/alltop.py data/alltop_processed.jl.gz
