PACKAGE=perfmetrics
TESTS_DIR=perfmetrics/tests
DOC_DIR=docs

# Use current python binary instead of system default.
COVERAGE = python $(shell which coverage)

all: default

default: dev_deps deps clean pylint test

.venv:
	if [ ! -e ".venv/bin/activate_this.py" ] ; then virtualenv --clear .venv ; fi

deps: .venv
	PYTHONPATH=.venv ; . .venv/bin/activate && .venv/bin/pip install -U -r requirements.txt

dev_deps: .venv
	PYTHONPATH=.venv ; . .venv/bin/activate && .venv/bin/pip install -U -r dev_requirements.txt

clean:
	$(COVERAGE) erase
	find . -type f -name '*.pyc' -delete
	find . -type f -path '*/__pycache__/*' -delete
	find . -type d -empty -delete
	@rm -rf tmp_test/

test:
	PYTHONPATH=$PYTHONPATH:.venv:. . .venv/bin/activate && python -W default setup.py nosetests --with-xunit --verbosity=2

pylint:
	PYTHONPATH=$PYTHONPATH:.venv:. . .venv/bin/activate && python setup.py lint --lint-rcfile=.pylintrc --lint-reports=no --lint-packages=$(PACKAGE)/

coverage:
	$(COVERAGE) erase
	$(COVERAGE) run "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py" --branch setup.py test
	$(COVERAGE) report "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"
	$(COVERAGE) html "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"

deploy:
	rm -rf dist/
	PYTHONPATH=$PYTHONPATH:.venv:. . .venv/bin/activate && python setup.py sdist
	curl -F package=@dist/`ls -t1 dist/ | grep tar.gz | head -n1` $(FURY_API_URL)

doc:
	make -C $(DOC_DIR) html
