import logging
import re
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

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

        create = re.findall(r"^create\s(.*)?$", query, re.IGNORECASE)

        try:
            if create:
                logger.debug(create)
                return RenderResultListAction([
                    ExtensionResultItem(
                        icon=extension.get_icon(),
                        name='Create task %s' % create[0],
                        description="Create a new task",
                        highlightable=False,
                        on_enter=ExtensionCustomAction({"action": "create", "query": create[0]}, keep_app_open=False))
                ])

        except:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon=extension.get_icon(),
                    name='An error ocurred',
                    description="",
                    highlightable=False,
                    on_enter=HideWindowAction())
            ])
