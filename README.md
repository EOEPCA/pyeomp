[![flake8](https://github.com/EOEPCA/pyeomp/workflows/flake8/badge.svg)](https://github.com/EOEPCA/pyeomp/actions)
[![main](https://github.com/EOEPCA/pyeomp/workflows/main/badge.svg)](https://github.com/EOEPCA/pyeomp/actions)

# pyeomp

## Overview

pyeomp is a utility to work with the EOEPCA Metadata Profile (EOMP)

## Installation

The easiest way to install pyeomp is via the Python [pip](https://pip.pypa.io)
utility:

```bash
pip3 install pyeomp
```

### Requirements
- Python 3
- [virtualenv](https://virtualenv.pypa.io)

### Dependencies
Dependencies are listed in [pyproject.toml](pyproject.toml). Dependencies
are automatically installed during pyeomp installation.

### Installing pyeomp

```bash
# setup virtualenv
python3 -m venv --system-site-packages pyeomp
cd pyeomp
source bin/activate

# clone codebase and install
git clone https://github.com/EOEPCA/pyeomp.git
cd pyeomp
pip3 install .
```

## Running

From command line:

```bash
# fetch version
pyeomp --version

# sync supporting configuration bundle (schemas, topics, etc.)
pyeomp bundle sync

# abstract test suite

# validate EOMP metadata against specification/schema (file on disk)
pyeomp record validate /path/to/file.json

# validate EOMP metadata against specification/schema (URL)
pyeomp record validate https://example.org/path/to/file.json

# adjust debugging messages (CRITICAL, ERROR, WARNING, INFO, DEBUG) to stdout
pyeomp record validate https://example.org/path/to/file.json --verbosity DEBUG

# write results to logfile
pyeomp record validate https://example.org/path/to/file.json --verbosity DEBUG --logfile /tmp/foo.txt
```

## Using the API
```pycon
>>> # test a file on disk
>>> import json
>>> from pyeomp.eomp.ets import EOMPTestSuite
>>> from pyeomp.errors import TestSuiteError
>>> with open('/path/to/file.json') as fh:
...     data = json.load(fh)
>>> # test ETS
>>> ts = EOMPTestSuite(data)
>>> ts.run_tests()
>>> ts.raise_for_status()  # raises pyeomp.errors.TestSuiteError on exception with list of errors captured in .errors property
>>> # test a URL
>>> from urllib2 import urlopen
>>> from StringIO import StringIO
>>> content = StringIO(urlopen('https://....').read())
>>> data = json.loads(content)
>>> ts = EOMPTestSuite(data)
>>> ts.run_tests()
>>> ts.raise_for_status()  # raises pyeomp.errors.TestSuiteError on exception with list of errors captured in .errors property
```

## Development

```bash
python3 -m venv pyeomp
cd pyeomp
source bin/activate
git clone https://github.com/EOEPCA/pyeomp.git
cd pyeomp
pip3 install .
pip3 install ".[dev]"
pip3 install ".[test]"
```

### Running tests

```bash
pytest
```

## Releasing

```bash
# create release (x.y.z is the release version)
vi pyproject.toml  # update [project]/version
git commit -am 'update release version x.y.z'
git push origin master
git tag -a x.y.z -m 'tagging release version x.y.z'
git push --tags

# upload to PyPI
rm -fr build dist *.egg-info
python3 -m build
twine upload dist/*

# publish release on GitHub (https://github.com/EOEPCA/pyeomp/releases/new)

# bump version back to dev
vi pyproject.toml  # update [project]/version
git commit -am 'back to dev'
git push origin master
```

## Code Conventions

[PEP8](https://www.python.org/dev/peps/pep-0008)

## Issues

Issues are managed at https://github.com/EOEPCA/pyeomp/issues

## Contact

* [Angelos Tzotsos](https://github.com/kalxas)
