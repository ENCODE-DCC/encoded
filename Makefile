clean:
	rm -rf node_modules
	rm -rf .sass-cache
	rm -rf src/encoded/static/build/*
	rm -rf src/encoded/static/build-server/*

install: download-ontology javascript
	pip install -e '.[dev]'
	cp conf/pyramid/development.ini .

javascript-and-download-files: download-annotations download-ontology javascript

download-ontology:
	curl -o ontology.json https://s3-us-west-1.amazonaws.com/encoded-build/ontology/ontology-2021-06-22.json

download-annotations:
	curl -o annotations.json https://s3-us-west-1.amazonaws.com/encoded-build/annotations/annotations_2020_10_21.json

javascript:
	npm ci
	npm run build

config:
	jsonnetfmt -n 2 --max-blank-lines 2 --string-style s --comment-style s -i conf/pyramid/config.jsonnet
	jsonnetfmt -n 2 --max-blank-lines 2 --string-style s --comment-style s -i conf/pyramid/sections.libsonnet
	jsonnet -m conf/pyramid -S conf/pyramid/config.jsonnet
