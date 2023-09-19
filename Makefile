.PHONY: notebooks
.EXPORT_ALL_VARIABLES:

lock:
	poetry lock

install:
	poetry install
	poetry run install
	
update:
	poetry update

activate:
	poetry shell

initialize_git:
	git init

setup: initialize_git install

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache

