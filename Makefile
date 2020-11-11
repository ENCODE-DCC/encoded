clean:
	rm -rf node_modules eggs parts bin develop
	rm -rf .sass-cache
	rm -rf src/encoded/static/build/*
	rm -rf src/encoded/static/build-server/*

dev-clean:
	rm -rf node_modules eggs parts bin
	rm -rf .sass-cache
	rm -rf src/encoded/static/build/*
	rm -rf src/encoded/static/build-server/*
