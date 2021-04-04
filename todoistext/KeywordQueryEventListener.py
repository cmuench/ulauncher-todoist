import logging
import re

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.action.ExtensionCustomAction import \
    ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import \
    RenderResultListAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

from todoistext.ProjectList import ProjectList

logger = logging.getLogger(__name__)


class KeywordQueryEventListener(EventListener):
    """ Handles Keyboard input """

    def __init__(self, icon_file):
        self.icon_file = icon_file

    def on_event(self, event, extension):
        query = event.get_argument() or ""

        if not query:
            return extension.show_menu()

        logger.debug(query)

        task_with_project = re.findall(r"^create\s(.*)?\s#(\S*)?$", query, re.IGNORECASE)
        if task_with_project:
            task = task_with_project[0][0]
            project = task_with_project[0][1]
            logger.debug(project)

            # get the projects which fit the input
            all_projects = ProjectList(extension).get_list()
            filtered_projects = [p for p in all_projects if str(project).lower() in str(p["name"]).lower()]
            # TODO: HANDLE PROJECT NAMES WITH WHITESPACES
            # TODO: CACHE PROJECTS
            return RenderResultListAction([ExtensionResultItem(
                        icon=extension.get_icon(),
                        name=p["name"],
                        description="Do you want to add the task to this project?",
                        highlightable=False,
                        on_enter=SetUserQueryAction(f"{extension.keyword} create {task} #\"{p['name']}\"")
            ) for p in filtered_projects])
        
        task_without_project = re.findall(r"^create\s(.*)?$", query, re.IGNORECASE)
        if task_without_project:
            task = task_without_project[0]
            logger.debug(task)
            return RenderResultListAction([
                ExtensionResultItem(
                    icon=extension.get_icon(),
                    name=f"Create task {task}",
                    description="Create a new task",
                    highlightable=False,
                    on_enter=ExtensionCustomAction({"action": "create", "query": task}, keep_app_open=False))
            ])
