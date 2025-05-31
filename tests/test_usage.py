import sys
from doctest import ELLIPSIS
from subprocess import check_call
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
        pass
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
    pkg = 'myproject'

    def setUp(self) -> None:
        check_call([sys.executable, '-m', 'pip', 'install', self.pkg_path])

    def tearDown(self) -> None:
        check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', self.pkg])
