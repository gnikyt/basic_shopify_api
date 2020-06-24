.PHONY: clean test cover cover-html lint

clean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '.pyo' -exec rm --force {} +
	find . -name '__pycache__' -type d -exec rm -rf {} +
	rm .coverage || true
	rm -rf htmlcov/ || true
	rm -rf .pytest_cache/ || true

test: clean
	env/bin/pytest

cover: clean
	env/bin/coverage run --source basic_shopify_api/ -m pytest
	env/bin/coverage report -m

cover-html: cover
	env/bin/coverage html -d htmlcov

lint:
	env/bin/flake8 . --count --exit-zero --statistics
