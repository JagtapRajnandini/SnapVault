# SnapVault/forms/__init__.py
#
# Re-exports all form classes so other modules can write:
#
#   from SnapVault.forms import RegisterForm, LoginForm, UploadForm
#
# instead of reaching into the individual sub-modules directly.
# This keeps imports clean and consistent across the codebase.
#
# Blueprint reference: Part 4 → app/forms/__init__.py
# Day 2: RegisterForm, LoginForm
# Day 3: UploadForm  ← added now

# Auth forms (Day 2)
from SnapVault.forms.auth_forms import LoginForm, RegisterForm  # noqa: F401

# Document forms (Day 3)
from SnapVault.forms.document_forms import UploadForm  # noqa: F401