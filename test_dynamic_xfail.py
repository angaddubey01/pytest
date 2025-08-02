import pytest


def test_xfail_test(request):
    mark = pytest.mark.xfail(reason="xfail added dynamically")
    request.node.add_marker(mark)
    assert 0