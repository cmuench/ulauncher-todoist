import logging
import os
import subprocess
from typing import Any
from uuid import uuid4

import gi
import requests
from todoist_api_python.api import TodoistAPI
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

    def create_task(self, content, project_id=None):
        api = TodoistAPI(self.api_token)
        result = self._quick_add_task(api, content)
        task = self._extract_task(result)

        task_id = getattr(task, "id", None)
        if project_id is not None and task_id:
            self.move_task(task_id=task_id, project_id=project_id)

        display_id = task_id or getattr(task, "uuid", None) or ""
        self.show_notification(f"Task {display_id} created", make_sound=True)

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

    def move_task(self, task_id: str, project_id: str) -> bool:
        """
        https://github.com/Doist/todoist-api-python/issues/8#issuecomment-1344860782
        """
        body = {
            "commands": [
                {
                    "type": "item_move",
                    "args": {"id": task_id, "project_id": project_id},
                    "uuid": uuid4().hex,
                },
            ],
        }
        response = requests.post(
            "https://api.todoist.com/sync/v9/sync",
            headers={"Authorization": f"Bearer {self.api_token}"},
            json=body,
        )
        return response.ok

    def _extract_task(self, task_result: Any) -> Any:
        """Normalize quick_add_task responses across todoist-api-python versions."""
        if hasattr(task_result, "task"):
            return task_result.task

        if isinstance(task_result, dict):
            return task_result

        if isinstance(task_result, (list, tuple)) and task_result:
            return task_result[0]

        return task_result

    def _quick_add_task(self, api: TodoistAPI, content: str) -> Any:
        if hasattr(api, "add_task_quick"):
            try:
                return api.add_task_quick(content)
            except TypeError:
                logger.debug("Todoist API add_task_quick signature mismatch, falling back", exc_info=True)

        if hasattr(api, "quick_add_task"):
            try:
                return api.quick_add_task(content)
            except TypeError:
                logger.debug("Todoist API quick_add_task signature mismatch, falling back", exc_info=True)

        return api.add_task(content)

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
