import logging
from typing import Any, Iterable, List

from todoist_api_python.api import TodoistAPI
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

logger = logging.getLogger(__name__)


class ProjectList(object):

    class _ProjectWrapper(object):
        """Small helper wrapper to normalize project data from the API."""

        __slots__ = ("id", "name", "is_deleted", "is_archived")

        def __init__(self, project: Any):
            if hasattr(project, "id") and hasattr(project, "name"):
                self.id = getattr(project, "id", None)
                self.name = self._normalize_name(getattr(project, "name", None))
                self.is_deleted = bool(getattr(project, "is_deleted", False))
                self.is_archived = bool(getattr(project, "is_archived", False))
            elif isinstance(project, dict):
                self.id = project.get("id")
                self.name = self._normalize_name(project.get("name"))
                self.is_deleted = bool(project.get("is_deleted", False))
                self.is_archived = bool(project.get("is_archived", False))
            elif isinstance(project, (list, tuple)):
                self.id = project[0] if len(project) > 0 else None
                self.name = self._normalize_name(project[1] if len(project) > 1 else None)
                self.is_deleted = False
                self.is_archived = False
            else:
                self.id = None
                self.name = None
                self.is_deleted = False
                self.is_archived = False

        @classmethod
        def _normalize_name(cls, raw_name: Any) -> Any:
            if raw_name is None:
                return None

            if isinstance(raw_name, str):
                return raw_name

            if hasattr(raw_name, "text"):
                return raw_name.text

            if hasattr(raw_name, "name") and not isinstance(raw_name, (str, bytes)):
                nested = getattr(raw_name, "name")
                return cls._normalize_name(nested)

            if isinstance(raw_name, dict):
                for key in ("name", "text", "title", "content"):
                    value = raw_name.get(key)
                    if value:
                        return cls._normalize_name(value)

            if isinstance(raw_name, (list, tuple)):
                return " ".join(str(part) for part in raw_name if part)

            return str(raw_name)

    def __init__(self, extension):
        self.extension = extension

    def get_list(self):
        api_token = self.extension.api_token
        api = TodoistAPI(api_token)

        raw_projects = self._materialize_projects(api.get_projects())
        normalized_projects: List[ProjectList._ProjectWrapper] = []

        for project in self._normalize_projects(raw_projects):
            if project and self._filter_project(project):
                normalized_projects.append(project)

        return normalized_projects

    def get_rendered_list(self):
        projects = self.get_list()

        rendered_projects = []
        for project in projects:
            rendered_projects.append(
                ExtensionResultItem(icon="images/projects.png",
                                    name=self.deEmojify(str(project.name)),
                                    on_enter=OpenUrlAction("https://todoist.com/app?#project/%s" % project.id)))

        return rendered_projects

    def _normalize_projects(self, projects: Iterable[Any]) -> Iterable[_ProjectWrapper]:
        for project in projects:
            wrapped = self._ProjectWrapper(project)
            if not wrapped.id or not wrapped.name:
                logger.warning("Skipping Todoist project with unexpected payload: %s", project)
                continue
            yield wrapped

    def _materialize_projects(self, projects: Any) -> List[Any]:
        if projects is None:
            return []

        if isinstance(projects, list):
            flattened: List[Any] = []
            for item in projects:
                if isinstance(item, list):
                    flattened.extend(item)
                else:
                    flattened.append(item)
            return flattened

        if hasattr(projects, "items") and isinstance(getattr(projects, "items"), list):
            return getattr(projects, "items")

        if hasattr(projects, "__iter__") and not isinstance(projects, (str, bytes)):
            flattened: List[Any] = []
            for page in projects:
                if isinstance(page, list):
                    flattened.extend(page)
                else:
                    flattened.append(page)
            return flattened

        logger.debug("Todoist API get_projects returned non-iterable payload: %s", type(projects))
        return [projects]

    def _filter_project(self, project: _ProjectWrapper) -> bool:
        if project.is_deleted:
            return False

        if project.is_archived:
            return False

        return True

    def deEmojify(self, inputString):
        """ https://stackoverflow.com/questions/33404752/removing-emojis-from-a-string-in-python """

        return inputString.encode('ascii', 'ignore').decode('ascii')
