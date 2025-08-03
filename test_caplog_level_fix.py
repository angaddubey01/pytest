import logging
import pytest

def test_caplog_level_1(caplog):
    """First test sets the level to 42."""
    print("Initial handler level in test_caplog_level_1:", caplog.handler.level)
    
    # Set to a custom level
    caplog.set_level(42)
    
    print("Modified handler level in test_caplog_level_1:", caplog.handler.level)
    
    # Log a message at various levels to verify only those >= 42 are captured
    logging.debug("This debug message should NOT be captured")
    logging.info("This info message should NOT be captured")
    logging.warning("This warning message should NOT be captured")
    logging.error("This error message should be captured")  # ERROR is 40
    logging.critical("This critical message should be captured")  # CRITICAL is 50
    
    # Print which messages were captured
    print("Records captured in test_caplog_level_1:")
    for record in caplog.records:
        print(f"- {record.levelname}: {record.getMessage()}")

def test_caplog_level_2(caplog):
    """Second test verifies that handler level is reset."""
    print("Handler level in test_caplog_level_2:", caplog.handler.level)
    
    # Log messages at various levels to see what's captured with default level
    logging.debug("This debug message should NOT be captured")
    logging.info("This info message should NOT be captured")
    logging.warning("This warning message should be captured")  # WARNING is 30
    logging.error("This error message should be captured")  # ERROR is 40
    
    # Print which messages were captured
    print("Records captured in test_caplog_level_2:")
    for record in caplog.records:
        print(f"- {record.levelname}: {record.getMessage()}")