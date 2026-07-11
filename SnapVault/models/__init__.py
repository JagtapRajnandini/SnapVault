# SnapVault/models/__init__.py
#
# Re-exports all model classes so other modules can write:
#
#   from SnapVault.models import User
#   from SnapVault.models import Document
#   from SnapVault.models import Reminder
#
# instead of reaching into each sub-module directly.
#
# Blueprint reference: Part 4 → app/models/__init__.py
# Day 1 Phase 1, item 11.

from SnapVault.models.user import User          # noqa: F401
from SnapVault.models.document import Document  # noqa: F401
from SnapVault.models.reminder import Reminder  # noqa: F401