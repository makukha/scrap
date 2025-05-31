from doctest import ELLIPSIS
import subprocess
import sys
from unittest import TestCase

from doctestcase import doctestcase


@doctestcase(options=ELLIPSIS)
class UsageProjectEntrypoint(TestCase):
    """
    Export project with package entrypoint

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

    >>> import scrap
    >>> scrap.get_projects()
    (('myproject', <class 'myproject.MyProject'>),)
    """

    pkg_path = 'tests/usage/myproject'
    pkg_name = 'myproject'

    def setUp(self) -> None:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', self.pkg_path]
        )

    def tearDown(self) -> None:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'uninstall', '-y', self.pkg_name]
        )
