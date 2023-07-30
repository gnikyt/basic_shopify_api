from os.path import abspath, dirname, join
from setuptools import setup, find_packages

from fastshopifyapi import __version__

NAME = "fastshopifyapi"
exec(open("fastshopifyapi/__version__.py").read())
DESCRIPTION = "A sync/async REST and GraphQL client for Shopify API using HTTPX"

readme_file = join(dirname(abspath(__file__)), "README.md")
try:
    import pypandoc
    LONG_DESCRIPTION = pypandoc.convert_file(readme_file, "rst")
    LONG_DESCRIPTION_CT = "text/x-rst"
except(IOError, ImportError):
    LONG_DESCRIPTION = open(readme_file).read()
    LONG_DESCRIPTION_CT = "text/markdown"

setup(
    name=NAME,
    version=__version__.VERSION,
    description="A sync/async REST and GraphQL client for Shopify API using HTTPX",
    long_description_content_type=LONG_DESCRIPTION_CT,
    long_description=LONG_DESCRIPTION,
    author="Sokos Lee",
    author_email="sokoslee@gmail.com",
    url="https://github.com/sokoslee/FastShopifyApi",
    packages=find_packages(exclude=['tests']),
    license="MIT License",
    install_requires=[
        "httpx>=0.24.1"
    ],
    platforms="Any",
    python_requires=">=3.8",
    zip_safe=False,
    include_package_data=True,
)
