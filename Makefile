clean:
	rm -rf node_modules
	rm -rf .sass-cache
	rm -rf src/encoded/static/build/*
	rm -rf src/encoded/static/build-server/*

devcontainer: download-ontology
	ln -sf /app/node_modules .
	npm run build
	pip install -e '.[dev]'
	cp conf/pyramid/development.ini .

init: stop
	docker compose --profile loading up


serve: download-ontology
	docker compose --profile serving up

stop:
	docker compose down -v --remove-orphans

connect:
	docker exec -it encoded-pyramid-1 /bin/bash

docker-link:
	ln -sf /install/node_modules .
	ln -sf /install/build /encoded/src/encoded/static/build
	ln -sf /install/build-server /encoded/src/encoded/static/build-server

compose: docker-link
	pip install -e '.[dev]'
	cp conf/pyramid/development.ini .

install: download-ontology javascript
	pip install -e '.[dev]'
	cp conf/pyramid/development.ini .

javascript-and-download-files: download-ontology javascript

download-ontology:
	curl -o ontology.json -z ontology.json https://s3-us-west-1.amazonaws.com/encoded-build/ontology/ontology-2022-08-01.json

javascript:
	npm ci
	npm run build

config:
	jsonnetfmt -n 2 --max-blank-lines 2 --string-style s --comment-style s -i conf/pyramid/config.jsonnet
	jsonnetfmt -n 2 --max-blank-lines 2 --string-style s --comment-style s -i conf/pyramid/sections.libsonnet
	jsonnet -m conf/pyramid -S conf/pyramid/config.jsonnet
