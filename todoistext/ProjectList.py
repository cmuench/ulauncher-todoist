import logging
import unicodedata
from datetime import datetime

import todoist
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

logger = logging.getLogger(__name__)


class ProjectList(object):

    def __init__(self, extension):
        self.extension = extension

    def get_list(self):
        api_token = self.extension.api_token
        api = todoist.TodoistAPI(api_token)
        api.sync()

        projects = []

        for project in api.projects.all(filt=self.filter_projects):
            logger.debug(project)
            projects.append(
                ExtensionResultItem(icon="images/projects.png",
                                    name=self.deEmojify(str(project["name"])),
                                    on_enter=OpenUrlAction("https://todoist.com/app?#project/%s" % project["id"]))
            )

        return projects

    def filter_projects(self, project):
        if project["is_deleted"] == 1:
            return False

        if project["is_archived"] == 1:
            return False

        return True

    def deEmojify(self, inputString):
        """ https://stackoverflow.com/questions/33404752/removing-emojis-from-a-string-in-python """

        return inputString.encode('ascii', 'ignore').decode('ascii')
