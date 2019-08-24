# ulauncher-todoist-ext


> Manage your Docker containers from Ulauncher

## Demo

![Demo](demo.gif)

## Features

- Lists all Todoist projects
- Add a new Task to Inbox
- Show today task list

## Requirements

- [Ulauncher 5](https://ulauncher.io)
- [Python](https://www.python.org) >= 3

This extension also needs the [todoist-python](https://github.com/Doist/todoist-python) pacakge.

You can install them in one command using: `pip3 install todoist-python`

## Install

Open ulauncher preferences window -> extensions -> add extension and paste the following url:

```
https://github.com/cmuench/ulauncher-todoist-ext
```

Set api token in configuration tab "extensions -> Todoist -> API Token".
You can find your API Token here: [https://todoist.com/prefs/integrations](https://todoist.com/prefs/integrations)


## Usage

On Ulauncher, use "todo" as the default keyword to trigger the extension. By default it will show a list of running containers.

## Development

```
git clone https://github.com/cmuench/ulauncher-todoist
make link
```

The `make link` command will symlink the cloned repo into the appropriate location on the ulauncher extensions folder.

To see your changes, stop ulauncher and run it from the command line with: `ulauncher -v`.

## Contributing

Contributions, issues and Features requests are welcome.

## License

Copyright @ 2019 [Christian Münch](https://github.com/cmuench)

This project is [MIT](LICENSE) Licensed.
