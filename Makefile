PROJECT_NAME = leumi-mail
VIRTUALENV = .virtualenv
BUILD_DIR = .virtualenvs/$(shell uname -s)-$(shell uname -r)-$(shell arch)
PYTHON = ${VIRTUALENV}/bin/python

# Dependency-related.
WHEEL_CACHE = ${HOME}/.cache/wheel/$(shell uname -s)-$(shell uname -r)-$(shell arch)
BUILD_WHEELS = ${VIRTUALENV}/bin/pip wheel --wheel-dir ${WHEEL_CACHE} --find-links ${WHEEL_CACHE}
INSTALL_WHEELS = ${VIRTUALENV}/bin/pip install --use-wheel --find-links ${WHEEL_CACHE}
REQS = requirements.txt

virtualenv:
	virtualenv ${BUILD_DIR}

# If no symlink or the symlink is different than the current OS, create the symlink.
	if [ ! -h ${VIRTUALENV} ] || [ "$(shell readlink ${VIRTUALENV})" != "${BUILD_DIR}" ] ; then \
        	ln -sf ${BUILD_DIR} ${VIRTUALENV}; \
    	fi
pip:
	${VIRTUALENV}/bin/pip install --upgrade "pip>=6.0.6" wheel

reqs:
	$(foreach reqs,${REQS}, ${BUILD_WHEELS} -r ${reqs}; ${INSTALL_WHEELS} -r ${reqs};)


quickstart: virtualenv pip reqs

clean:
	# Delete all .pyc and .pyo files.
	find . \( -name "*~" -o -name "*.py[co]" -o -name ".#*" -o -name "#*#" \) -exec rm '{}' +
