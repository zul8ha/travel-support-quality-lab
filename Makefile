.PHONY: install run test e2e

install:
	python -m pip install -e '.[test]'

run:
	uvicorn app.main:app --reload

test:
	pytest tests/api

e2e:
	python -m playwright install chromium
	RUN_E2E=1 pytest tests/e2e
