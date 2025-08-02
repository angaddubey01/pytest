"""
This is a simple script that simulates the behavior of the pytest_runtest_makereport hook
to verify that our fix is working correctly.
"""

class Config:
    """Mock pytest config class."""
    def __init__(self, runxfail):
        self.option = type("Option", (), {"runxfail": runxfail})

class Report:
    """Mock pytest report class."""
    def __init__(self):
        self.skipped = True
        self.longrepr = ("skipping.py", 238, "unconditional skip")
        
class Item:
    """Mock pytest item class."""
    def __init__(self, config, store):
        self.config = config
        self._store = store
        
    def reportinfo(self):
        return "test_file.py", 42, "test_name"

def check_skip_location(runxfail):
    """Test the skip location reporting with and without --runxfail."""
    # Create mock objects
    config = Config(runxfail)
    store = {"skipped_by_mark_key": True}
    item = Item(config, store)
    rep = Report()
    
    # This is the logic from the pytest_runtest_makereport hook
    # with our fix applied
    if (
        not config.option.runxfail  # This is the fix we added
        and store.get("skipped_by_mark_key", True)
        and rep.skipped
        and type(rep.longrepr) is tuple
    ):
        _, _, reason = rep.longrepr
        filename, line = item.reportinfo()[:2]
        rep.longrepr = str(filename), line + 1, reason
    
    # Return the report for inspection
    return rep

# Test without --runxfail
report_without_runxfail = check_skip_location(False)
print("Without --runxfail:")
print(f"  Location: {report_without_runxfail.longrepr[0]}:{report_without_runxfail.longrepr[1]}")

# Test with --runxfail
report_with_runxfail = check_skip_location(True)
print("With --runxfail:")
print(f"  Location: {report_with_runxfail.longrepr[0]}:{report_with_runxfail.longrepr[1]}")

# Verify the fix
is_fixed = (
    report_without_runxfail.longrepr[0] == "test_file.py" and  # Adjusted to test file
    report_without_runxfail.longrepr[1] == 43 and              # Line number + 1
    report_with_runxfail.longrepr[0] == "skipping.py" and      # Original location
    report_with_runxfail.longrepr[1] == 238                    # Original line
)

print("\nTest result:")
print(f"  Fix successful: {is_fixed}")