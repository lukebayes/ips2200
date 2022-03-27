###########################################################
# IPS2200 build script
###########################################################

# Operating System (darwin or linux)
PLATFORM:=$(shell uname | tr A-Z a-z)
ARCH=x64
PROJECT_ROOT=$(shell git rev-parse --show-toplevel)

# NOTE: Get when-changed.py into your path
WHEN_CHG=`which when-changed.py`

#NOTE: Get python3 into your path
PYTHON=`which python3`

SRC_FILES=`find . -name "ips2200/*.py"`
TEST_FILES=`find . -name "tests/*_test.py"`
ALL_FILES=`find . -name "*.py"`
PYCACHE_FILES=`find . -name "__pycache__"`


.PHONY: test test-w build lint clean

clean:
	rm -rf $(PYCACHE_FILES)
	

test: Makefile
	pytest -s $(TEST_FILES)
	# pytest -k set_address -s $(TEST_FILES)
	# $(PYTHON) -m unittest discover -s tests -p '*_test.py'

test-w:
	$(WHEN_CHG) $(ALL_FILES) -c "make test"
