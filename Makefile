
.PHONY: run-app
run-app:
	python2 app.py


.PHONY: get-media
get-media:
	git clone git@gitlab.com:travel-log/media.git cache/media
	cp cache/media/* static/


.PHONY: dependencies
dependencies: install-python-packages install-jquery install-bootstrap install-osm

.PHONY: install-python-packages
install-python-packages:
	pip2 install -r requirements.txt

.PHONY: install-jquery
install-jquery:
	mkdir -p static/lib/jquery/
	wget -O static/lib/jquery/jquery.min.js https://code.jquery.com/jquery-2.2.0.min.js

.PHONY: install-bootstrap
install-bootstrap:
	wget -P cache https://github.com/twbs/bootstrap/releases/download/v3.3.6/bootstrap-3.3.6-dist.zip
	mkdir -p static/lib/bootstrap/{js,css,fonts}
	cp cache/bootstrap-3.3.6-dist/js/bootstrap.min.js static/lib/bootstrap/js
	cp cache/bootstrap-3.3.6-dist/css/bootstrap.min.css static/lib/bootstrap/css
	cp cache/bootstrap-3.3.6-dist/fonts/glyphicons-halflings-regular.* static/lib/bootstrap/fonts

.PHONY: install-osm
install-osm:
	wget -P static/lib/osm http://openlayers.org/en/v3.12.1/css/ol.css
	wget -P static/lib/osm http://openlayers.org/en/v3.12.1/build/ol.js



.PHONY: clean
clean:
	rm -rf cache



.PHONY: create-database
create-database:
	echo 'DROP DATABASE IF EXISTS travel_log; CREATE DATABASE travel_log;' | psql postgres
	cat data_model.sql | psql travel_log
