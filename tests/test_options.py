import pytest
from basic_shopify_api import Options

def test_options_version():
  opts = Options()
  opts.version = "unstable"

  assert opts.version == "unstable"

def test_options_failed_version():
  with pytest.raises(ValueError):
    opts = Options()
    opts.version = "oops"