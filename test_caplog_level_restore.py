import logging

# First test - this will modify the log level
def test_foo(caplog):
    print("Before setting level in test_foo:")
    print("- caplog.handler.level:", caplog.handler.level)
    print("- Root logger level:", logging.getLogger().level)
    print("- Handler ID:", hex(id(caplog.handler)))
    
    caplog.set_level(42)
    
    print("After setting level in test_foo:")
    print("- caplog.handler.level:", caplog.handler.level)
    print("- Root logger level:", logging.getLogger().level)
    print("- Handler ID:", hex(id(caplog.handler)))

# Second test - should see original levels
def test_bar(caplog):
    print("In test_bar:")
    print("- caplog.handler.level:", caplog.handler.level)
    print("- Root logger level:", logging.getLogger().level)
    print("- Handler ID:", hex(id(caplog.handler)))

# Add a log message to see which levels are actually captured
def test_check_level(caplog):
    logging.getLogger().setLevel(logging.DEBUG)  # Allow all logs
    print("- Handler ID:", hex(id(caplog.handler)))
    
    # Log at all levels to see what gets captured
    logging.debug("Debug message")
    logging.info("Info message")
    logging.warning("Warning message")
    logging.error("Error message")
    
    # Print what was captured
    print("Log records captured:")
    for record in caplog.records:
        print(f"- {record.levelname}: {record.getMessage()}")
        
    print("Caplog handler level:", caplog.handler.level)