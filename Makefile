EXT_NAME:=com.github.cmuench-ulauncher-todoist
EXT_DIR:=$(shell pwd)
PYTHON?=python3
PYTHON_SITE:=$(shell $(PYTHON) -c 'import sysconfig; print(sysconfig.get_paths()["platlib"])')


.PHONY: help lint format link unlink deps ulauncher-dev dev-extension
.DEFAULT_TARGET: help

help: ## Show help menu
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

lint: ## Run Pylint
	@find . -iname "*.py" | xargs pylint

format: ## Format code using yapf
	@yapf --in-place --recursive .

link: ## Symlink the project source directory with Ulauncher extensions dir.
	ln -s ${EXT_DIR} ~/.local/share/ulauncher/extensions/${EXT_NAME}

unlink: ## Unlink extension from Ulauncher
	@rm -r ~/.local/share/ulauncher/extensions/${EXT_NAME}

deps: ## Install Python Dependencies
	@sudo pip3 install -r requirements.txt

ulauncher-dev: ## Start Ulauncher in dev mode (no extensions loaded)
	ulauncher --no-extensions --dev -v

dev-extension: ## Attach the extension to a running `make ulauncher-dev`
	VERBOSE=1 ULAUNCHER_WS_API=ws://127.0.0.1:5054/${EXT_NAME} PYTHONPATH=${PYTHON_SITE}:${EXT_DIR} ${PYTHON} ${EXT_DIR}/main.py
