.PHONY: clean test cover cover-html lint

clean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '.pyo' -exec rm --force {} +
	find . -name '__pycache__' -type d -exec rm -rf {} +
	rm .coverage || true
	rm -rf htmlcov/ || true
	rm -rf .pytest_cache/ || true

test: clean
	$(PREFIX)pytest

cover: clean
	$(PREFIX)coverage run --source basic_shopify_api/ -m pytest
	$(PREFIX)coverage report -m

cover-html: cover
	$(PREFIX)coverage html -d htmlcov

lint:
	$(PREFIX)flake8 . --count --exit-zero --statistics
