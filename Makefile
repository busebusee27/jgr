PYTHON := python3

all: phase0 phase1 phase2

phase0:
	$(PYTHON) -m doctest scheme_reader.py

phase1: env_test $(patsubst %.scm,%.test,$(wildcard phase1*tests.scm))

env_test:
	python3 -m doctest scheme_core.py

phase2: $(patsubst %.scm,%.test,$(wildcard phase2*tests.scm))

phase3: $(patsubst %.scm,%.test,$(wildcard phase3*tests.scm))

phase2_%: phase2_%_tests.test
	@: # null command

%.test:
	$(PYTHON) scheme_test.py $(@:.test=.scm)

STYLE_SOURCES := $(wildcard *.py)
PYLINT_FLAGS :=

style: style-pycode style-pydoc style-pylint

style-pycode:
	pycodestyle $(STYLE_SOURCES)

style-pydoc:
	pydocstyle $(STYLE_SOURCES)

style-pylint:
	pylint $(PYLINT_FLAGS) $(STYLE_SOURCES)
