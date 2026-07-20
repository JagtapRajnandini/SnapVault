# SnapVault/routes/dashboard_routes.py
#
# Dashboard route — the landing page for logged-in users.
#
# Responsibilities:
#   1. Count the total number of documents the user has uploaded.
#   2. Count documents per category using a GROUP BY query.
#   3. Fetch the 5 most recently uploaded documents.
#   4. Pass all of this to the dashboard template.
#
# All counting is done IN THE DATABASE using aggregate functions,
# not by loading all documents into Python memory and using len().
#
# Blueprint reference: Part 4 → app/routes/dashboard_routes.py
# Day 4.

from flask import render_template
from flask_login import current_user, login_required
from sqlalchemy import func

from SnapVault import app, db
from SnapVault.models.document import Document
from SnapVault.utils.constants import CATEGORIES


# ---------------------------------------------------------------------------
# Dashboard  GET /dashboard
# ---------------------------------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard_page():
    """
    The main landing page for authenticated users.

    Queries:
      1. total_count  — total number of documents uploaded by this user.
      2. category_counts — a dict mapping each category name to its count.
      3. recent_docs — the 5 most recently uploaded documents.

    Uses SQLAlchemy aggregate queries (func.count + group_by) so the
    database does the counting work, not Python. This is efficient even
    when a user has thousands of documents.
    """

    # ── Query 1: Total document count ─────────────────────────────────────
    # func.count(Document.id) counts the number of rows.
    # filter_by restricts to the current user.
    # scalar() returns the single integer result directly.
    total_count = db.session.query(
        func.count(Document.id)
    ).filter(
        Document.user_id == current_user.id
    ).scalar() or 0

    # ── Query 2: Per-category document counts ─────────────────────────────
    # group_by(Document.category) groups the rows by the category column.
    # with_entities() tells SQLAlchemy which columns to SELECT:
    #   - Document.category: the group key
    #   - func.count(Document.id): the count for that group
    # The result is a list of Row objects: [(category_name, count), ...]
    rows = db.session.query(
        Document.category,
        func.count(Document.id).label('count')
    ).filter(
        Document.user_id == current_user.id
    ).group_by(
        Document.category
    ).all()

    # Build a dict from the query results: {'Bills': 3, 'Medical': 1, ...}
    # Start with 0 for every category so the template always has a full set.
    category_counts = {category: 0 for category in CATEGORIES}
    for row in rows:
        # row.category is the category name string.
        # row.count is the integer count.
        if row.category in category_counts:
            category_counts[row.category] = row.count

    # ── Query 3: 5 most recent documents ──────────────────────────────────
    # order_by(Document.uploaded_at.desc()) sorts newest first.
    # limit(5) retrieves only 5 rows — efficient regardless of total count.
    recent_docs = Document.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Document.uploaded_at.desc()
    ).limit(5).all()

    return render_template(
        'dashboard/index.html',
        total_count=total_count,
        category_counts=category_counts,
        recent_docs=recent_docs,
        categories=CATEGORIES,
    )