POETRY=poetry
INTEGRATION_FOLDER=custom_components
TEST_FOLDER=tests/

ALL_FOLDERS = $(INTEGRATION_FOLDER) $(TEST_FOLDER)

lint: black mypy flake
lintfix: isort blackfix lint

mypy:
	$(POETRY) run mypy --ignore-missing-imports $(ALL_FOLDERS)

flake:
	$(POETRY) run flake8 $(ALL_FOLDERS)

black:
	$(POETRY) run black --check $(ALL_FOLDERS)

blackfix:
	$(POETRY) run black $(ALL_FOLDERS)

isort:
	$(POETRY) run isort --atomic $(ALL_FOLDERS)

test:
	$(POETRY) run pytest $(TEST_FOLDER)

coverage:
	$(POETRY) run pytest --cov-report xml --cov=custom_components.xiaomi_viomi $(TEST_FOLDER)

coverage-html:
	$(POETRY) run pytest --cov-report html --cov=custom_components.xiaomi_viomi $(TEST_FOLDER)