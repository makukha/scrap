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
