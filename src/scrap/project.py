from importlib.metadata import entry_points


class Project:
    """
    Base project class and registry holder.
    """


def get_projects(only: type = Project) -> tuple[tuple[str, type[Project]], ...]:
    """
    Get all scrap projects, optionally filtered by superclass.
    """
    return tuple(
        (entry_point.name, project_class)
        for entry_point in entry_points(group='scrap.project')
        if issubclass((project_class := entry_point.load()), only)
    )
