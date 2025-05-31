# scrap
<!-- docsub: begin -->
<!-- docsub: exec yq '"> " + .project.description' pyproject.toml -->
> Web testing utilities
<!-- docsub: end -->

<!-- docsub: begin -->
<!-- docsub: include docs/badges.md -->
[![license](https://img.shields.io/github/license/makukha/scrap.svg)](https://github.com/makukha/scrap/blob/main/LICENSE)
[![pypi](https://img.shields.io/pypi/v/scrap.svg#v0.0.0)](https://pypi.org/project/scrap)
[![python versions](https://img.shields.io/pypi/pyversions/scrap.svg)](https://pypi.org/project/scrap)
[![tests](https://raw.githubusercontent.com/makukha/scrap/v0.0.0/docs/img/badge/tests.svg)](https://github.com/makukha/scrap)
[![coverage](https://raw.githubusercontent.com/makukha/scrap/v0.0.0/docs/img/badge/coverage.svg)](https://github.com/makukha/scrap)
[![tested with multipython](https://img.shields.io/badge/tested_with-multipython-x)](https://github.com/makukha/multipython)
[![uses docsub](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/makukha/docsub/refs/heads/main/docs/badge/v1.json)](https://github.com/makukha/docsub)
[![mypy](https://img.shields.io/badge/type_checked-mypy-%231674b1)](http://mypy.readthedocs.io)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/ruff)
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![openssf best practices](https://www.bestpractices.dev/projects/10675/badge)](https://www.bestpractices.dev/projects/)
<!-- docsub: end -->


# Features

<!-- docsub: begin -->
<!-- docsub: include docs/features.md -->
- _Structured vector_ data structure
<!-- docsub: end -->


# Installation

```shell
$ pip install scrap
```


# Usage

<!-- docsub: begin #usage.md -->
<!-- docsub: include docs/usage.md -->
<!-- docsub: begin -->
<!-- docsub: x toc tests/test_usage.py 'Usage.*' -->
* [Export project with package entrypoint](#export-project-with-package-entrypoint)
<!-- docsub: end -->

```pycon
>>> from scrap import *
```

<!-- docsub: begin -->
<!-- docsub: x cases tests/test_usage.py 'Usage.*' -->
## Export project with package entrypoint

When project package declares entry point `scrap.project`,
```python
# myproject/myproject.py
import scrap

class MyProject(scrap.Project):
    ...
```
```toml
# myproject/pyproject.toml
[project]
name = "myproject"
version = "0.1.0"
description = ""

[project.entry-points."scrap.project"]
myproject = "myproject:MyProject"
```

it becomes registered as `scrap` project:

```pycon
>>> import scrap
>>> scrap.get_projects()
(('myproject', <class 'myproject.MyProject'>),)
```

<!-- docsub: end -->
<!-- docsub: end #usage.md -->


# Contributing

Pull requests, feature requests, and bug reports are welcome!

* [Contribution guidelines](https://github.com/makukha/scrap/blob/main/.github/CONTRIBUTING.md)


# Authors

* Michael Makukha


# See also

* [Documentation](https://github.com/makukha/scrap#readme)
* [Issues](https://github.com/makukha/scrap/issues)
* [Changelog](https://github.com/makukha/scrap/blob/main/CHANGELOG.md)
* [Security Policy](https://github.com/makukha/scrap/blob/main/.github/SECURITY.md)
* [Contribution Guidelines](https://github.com/makukha/scrap/blob/main/.github/CONTRIBUTING.md)
* [Code of Conduct](https://github.com/makukha/scrap/blob/main/.github/CODE_OF_CONDUCT.md)
* [License](https://github.com/makukha/scrap/blob/main/LICENSE)
