;; GNU Guix manifest for OpenAlex Python client development environment
;;
;; Usage: guix shell -m manifest.scm
;;
;; For a pure environment: guix shell --pure -m manifest.scm
;; For a containerized environment: guix shell --container -m manifest.scm
(specifications->manifest
 '(;; Core development tools
   "git"
   "python"
   "poetry"
   ;; Core Python dependencies (from pyproject.toml)
   "python-httpx"
   "python-pydantic"
   "python-structlog"
   "python-rich"
   "python-dateutil"
   "python-orjson"
   "python-typing-extensions"
   "python-cachetools"
   "python-xxhash"
   ;; Testing framework and tools
   "python-pytest"
   "python-pytest-asyncio"
   "python-pytest-cov"
   "python-pytest-httpx"
   "python-pytest-examples"
   "python-pytest-benchmark"
   ;; Code quality and linting
   "python-ruff"
   "node-pyright"
   "pre-commit"
   ;; Development tools
   "python-ipython"
   ;; Documentation tools
   "python-sphinx"
   "python-sphinx-rtd-theme"
   "python-sphinx-autodoc-typehints"
   "python-myst-parser"
))
