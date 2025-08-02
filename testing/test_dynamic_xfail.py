import pytest


def test_dynamic_xfail_during_test(testdir):
    """Test that xfail markers added during the test via request.node.add_marker work."""
    testdir.makepyfile(
        """
        import pytest
        
        def test_xfail_test(request):
            mark = pytest.mark.xfail(reason="xfail added dynamically")
            request.node.add_marker(mark)
            assert 0
        """
    )
    result = testdir.runpytest("-v")
    result.stdout.fnmatch_lines(["*XFAIL*test_xfail_test*", "*xfail added dynamically*"])
    assert result.ret == 0


def test_dynamic_xfail_strict(testdir):
    """Test that dynamically added xfail markers honor the strict option."""
    testdir.makepyfile(
        """
        import pytest
        
        def test_xfail_pass_strict(request):
            mark = pytest.mark.xfail(reason="should fail because strict", strict=True)
            request.node.add_marker(mark)
            assert True  # test passes, but marked xfail with strict=True, so it should fail
        """
    )
    result = testdir.runpytest("-v")
    result.stdout.fnmatch_lines(["*FAILED*test_xfail_pass_strict*", "*[XPASS(strict)]*"])
    assert result.ret == 1


def test_multiple_dynamic_xfail(testdir):
    """Test that multiple xfail markers can be added dynamically."""
    testdir.makepyfile(
        """
        import pytest
        
        def test_multiple_xfail_markers(request):
            # First marker would normally cause an xfail
            mark1 = pytest.mark.xfail(reason="first xfail marker")
            request.node.add_marker(mark1)
            
            # Second marker would make it strict
            mark2 = pytest.mark.xfail(reason="second strict marker", strict=True)
            request.node.add_marker(mark2)
            
            assert True  # This will be a FAILED XPASS(strict)
        """
    )
    result = testdir.runpytest("-v")
    # The last marker should take precedence for the strict behavior
    result.stdout.fnmatch_lines(["*FAILED*test_multiple_xfail_markers*", "*[XPASS(strict)]*"])
    assert result.ret == 1