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

def test_options_type():
  opts = Options()

  # Public test
  opts.mode = "public"
  assert opts.mode == "public"
  assert opts.is_public == True
  assert opts.is_private == False

  # Private test
  opts.mode = "private"
  assert opts.mode == "private"
  assert opts.is_public == False
  assert opts.is_private == True

def test_options_failed_type():
  with pytest.raises(ValueError):
    opts = Options()
    opts.mode = "oops"
