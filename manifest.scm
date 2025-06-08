;; GNU Guix manifest for openalex-python development environment

(specifications->manifest
 '(
   ;; Version control and shell
   "git"
   "bash"
   "make"
   
   ;; Python and package management
   "python"
   "python-pip"
   "python-virtualenv"
   "poetry"
   
   ;; Runtime dependencies
   "python-certifi"
   "python-six"
   "python-dateutil"
   "python-setuptools"
   "python-urllib3"
   
   ;; Testing framework
   "python-pytest"
   "python-pytest-cov"
   "python-pytest-xdist"
   "python-coverage"
   "python-nose"
   
   ;; Code quality and linting
   "python-mypy"
   "python-ruff"
   "python-black"
   "python-isort"
   "python-flake8"
   "pre-commit"
   
   ;; Development utilities
   "python-pluggy"
   "python-py"
   "python-tox"
   
   ;; Documentation
   "python-sphinx"
   "python-sphinx-autodoc-typehints"
   
   ;; Additional tools
   "python-wheel"
   "python-setuptools"
   "python-twine"
   ))