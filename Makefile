
.PHONY: run-travel-log
run-travel-log:
	@( \
		source env/bin/activate; \
		cd src && python3 app.py; \
	)

.PHONY: run-request-logger
run-request-logger:
	@( \
		source env/bin/activate; \
		cd src && python3 request_logger.py; \
	)

.PHONY: vacuum
vacuum:
	@( \
		source env/bin/activate; \
		cd src && python3 vacuum.py; \
	)


JS_FILES = $(filter-out %.min.js, $(wildcard src/static/*.js))
JS_FILES_MINIFIED = $(JS_FILES:.js=.min.js)
JS_COMPRESSOR = closure-compiler
JS_COMPRESSOR_FLAGS = --language_in ECMASCRIPT5 --compilation_level SIMPLE_OPTIMIZATIONS

CSS_FILES = $(filter-out %.min.css, $(wildcard src/static/*.css))
CSS_FILES_MINIFIED = $(CSS_FILES:.css=.min.css)
CSS_COMPRESSOR = yuicompressor
CSS_COMPRESSOR_FLAGS = --charset UTF-8

minify-js: $(JS_FILES) $(JS_FILES_MINIFIED)
minify-css: $(CSS_FILES) $(CSS_FILES_MINIFIED)

%.min.js: %.js
	@echo '-> Minifying $<'
	$(JS_COMPRESSOR) $(JS_COMPRESSOR_FLAGS) $< > $@

%.min.css: %.css
	@echo '-> Minifying $<'
	$(CSS_COMPRESSOR) $(CSS_COMPRESSOR_FLAGS) $< > $@


.PHONY: minify-production
minify-production: minify-js minify-css


.PHONY: minify-dev
minify-dev: clean-minified-files symlink-static-files

clean-minified-files:
	rm -f $(JS_FILES_MINIFIED) $(CSS_FILES_MINIFIED)

symlink-static-files:
	cd src/static && rm -f *.min.js && find ./ -maxdepth 1 -iname "*.js" -exec sh -c 'ln -s $$0 `basename "$$0" .js`.min.js' '{}' \;
	cd src/static && rm -f *.min.css && find ./ -maxdepth 1 -iname "*.css" -exec sh -c 'ln -s $$0 `basename "$$0" .css`.min.css' '{}' \;



.PHONY: dependencies
dependencies: create-local-config install-python-packages static-dependencies

.PHONY: static-dependencies
static-dependencies: install-jquery install-bootstrap install-osm install-pickadate


.PHONY: create-local-config
create-local-config:
	if [ ! -f src/config_local.json ]; then echo -e '{\n    "SECRET_KEY": "",\n    "debug": false,\n    "log-level": "WARNING"\n}' > src/config_local.json; fi;

.PHONY: install-python-packages
install-python-packages:
	@( \
		if [ ! -d env ]; then virtualenv -p python3 --system-site-packages env; fi; \
		source env/bin/activate; \
		pip3 install -r requirements.txt; \
	)

.PHONY: install-jquery
install-jquery:
	mkdir -p src/static/lib/jquery/
	wget -O src/static/lib/jquery/jquery.min.js https://code.jquery.com/jquery-2.2.0.min.js

.PHONY: install-bootstrap
install-bootstrap:
	wget -P cache https://github.com/twbs/bootstrap/releases/download/v3.3.6/bootstrap-3.3.6-dist.zip
	unzip -d cache/ cache/bootstrap-3.3.6-dist.zip
	mkdir -p src/static/lib/bootstrap/{js,css,fonts}
	cp cache/bootstrap-3.3.6-dist/js/bootstrap.min.js src/static/lib/bootstrap/js/
	cp cache/bootstrap-3.3.6-dist/css/bootstrap.min.css src/static/lib/bootstrap/css/
	cp cache/bootstrap-3.3.6-dist/fonts/glyphicons-halflings-regular.* src/static/lib/bootstrap/fonts/

.PHONY: install-osm
install-osm:
	wget -P src/static/lib/osm http://openlayers.org/en/v3.12.1/css/ol.css
	wget -P src/static/lib/osm http://openlayers.org/en/v3.12.1/build/ol.js

.PHONY: install-pickadate
install-pickadate:
	wget -O cache/pickadate-3.5.6.zip http://github.com/amsul/pickadate.js/archive/3.5.6.zip
	unzip -d cache cache/pickadate-3.5.6.zip
	mkdir -p src/static/lib/pickadate
	cp cache/pickadate.js-3.5.6/lib/compressed/picker.js src/static/lib/pickadate/
	cp cache/pickadate.js-3.5.6/lib/compressed/picker.date.js src/static/lib/pickadate/
	cp cache/pickadate.js-3.5.6/lib/compressed/picker.time.js src/static/lib/pickadate/
	cp cache/pickadate.js-3.5.6/lib/compressed/themes/classic.css src/static/lib/pickadate/
	cp cache/pickadate.js-3.5.6/lib/compressed/themes/classic.date.css src/static/lib/pickadate/
	cp cache/pickadate.js-3.5.6/lib/compressed/themes/classic.time.css src/static/lib/pickadate/


clean:
	rm -f $(JS_FILES_MINIFIED) $(CSS_FILES_MINIFIED)
	rm -rf cache
	rm -rf env



.PHONY: recreate-database
recreate-database:
	echo 'DROP DATABASE IF EXISTS travel_log; CREATE DATABASE travel_log;' | psql -U travel_log_admin postgres
	cat data/data_model.sql | psql -U travel_log_admin travel_log
