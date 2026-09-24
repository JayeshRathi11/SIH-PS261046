"""
conftest.py – Session-scoped event loop for Python 3.14

Forces all tests and fixtures to share one event loop for the full session.
This prevents asyncpg connection pool "Future attached to a different loop"
errors that occur when each test gets its own event loop.
"""
