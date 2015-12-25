
.PHONY: run-app
run-app:
	python2 app.py


.PHONY: get-media
get-media:
	git clone git@gitlab.com:crst/working-title-media.git media
	cp media/* static/


.PHONY: dependencies
dependencies: install-python-packages install-jquery install-bootstrap install-osm

.PHONY: install-python-packages
install-python-packages:
	pip2 install -r requirements.txt

.PHONY: install-jquery
install-jquery:
	bower install jquery#2.1.4
	mkdir -p static/lib/jquery/
	cp bower_components/jquery/dist/jquery.min.js static/lib/jquery

.PHONY: install-bootstrap
install-bootstrap:
	bower install bootstrap#3.3.6
	mkdir -p static/lib/bootstrap/{js,css,fonts}
	cp bower_components/bootstrap/dist/js/bootstrap.min.js static/lib/bootstrap/js
	cp bower_components/bootstrap/dist/css/bootstrap.min.css static/lib/bootstrap/css
	cp bower_components/bootstrap/dist/fonts/glyphicons-halflings-regular.* static/lib/bootstrap/fonts

.PHONY: install-osm
install-osm:
	wget -P static/lib/osm http://openlayers.org/en/v3.12.1/css/ol.css
	wget -P static/lib/osm http://openlayers.org/en/v3.12.1/build/ol.js



.PHONY: clean
clean:
	rm -rf bower-components



.PHONY: create-database
create-database:
	echo 'DROP DATABASE IF EXISTS app; CREATE DATABASE app;' | psql postgres
	cat data_model.sql | psql app



.PHONY: user-log
user-log:
	@tail -f log/app.log | grep '{User}'

.PHONY: album-log
album-log:
	@tail -f log/app.log | grep '{Album}'

.PHONY: edit-log
edit-log:
	@tail -f log/app.log | grep '{Edit album}'

.PHONY: share-log
share-log:
	@tail -f log/app.log | grep '{Share album}'
