import logging

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.RenderResultListAction import \
    RenderResultListAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

from todoistext.ProjectList import ProjectList
from todoistext.TodayTaskList import TodayTaskList

logger = logging.getLogger(__name__)


class ItemEnterEventListener(EventListener):
    def __init__(self, icon_file):
        self.icon_file = icon_file

    def on_event(self, event, extension):
        data = event.get_data()

        logger.debug(data)

        if data['action'] == "create":
            extension.create_task(data["task"], data["project_id"])

        if data['action'] == "today":
            return RenderResultListAction(TodayTaskList(extension).get_rendered_list())

        if data['action'] == "projects":
            return RenderResultListAction(ProjectList(extension).get_rendered_list())

        return self.get_action_to_render(name="Incorrect request",
                                         description="todo create my task")

    def get_action_to_render(self, name, description, on_enter=None):
        item = ExtensionResultItem(name=name,
                                   description=description,
                                   icon=self.icon_file,
                                   on_enter=on_enter or DoNothingAction())

        return RenderResultListAction([item])
