.PHONY: clean test cover cover-html lint build verify publish docs release

clean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '.pyo' -exec rm --force {} +
	find . -name '__pycache__' -type d -exec rm -rf {} +
	find . -name '*.egg-info' -type d -exec rm -rf {} +
	find . -name 'dist' -type d -exec rm -rf {} +
	find . -name 'build' -type d -exec rm -rf {} +
	find . -name 'docs' -type d -exec rm -rf {} +
	rm .coverage || true
	rm -rf htmlcov/ || true
	rm -rf .pytest_cache/ || true

test: clean
	$(PREFIX)pytest

cover: clean
	$(PREFIX)coverage run --source fastshopifyapi/ -m pytest
	$(PREFIX)coverage report -m

cover-html: cover
	$(PREFIX)coverage html -d htmlcov

lint:
	$(PREFIX)flake8 . --count --exit-zero --statistics

build: clean
	python setup.py sdist bdist_wheel

verify:
	$(PREFIX)twine check dist/*

publish:
	$(PREFIX)twine upload dist/*

docs: clean
	$(PREFIX)pdoc --output-dir docs fastshopifyapi
	mv docs/fastshopifyapi/* docs/
	rm -rf docs/fastshopifyapi/

release: build verify docs publish
