import logging
from datetime import datetime

from todoist_api_python.api import TodoistAPI
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

logger = logging.getLogger(__name__)


class TodayTaskList(object):

    def __init__(self, extension):
        self.extension = extension

    def get_rendered_list(self):
        api_token = self.extension.api_token
        api = TodoistAPI(api_token)
        api_tasks = api.get_tasks(filter="today")
        print(api_tasks)

        tasks = []
        for task in api_tasks:
            logger.debug(task)
            tasks.append(
                ExtensionResultItem(icon=self.extension.get_icon(),
                                    name="%s" % str(task.content),
                                    on_enter=HideWindowAction())
            )

        return tasks
