import logging
from datetime import datetime

import todoist
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

logger = logging.getLogger(__name__)


class TodayTaskList(object):

    def __init__(self, extension):
        self.extension = extension

    def get_rendered_list(self):
        api_token = self.extension.api_token
        api = todoist.TodoistAPI(api_token)
        api.sync()

        tasks = []

        for item in api.items.all(filt=self.today_tasks_filter):
            logger.debug(item)
            tasks.append(
                ExtensionResultItem(icon=self.extension.get_icon(),
                                    name="%s" % (str(item["content"])),
                                    on_enter=HideWindowAction())
            )

        return tasks

    def today_tasks_filter(self, item):
        if item["checked"] == 1:
            return False

        if item["due"] is None:
            return False

        try:
            return datetime.strptime(item["due"]["date"], "%Y-%m-%d").date() <= datetime.today().date()
        except:
            pass

        try:
            return datetime.strptime(item["due"]["date"], "%Y-%m-%dT%H:%M:%SZ").date() <= datetime.today().date()
        except:
            pass

        return False
