import gi
gi.require_version('Gdk', '3.0')
from todoistext.TodoistExtension import TodoistExtension

if __name__ == '__main__':
    TodoistExtension().run()
