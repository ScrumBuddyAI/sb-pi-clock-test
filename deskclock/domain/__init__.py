"""Domain layer for DeskClock core business logic.

This package contains domain entities, value objects, and service interfaces
that represent the core concepts of the application. Domain components are
independent of UI frameworks and infrastructure concerns.

Key components:
- TimeService: Current time retrieval and formatting
"""

from deskclock.domain.time_service import TimeService, TimeServiceProtocol

__all__ = ["TimeService", "TimeServiceProtocol"]
