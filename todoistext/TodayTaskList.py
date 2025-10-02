import logging
from datetime import datetime, timezone
from typing import Any, List

from todoist_api_python.api import TodoistAPI
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

logger = logging.getLogger(__name__)


class TodayTaskList(object):

    def __init__(self, extension):
        self.extension = extension

    def get_rendered_list(self):
        api_token = self.extension.api_token
        api = TodoistAPI(api_token)
        api_tasks = self._fetch_today_tasks(api)

        tasks = []
        for task in api_tasks:
            logger.debug(task)
            task_content = self._extract_task_content(task)
            if not task_content:
                continue
            task_id = self._extract_task_id(task)
            on_enter_action = OpenUrlAction(f"https://todoist.com/app/task/{task_id}") if task_id else HideWindowAction()
            tasks.append(
                ExtensionResultItem(icon=self.extension.get_icon(),
                                    name=str(task_content),
                                    on_enter=on_enter_action)
            )

        return tasks

    def _fetch_today_tasks(self, api):
        """Fetch tasks due today while supporting multiple SDK signatures."""
        for kwargs in ({"filter": "today"}, {"filter_": "today"}, {"filter_query": "today"}):
            try:
                return self._materialize_tasks(api.get_tasks(**kwargs))
            except TypeError:
                logger.debug("Todoist API get_tasks signature rejected kwargs: %s", kwargs)
                continue

        try:
            tasks = self._materialize_tasks(api.get_tasks())
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to fetch tasks from Todoist API: %s", exc)
            return []

        today_tasks = [task for task in tasks if self._is_due_today(task)]
        if tasks and not today_tasks:
            logger.debug("Todoist API fallback returned %d tasks but none matched today's filter", len(tasks))
        return today_tasks

    def _extract_task_content(self, task):
        """Return the task title regardless of payload shape."""
        content = getattr(task, "content", None)

        if hasattr(content, "text"):
            content = content.text
        elif hasattr(content, "name") and not isinstance(content, str):
            content = content.name
        elif isinstance(content, dict):
            content = content.get("text") or content.get("name")

        if not content and isinstance(task, dict):
            nested_task = task.get("task")
            if isinstance(nested_task, dict):
                content = nested_task.get("content")
                if isinstance(content, dict):
                    content = content.get("text") or content.get("name")

            if not content:
                content = task.get("content")
                if hasattr(content, "text"):
                    content = content.text
                elif hasattr(content, "name") and not isinstance(content, str):
                    content = content.name
                elif isinstance(content, dict):
                    content = content.get("text") or content.get("name")

        if not content and hasattr(task, "task"):
            nested_task = getattr(task, "task", None)
            if nested_task is not None:
                return self._extract_task_content(nested_task)

        if isinstance(content, (list, tuple)):
            content = " ".join(str(part) for part in content if part)

        if content is not None and not isinstance(content, str):
            content = str(content)

        return content

    def _extract_task_id(self, task) -> str:
        task_id = getattr(task, "id", None)
        if task_id:
            return str(task_id)

        if isinstance(task, dict):
            task_id = task.get("id") or task.get("task_id")
            if task_id:
                return str(task_id)

            nested_task = task.get("task")
            if nested_task is not None:
                nested_id = self._extract_task_id(nested_task)
                if nested_id:
                    return nested_id

        if hasattr(task, "task"):
            nested_task = getattr(task, "task", None)
            if nested_task is not None:
                nested_id = self._extract_task_id(nested_task)
                if nested_id:
                    return nested_id

        return ""

    def _is_due_today(self, task) -> bool:
        today = datetime.now(timezone.utc).date()

        def _get(attr, key):
            value = getattr(attr, key, None)
            if value is None and isinstance(attr, dict):
                value = attr.get(key)
            return value

        due = getattr(task, "due", None)
        if due is None and isinstance(task, dict):
            due = task.get("due")

        if not due:
            return False

        datetime_value = _get(due, "datetime")
        if datetime_value:
            normalized = datetime_value.replace("Z", "+00:00") if isinstance(datetime_value, str) else datetime_value
            try:
                due_dt = datetime.fromisoformat(normalized)
            except ValueError:
                due_dt = None
            if due_dt is not None:
                if due_dt.tzinfo is None:
                    due_dt = due_dt.replace(tzinfo=timezone.utc)
                return due_dt.astimezone(timezone.utc).date() == today

        date_value = _get(due, "date")
        if date_value:
            try:
                due_date = datetime.fromisoformat(str(date_value)).date()
            except ValueError:
                return False
            return due_date == today

        return False

    def _materialize_tasks(self, tasks: Any) -> List[Any]:
        if tasks is None:
            return []

        if isinstance(tasks, list):
            flattened: List[Any] = []
            for item in tasks:
                if isinstance(item, list):
                    flattened.extend(item)
                else:
                    flattened.append(item)
            return flattened

        if hasattr(tasks, "items") and isinstance(getattr(tasks, "items"), list):
            return getattr(tasks, "items")

        if hasattr(tasks, "__iter__") and not isinstance(tasks, (str, bytes)):
            flattened: List[Any] = []
            for page in tasks:
                if isinstance(page, list):
                    flattened.extend(page)
                else:
                    flattened.append(page)
            return flattened

        logger.debug("Todoist API get_tasks returned non-iterable payload: %s", type(tasks))
        return [tasks]
