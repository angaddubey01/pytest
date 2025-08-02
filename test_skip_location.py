import pytest
import sys

@pytest.mark.skip(reason="unconditional skip")
def test_skip_location():
    assert 0

@pytest.mark.skipif(True, reason="conditional skip")
def test_skipif_location():
    assert 0

# This function will be used to test if the location reporting is correct
# It should always show the skip line from where it's defined, not from the _pytest/skipping.py file
def test_dynamic_skip():
    pytest.skip("dynamic skip")