# SnapVault/forms/__init__.py
#
# Re-exports all form classes so other modules can write:
#
#   from SnapVault.forms import RegisterForm, LoginForm
#
# instead of reaching into the individual sub-modules directly.
#
# Blueprint reference: Part 4 → app/forms/__init__.py
# Day 2 Phase 3, item 16.

from SnapVault.forms.auth_forms import LoginForm, RegisterForm  # noqa: F401
