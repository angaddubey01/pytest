import pytest
import sys
import os

# Add the local pytest repo to the path
sys.path.insert(0, os.path.abspath('.'))

from src._pytest.reports import BaseReport
from src._pytest.runner import CallInfo
from src._pytest.skipping import skipped_by_mark_key, pytest_runtest_makereport

class MockItem:
    def __init__(self, config, store=None):
        self.config = config
        self._store = store or {}
        
    def reportinfo(self):
        return "test_file.py", 42, "test_name"

class MockConfig:
    def __init__(self, runxfail=False):
        self.option = type('Option', (), {'runxfail': runxfail})

class MockReport(BaseReport):
    def __init__(self):
        self.when = "call"
        self.outcome = "skipped"
        self.longrepr = ("file.py", 100, "reason")
        self.sections = []
        self.nodeid = "test_node"
        self.location = None
        
    @property
    def skipped(self):
        return self.outcome == "skipped"
        
def test_skip_location_with_runxfail():
    """Test that skip location is preserved when using --runxfail."""
    # Without --runxfail
    config = MockConfig(runxfail=False)
    store = {skipped_by_mark_key: True}
    item = MockItem(config, store)
    call_info = CallInfo.from_call(lambda: None, "call")
    
    report = MockReport()
    report.longrepr = ("skipping.py", 238, "unconditional skip")
    
    class OutcomeWrapper:
        def get_result(self):
            return report
            
    outcome = OutcomeWrapper()
    
    # Test without runxfail
    hook = pytest_runtest_makereport(item, call_info)
    next(hook)
    hook.send(outcome)
    
    # Report should point to the test file (line 42+1)
    assert report.longrepr[0] == "test_file.py"
    assert report.longrepr[1] == 43
    
    # With --runxfail
    config = MockConfig(runxfail=True)
    store = {skipped_by_mark_key: True}
    item = MockItem(config, store)
    
    report = MockReport()
    report.longrepr = ("skipping.py", 238, "unconditional skip")
    
    outcome = OutcomeWrapper()
    
    # Test with runxfail
    hook = pytest_runtest_makereport(item, call_info)
    next(hook)
    hook.send(outcome)
    
    # Report should remain pointing to skipping.py with runxfail
    assert report.longrepr[0] == "skipping.py"
    assert report.longrepr[1] == 238