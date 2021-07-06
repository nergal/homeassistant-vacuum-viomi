POETRY=poetry
INTEGRATION_FOLDER=custom_components/xiaomi_viomi
TEST_FOLDER=tests/

lint: black mypy flake
lintfix: blackfix lint

mypy:
	$(POETRY) run mypy --ignore-missing-imports $(INTEGRATION_FOLDER)

flake:
	$(POETRY) run flake8 $(INTEGRATION_FOLDER)

black:
	$(POETRY) run black --check $(INTEGRATION_FOLDER)

blackfix:
	$(POETRY) run black $(INTEGRATION_FOLDER)

test:
	$(POETRY) run pytest $(TEST_FOLDER)

coverage:
	$(POETRY) run pytest --cov-report term $(TEST_FOLDER)