import logging
import os
import subprocess

import gi
import todoist
from ulauncher.api.shared.action.ExtensionCustomAction import \
    ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import \
    RenderResultListAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')

from gi.repository import Notify
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.event import (ItemEnterEvent, KeywordQueryEvent,
                                        PreferencesEvent,
                                        PreferencesUpdateEvent)

from .ItemEnterEventListener import ItemEnterEventListener
from .KeywordQueryEventListener import KeywordQueryEventListener
from .PreferencesEventListener import (PreferencesEventListener,
                                       PreferencesUpdateEventListener)

logger = logging.getLogger(__name__)

class TodoistExtension(Extension):
    SOUND_FILE = "/usr/share/sounds/freedesktop/stereo/message.oga"
    ICON_FILE = 'images/icon.png'

    keyword = None
    api_token = None

    def __init__(self):
        super(TodoistExtension, self).__init__()
        self.icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.ICON_FILE)
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener(self.ICON_FILE))
        self.subscribe(ItemEnterEvent, ItemEnterEventListener(self.ICON_FILE))
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())

    def create_task(self, message):
        api = todoist.TodoistAPI(self.api_token)
        new_item = api.quick.add(message)
        api.commit()
        self.show_notification('Task %i created' % new_item["id"], make_sound=True)

    def get_icon(self):
        return self.ICON_FILE

    def show_notification(self, message, make_sound: object = True):
        """

        :rtype: object
        :param message: Message to display
        :param make_sound: Play a "beep" sound
        """
        logger.debug('Show notification: %s' % message)
        Notify.init("TodoistExtension")
        Notify.Notification.new("Created Todoist Task", message, self.icon_path).show()
        if make_sound:
            subprocess.call(("paplay", self.SOUND_FILE))

    def show_menu(self):
        keyword = self.keyword

        items = []

        items.append(
            ExtensionResultItem(name="Create Task",
                                description="Create a new task",
                                icon="images/create.png",
                                on_enter=SetUserQueryAction("%s create " % keyword))
        )

        items.append(
            ExtensionResultItem(name="Today Tasks",
                                description="Today task list",
                                icon="images/today.png",
                                on_enter=ExtensionCustomAction({"action": "today"}, keep_app_open=True))
        )

        items.append(
            ExtensionResultItem(name="Projects",
                                description="Project list",
                                icon="images/projects.png",
                                on_enter=ExtensionCustomAction({"action": "projects"}, keep_app_open=True))
        )

        return RenderResultListAction(items)
