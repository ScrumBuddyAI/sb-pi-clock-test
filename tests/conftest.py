"""Pytest configuration and fixtures for DeskClock tests.

This module configures Qt for headless operation and provides
shared fixtures for testing Qt-based components in CI environments.

The QT_QPA_PLATFORM environment variable is set to 'offscreen' before
any Qt imports to enable testing without a physical display.
"""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Generator

import pytest

# Configure Qt for headless/offscreen operation BEFORE importing Qt modules.
# This must happen before any PySide6 imports to take effect.
# The 'offscreen' platform allows Qt to run without a display server.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Try to import Qt, but handle missing system libraries gracefully
try:
    from PySide6.QtWidgets import QApplication

    QT_AVAILABLE = True
except ImportError as e:
    QT_AVAILABLE = False
    QT_IMPORT_ERROR = str(e)
    QApplication = None  # type: ignore[misc, assignment]

if TYPE_CHECKING:
    pass


# Skip all Qt-dependent tests if Qt libraries are not available
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "qt: mark test as requiring Qt (skipped if Qt unavailable)"
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Skip Qt-dependent tests if Qt is not available."""
    if QT_AVAILABLE:
        return

    skip_qt = pytest.mark.skip(reason=f"Qt not available: {QT_IMPORT_ERROR}")
    for item in items:
        # Skip any test that uses the qapp fixture
        if "qapp" in getattr(item, "fixturenames", []):
            item.add_marker(skip_qt)


@pytest.fixture(scope="session")
def qapp() -> Generator[QApplication, None, None]:
    """Create a QApplication instance for the test session.

    This fixture is session-scoped to ensure only one QApplication
    exists during the entire test run. Qt only allows a single
    QApplication instance per process.

    The fixture checks for an existing instance to support running
    tests alongside other Qt-based test utilities.

    Yields:
        The QApplication instance for use in tests.

    Raises:
        pytest.skip: If Qt libraries are not available in the environment.
    """
    if not QT_AVAILABLE:
        pytest.skip(f"Qt not available: {QT_IMPORT_ERROR}")

    # Check if a QApplication already exists (e.g., from pytest-qt)
    existing_app = QApplication.instance()
    if existing_app is not None:
        # Cast to QApplication since we know it's a GUI application
        app: QApplication = existing_app  # type: ignore[assignment]
    else:
        # Create a new QApplication with minimal arguments
        app = QApplication(sys.argv)

    yield app

    # Note: We don't call app.quit() here because:
    # 1. It can cause issues with test cleanup order
    # 2. The process will exit cleanly anyway when tests complete
