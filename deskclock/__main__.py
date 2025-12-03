"""Entrypoint module for running DeskClock as a package.

This module enables execution via: python -m deskclock

The entrypoint delegates to the application orchestration layer,
maintaining separation between the bootstrap mechanism and the
application lifecycle management.
"""

import sys

from deskclock.app.app import run


def main() -> int:
    """Main entrypoint for the DeskClock application.

    Returns:
        Exit code: 0 for success, non-zero for errors.
    """
    return run()


if __name__ == "__main__":
    sys.exit(main())
