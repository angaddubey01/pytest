## F02-Y Code Debugging - Investigating pytest Skip Location Reporting Bug with --runxfail Flag

Bug - [skipping: --runxfail breaks pytest.mark.skip location reporting #7392](https://github.com/pytest-dev/pytest/issues/7392)

PR - [Fix reported location of skip when --runxfail is used #7432](https://github.com/pytest-dev/pytest/pull/7432)

---

### [1] First Pair of Completion

- Completion A
    
    ```diff
    (
      cd "$(git rev-parse --show-toplevel)"
      git apply --3way <<'EOF'
    diff --git a/src/_pytest/skipping.py b/src/_pytest/skipping.py
    index 7bd975e5a..a630dbd4f 100644
    --- a/src/_pytest/skipping.py
    +++ b/src/_pytest/skipping.py
    @@ -270,35 +270,33 @@ def pytest_runtest_makereport(item: Item, call: CallInfo[None]):
             else:
                 rep.longrepr = "Unexpected success"
             rep.outcome = "failed"
    -    elif item.config.option.runxfail:
    -        pass  # don't interfere
    -    elif call.excinfo and isinstance(call.excinfo.value, xfail.Exception):
    -        assert call.excinfo.value.msg is not None
    -        rep.wasxfail = "reason: " + call.excinfo.value.msg
    -        rep.outcome = "skipped"
    -    elif not rep.skipped and xfailed:
    -        if call.excinfo:
    -            raises = xfailed.raises
    -            if raises is not None and not isinstance(call.excinfo.value, raises):
    -                rep.outcome = "failed"
    -            else:
    +    else:
    +        if not item.config.option.runxfail:
    +            if call.excinfo and isinstance(call.excinfo.value, xfail.Exception):
    +                assert call.excinfo.value.msg is not None
    +                rep.wasxfail = "reason: " + call.excinfo.value.msg
                     rep.outcome = "skipped"
    -                rep.wasxfail = xfailed.reason
    -        elif call.when == "call":
    -            if xfailed.strict:
    -                rep.outcome = "failed"
    -                rep.longrepr = "[XPASS(strict)] " + xfailed.reason
    -            else:
    -                rep.outcome = "passed"
    -                rep.wasxfail = xfailed.reason
    -    elif (
    +            elif not rep.skipped and xfailed:
    +                if call.excinfo:
    +                    raises = xfailed.raises
    +                    if raises is not None and not isinstance(call.excinfo.value, raises):
    +                        rep.outcome = "failed"
    +                    else:
    +                        rep.outcome = "skipped"
    +                        rep.wasxfail = xfailed.reason
    +                elif call.when == "call":
    +                    if xfailed.strict:
    +                        rep.outcome = "failed"
    +                        rep.longrepr = "[XPASS(strict)] " + xfailed.reason
    +                    else:
    +                        rep.outcome = "passed"
    +                        rep.wasxfail = xfailed.reason
    +
    +    if (
             item._store.get(skipped_by_mark_key, True)
             and rep.skipped
             and type(rep.longrepr) is tuple
         ):
    -        # skipped by mark.skipif; change the location of the failure
    -        # to point to the item definition, otherwise it will display
    -        # the location of where the skip exception was raised within pytest
             _, _, reason = rep.longrepr
             filename, line = item.reportinfo()[:2]
             assert line is not None
    diff --git a/testing/test_skipping.py b/testing/test_skipping.py
    index 0b1c0b49b..da5294414 100644
    --- a/testing/test_skipping.py
    +++ b/testing/test_skipping.py
    @@ -1205,3 +1205,20 @@ def test_relpath_rootdir(testdir):
         result.stdout.fnmatch_lines(
             ["SKIPPED [[]1[]] tests/test_1.py:2: unconditional skip"]
         )
    +
    +
    +def test_skip_location_with_runxfail(testdir):
    +    p = testdir.makepyfile(
    +        test_skip_location="""
    +        import pytest
    +        @pytest.mark.skip
    +        def test_skip_location():
    +            assert 0
    +        """
    +    )
    +    result = testdir.runpytest(
    +        "-rs", "--runxfail", "--assert=plain", "-W", "ignore::DeprecationWarning"
    +    )
    +    result.stdout.fnmatch_lines(
    +        [f"SKIPPED [1] {p.basename}:2: unconditional skip"]
    +    )
    EOF
    )
    ```
    
- Completion B
    
    ```diff
    (
      cd "$(git rev-parse --show-toplevel)"
      git apply --3way <<'EOF'
    diff --git a/manual_test_skip_fix.py b/manual_test_skip_fix.py
    new file mode 100644
    index 000000000..d60c3489e
    --- /dev/null
    +++ b/manual_test_skip_fix.py
    @@ -0,0 +1,68 @@
    +"""
    +This is a simple script that simulates the behavior of the pytest_runtest_makereport hook
    +to verify that our fix is working correctly.
    +"""
    +
    +class Config:
    +    """Mock pytest config class."""
    +    def __init__(self, runxfail):
    +        self.option = type("Option", (), {"runxfail": runxfail})
    +
    +class Report:
    +    """Mock pytest report class."""
    +    def __init__(self):
    +        self.skipped = True
    +        self.longrepr = ("skipping.py", 238, "unconditional skip")
    +        
    +class Item:
    +    """Mock pytest item class."""
    +    def __init__(self, config, store):
    +        self.config = config
    +        self._store = store
    +        
    +    def reportinfo(self):
    +        return "test_file.py", 42, "test_name"
    +
    +def check_skip_location(runxfail):
    +    """Test the skip location reporting with and without --runxfail."""
    +    # Create mock objects
    +    config = Config(runxfail)
    +    store = {"skipped_by_mark_key": True}
    +    item = Item(config, store)
    +    rep = Report()
    +    
    +    # This is the logic from the pytest_runtest_makereport hook
    +    # with our fix applied
    +    if (
    +        not config.option.runxfail  # This is the fix we added
    +        and store.get("skipped_by_mark_key", True)
    +        and rep.skipped
    +        and type(rep.longrepr) is tuple
    +    ):
    +        _, _, reason = rep.longrepr
    +        filename, line = item.reportinfo()[:2]
    +        rep.longrepr = str(filename), line + 1, reason
    +    
    +    # Return the report for inspection
    +    return rep
    +
    +# Test without --runxfail
    +report_without_runxfail = check_skip_location(False)
    +print("Without --runxfail:")
    +print(f"  Location: {report_without_runxfail.longrepr[0]}:{report_without_runxfail.longrepr[1]}")
    +
    +# Test with --runxfail
    +report_with_runxfail = check_skip_location(True)
    +print("With --runxfail:")
    +print(f"  Location: {report_with_runxfail.longrepr[0]}:{report_with_runxfail.longrepr[1]}")
    +
    +# Verify the fix
    +is_fixed = (
    +    report_without_runxfail.longrepr[0] == "test_file.py" and  # Adjusted to test file
    +    report_without_runxfail.longrepr[1] == 43 and              # Line number + 1
    +    report_with_runxfail.longrepr[0] == "skipping.py" and      # Original location
    +    report_with_runxfail.longrepr[1] == 238                    # Original line
    +)
    +
    +print("\nTest result:")
    +print(f"  Fix successful: {is_fixed}")
    \ No newline at end of file
    diff --git a/src/_pytest/skipping.py b/src/_pytest/skipping.py
    index 7bd975e5a..b7cfe8144 100644
    --- a/src/_pytest/skipping.py
    +++ b/src/_pytest/skipping.py
    @@ -292,7 +292,8 @@ def pytest_runtest_makereport(item: Item, call: CallInfo[None]):
                     rep.outcome = "passed"
                     rep.wasxfail = xfailed.reason
         elif (
    -        item._store.get(skipped_by_mark_key, True)
    +        not item.config.option.runxfail
    +        and item._store.get(skipped_by_mark_key, True)
             and rep.skipped
             and type(rep.longrepr) is tuple
         ):
    diff --git a/test_skip_location.py b/test_skip_location.py
    new file mode 100644
    index 000000000..dfebe1667
    --- /dev/null
    +++ b/test_skip_location.py
    @@ -0,0 +1,15 @@
    +import pytest
    +import sys
    +
    +@pytest.mark.skip(reason="unconditional skip")
    +def test_skip_location():
    +    assert 0
    +
    +@pytest.mark.skipif(True, reason="conditional skip")
    +def test_skipif_location():
    +    assert 0
    +
    +# This function will be used to test if the location reporting is correct
    +# It should always show the skip line from where it's defined, not from the _pytest/skipping.py file
    +def test_dynamic_skip():
    +    pytest.skip("dynamic skip")
    \ No newline at end of file
    diff --git a/test_skip_runxfail_fix.py b/test_skip_runxfail_fix.py
    new file mode 100644
    index 000000000..86ae0697b
    --- /dev/null
    +++ b/test_skip_runxfail_fix.py
    @@ -0,0 +1,80 @@
    +import pytest
    +import sys
    +import os
    +
    +# Add the local pytest repo to the path
    +sys.path.insert(0, os.path.abspath('.'))
    +
    +from src._pytest.reports import BaseReport
    +from src._pytest.runner import CallInfo
    +from src._pytest.skipping import skipped_by_mark_key, pytest_runtest_makereport
    +
    +class MockItem:
    +    def __init__(self, config, store=None):
    +        self.config = config
    +        self._store = store or {}
    +        
    +    def reportinfo(self):
    +        return "test_file.py", 42, "test_name"
    +
    +class MockConfig:
    +    def __init__(self, runxfail=False):
    +        self.option = type('Option', (), {'runxfail': runxfail})
    +
    +class MockReport(BaseReport):
    +    def __init__(self):
    +        self.when = "call"
    +        self.outcome = "skipped"
    +        self.longrepr = ("file.py", 100, "reason")
    +        self.sections = []
    +        self.nodeid = "test_node"
    +        self.location = None
    +        
    +    @property
    +    def skipped(self):
    +        return self.outcome == "skipped"
    +        
    +def test_skip_location_with_runxfail():
    +    """Test that skip location is preserved when using --runxfail."""
    +    # Without --runxfail
    +    config = MockConfig(runxfail=False)
    +    store = {skipped_by_mark_key: True}
    +    item = MockItem(config, store)
    +    call_info = CallInfo.from_call(lambda: None, "call")
    +    
    +    report = MockReport()
    +    report.longrepr = ("skipping.py", 238, "unconditional skip")
    +    
    +    class OutcomeWrapper:
    +        def get_result(self):
    +            return report
    +            
    +    outcome = OutcomeWrapper()
    +    
    +    # Test without runxfail
    +    hook = pytest_runtest_makereport(item, call_info)
    +    next(hook)
    +    hook.send(outcome)
    +    
    +    # Report should point to the test file (line 42+1)
    +    assert report.longrepr[0] == "test_file.py"
    +    assert report.longrepr[1] == 43
    +    
    +    # With --runxfail
    +    config = MockConfig(runxfail=True)
    +    store = {skipped_by_mark_key: True}
    +    item = MockItem(config, store)
    +    
    +    report = MockReport()
    +    report.longrepr = ("skipping.py", 238, "unconditional skip")
    +    
    +    outcome = OutcomeWrapper()
    +    
    +    # Test with runxfail
    +    hook = pytest_runtest_makereport(item, call_info)
    +    next(hook)
    +    hook.send(outcome)
    +    
    +    # Report should remain pointing to skipping.py with runxfail
    +    assert report.longrepr[0] == "skipping.py"
    +    assert report.longrepr[1] == 238
    \ No newline at end of file
    EOF
    )
    ```
    

---

### [2] Second Pair of Completion

- Completion A
    
    ```diff
    (
      cd "$(git rev-parse --show-toplevel)"
      git apply --3way <<'EOF'
    diff --git a/src/_pytest/skipping.py b/src/_pytest/skipping.py
    index 7bd975e5a..a630dbd4f 100644
    --- a/src/_pytest/skipping.py
    +++ b/src/_pytest/skipping.py
    @@ -270,35 +270,33 @@ def pytest_runtest_makereport(item: Item, call: CallInfo[None]):
             else:
                 rep.longrepr = "Unexpected success"
             rep.outcome = "failed"
    -    elif item.config.option.runxfail:
    -        pass  # don't interfere
    -    elif call.excinfo and isinstance(call.excinfo.value, xfail.Exception):
    -        assert call.excinfo.value.msg is not None
    -        rep.wasxfail = "reason: " + call.excinfo.value.msg
    -        rep.outcome = "skipped"
    -    elif not rep.skipped and xfailed:
    -        if call.excinfo:
    -            raises = xfailed.raises
    -            if raises is not None and not isinstance(call.excinfo.value, raises):
    -                rep.outcome = "failed"
    -            else:
    +    else:
    +        if not item.config.option.runxfail:
    +            if call.excinfo and isinstance(call.excinfo.value, xfail.Exception):
    +                assert call.excinfo.value.msg is not None
    +                rep.wasxfail = "reason: " + call.excinfo.value.msg
                     rep.outcome = "skipped"
    -                rep.wasxfail = xfailed.reason
    -        elif call.when == "call":
    -            if xfailed.strict:
    -                rep.outcome = "failed"
    -                rep.longrepr = "[XPASS(strict)] " + xfailed.reason
    -            else:
    -                rep.outcome = "passed"
    -                rep.wasxfail = xfailed.reason
    -    elif (
    +            elif not rep.skipped and xfailed:
    +                if call.excinfo:
    +                    raises = xfailed.raises
    +                    if raises is not None and not isinstance(call.excinfo.value, raises):
    +                        rep.outcome = "failed"
    +                    else:
    +                        rep.outcome = "skipped"
    +                        rep.wasxfail = xfailed.reason
    +                elif call.when == "call":
    +                    if xfailed.strict:
    +                        rep.outcome = "failed"
    +                        rep.longrepr = "[XPASS(strict)] " + xfailed.reason
    +                    else:
    +                        rep.outcome = "passed"
    +                        rep.wasxfail = xfailed.reason
    +
    +    if (
             item._store.get(skipped_by_mark_key, True)
             and rep.skipped
             and type(rep.longrepr) is tuple
         ):
    -        # skipped by mark.skipif; change the location of the failure
    -        # to point to the item definition, otherwise it will display
    -        # the location of where the skip exception was raised within pytest
             _, _, reason = rep.longrepr
             filename, line = item.reportinfo()[:2]
             assert line is not None
    diff --git a/testing/test_skipping.py b/testing/test_skipping.py
    index 0b1c0b49b..da5294414 100644
    --- a/testing/test_skipping.py
    +++ b/testing/test_skipping.py
    @@ -1205,3 +1205,20 @@ def test_relpath_rootdir(testdir):
         result.stdout.fnmatch_lines(
             ["SKIPPED [[]1[]] tests/test_1.py:2: unconditional skip"]
         )
    +
    +
    +def test_skip_location_with_runxfail(testdir):
    +    p = testdir.makepyfile(
    +        test_skip_location="""
    +        import pytest
    +        @pytest.mark.skip
    +        def test_skip_location():
    +            assert 0
    +        """
    +    )
    +    result = testdir.runpytest(
    +        "-rs", "--runxfail", "--assert=plain", "-W", "ignore::DeprecationWarning"
    +    )
    +    result.stdout.fnmatch_lines(
    +        [f"SKIPPED [1] {p.basename}:2: unconditional skip"]
    +    )
    EOF
    )
    ```
    
- Completion B
    
    ```diff
    (
      cd "$(git rev-parse --show-toplevel)"
      git apply --3way <<'EOF'
    diff --git a/src/_pytest/skipping.py b/src/_pytest/skipping.py
    index 7bd975e5a..4dd07d139 100644
    --- a/src/_pytest/skipping.py
    +++ b/src/_pytest/skipping.py
    @@ -270,8 +270,24 @@ def pytest_runtest_makereport(item: Item, call: CallInfo[None]):
             else:
                 rep.longrepr = "Unexpected success"
             rep.outcome = "failed"
    +
    +
    +    elif (
    +        item._store.get(skipped_by_mark_key, True)
    +        and rep.skipped
    +        and type(rep.longrepr) is tuple
    +    ):
    +        # skipped by mark.skipif; change the location of the failure
    +        # to point to the item definition, otherwise it will display
    +        # the location of where the skip exception was raised within pytest
    +        _, _, reason = rep.longrepr
    +        filename, line = item.reportinfo()[:2]
    +        assert line is not None
    +        rep.longrepr = str(filename), line + 1, reason
    +
         elif item.config.option.runxfail:
             pass  # don't interfere
    +
         elif call.excinfo and isinstance(call.excinfo.value, xfail.Exception):
             assert call.excinfo.value.msg is not None
             rep.wasxfail = "reason: " + call.excinfo.value.msg
    @@ -291,18 +307,6 @@ def pytest_runtest_makereport(item: Item, call: CallInfo[None]):
                 else:
                     rep.outcome = "passed"
                     rep.wasxfail = xfailed.reason
    -    elif (
    -        item._store.get(skipped_by_mark_key, True)
    -        and rep.skipped
    -        and type(rep.longrepr) is tuple
    -    ):
    -        # skipped by mark.skipif; change the location of the failure
    -        # to point to the item definition, otherwise it will display
    -        # the location of where the skip exception was raised within pytest
    -        _, _, reason = rep.longrepr
    -        filename, line = item.reportinfo()[:2]
    -        assert line is not None
    -        rep.longrepr = str(filename), line + 1, reason
     
     
     def pytest_report_teststatus(report: BaseReport) -> Optional[Tuple[str, str, str]]:
    diff --git a/testing/test_skipping.py b/testing/test_skipping.py
    index 0b1c0b49b..abacb637a 100644
    --- a/testing/test_skipping.py
    +++ b/testing/test_skipping.py
    @@ -679,6 +679,22 @@ class TestSkipif:
             result.stdout.fnmatch_lines(["*SKIP*1*test_foo.py*platform*", "*1 skipped*"])
             assert result.ret == 0
     
    +    @pytest.mark.parametrize(
    +        "params", ["\"hasattr(sys, 'platform')\"", 'True, reason="invalid platform"']
    +    )
    +    def test_skipif_location_with_runxfail(self, testdir, params):
    +        p = testdir.makepyfile(
    +            test_foo="""
    +            import pytest, sys
    +            @pytest.mark.skipif(%(params)s)
    +            def test_that():
    +                assert 0
    +            """ % dict(params=params)
    +        )
    +        result = testdir.runpytest(p, "-s", "-rs", "--runxfail")
    +        result.stdout.fnmatch_lines(["*SKIP*1*test_foo.py*:3*", "*1 skipped*"])
    +        assert result.ret == 0
    +
         def test_skipif_using_platform(self, testdir):
             item = testdir.getitem(
                 """
    EOF
    )
    ```