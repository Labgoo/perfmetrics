PACKAGE=perfmetrics
TESTS_DIR=perfmetrics/tests
DOC_DIR=docs

# Use current python binary instead of system default.
COVERAGE = python $(shell which coverage)

all: default

default: clean coverage test

clean:
	find . -type f -name '*.pyc' -delete
	find . -type f -path '*/__pycache__/*' -delete
	find . -type d -empty -delete
	@rm -rf tmp_test/

test:
	python -W default setup.py nosetests --with-xunit --with-cov --verbosity=2

pylint:
	python setup.py lint --lint-rcfile=.pylintrc --lint-reports=no --lint-packages=$(PACKAGE)/

coverage:
	$(COVERAGE) erase
	$(COVERAGE) run "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py" --branch setup.py test
	$(COVERAGE) report "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"
	$(COVERAGE) html "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"

doc:
	make -C $(DOC_DIR) html