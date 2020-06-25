from os.path import abspath, dirname, join
from setuptools import setup

NAME = "basic_shopify_api"
exec(open("basic_shopify_api/__version__.py").read())
DESCRIPTION = "A sync/async REST and GraphQL client for Shopify API using HTTPX"
with open(join(dirname(abspath(__file__)), "README.md")) as readme:
    README = readme.read()

setup(
    name=NAME,
    version=VERSION,
    description="A sync/async REST and GraphQL client for Shopify API using HTTPX",
    long_description_content_type="text/markdown",
    long_description=README,
    author="osiset",
    author_email="tyler@osiset.com",
    url="https://github.com/osiset/basic_shopify_api",
    packages=["basic_shopify_api"],
    license="MIT License",
    install_requires=[
        "httpx>=0.13"
    ],
    test_suite="tests",
    tests_require=[
        "mock>=1.0.1",
    ],
    platforms="Any",
    python_requires=">=3.6",
    zip_safe=False,
    include_package_data=True,
)
