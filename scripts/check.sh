#!/usr/bin/bash

APP_DIR=${DIR}/project/project

alias pylint='DJANGO_SETTINGS_MODULE=project.settings.development pylint -j 0 --output-format=colorized --load-plugins pylint_django ${APP_DIR}'
alias black='black ${APP_DIR}'
alias isort='isort ${APP_DIR}'
alias docs='sphinx-apidoc -o ${DIR}/docs ${DIR}/project \
	${DIR}/**/migrations \
	${DIR}/project/settings/production.py \
	${DIR}/project/storage_backend.py \
	${DIR}/**/oscar-code \
	${DIR}/**/oscar-template \
	${DIR}/**/oscar-templatetags \
	'
alias pytest='DJANGO_SETTINGS_MODULE=project.settings.test pytest ${APP_DIR}'

# check everything before user can push to remote
function check {
	cd $DIR # cd to root directory for the pyproject.toml

	### FORMATTING ###

	# Black formatting
	black

	# Isort imports
	isort

	### CHECK SINTAX ###

	# Pylint check
	pylint

	### CHECK TESTS ###

	# Django test
	python3 ${DIR}/project/manage.py test

	# Pytest
	pytest

	cd - # cd back from root

	### BUILD DOCS ###

	# Sphynx
	docs

	cd $DIR/docs
	make doctest # sphinx-build -b doctest source/ build/
	make clean html # sphinx-build -b html source/ build/
	cd -

	### RUN SERVER ###
	runserver

}
