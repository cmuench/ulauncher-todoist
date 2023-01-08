import logging

from todoist_api_python.api import TodoistAPI
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

logger = logging.getLogger(__name__)


class ProjectList(object):

    def __init__(self, extension):
        self.extension = extension

    def get_list(self):
        api_token = self.extension.api_token
        api = TodoistAPI(api_token)

        return api.get_projects()

    def get_rendered_list(self):
        projects = self.get_list()

        rendered_projects = []
        for project in projects:
            rendered_projects.append(
                ExtensionResultItem(icon="images/projects.png",
                                    name=self.deEmojify(str(project.name)),
                                    on_enter=OpenUrlAction("https://todoist.com/app?#project/%s" % project.id)))

        return rendered_projects


    def filter_projects(self, project):
        if project["is_deleted"] == 1:
            return False

        if project["is_archived"] == 1:
            return False

        return True

    def deEmojify(self, inputString):
        """ https://stackoverflow.com/questions/33404752/removing-emojis-from-a-string-in-python """

        return inputString.encode('ascii', 'ignore').decode('ascii')
