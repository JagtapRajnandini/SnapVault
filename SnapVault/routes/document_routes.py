# SnapVault/routes/document_routes.py
#
# Routes for document upload, history, detail view, and file serving.
#
# Upload pipeline (POST /upload):
#   validate form → check extension → compute hash → detect duplicates
#   → save file → create Document row → run OCR → classify → commit → redirect
#
# Every route that touches a Document verifies ownership so that
# User A can never access User B's documents (IDOR protection).
#
# Blueprint reference: Part 4 → app/routes/document_routes.py
#                      Part 6.2 Route Map
#                      Part 3.4 Document Upload Flow
# Day 3 Phase 4.

import os # Imports Python's os module.
          # Used to work with file paths.

from flask import (abort, # Stop request with error (403,404,etc.)
                   flash, # Show one-time message
                   redirect, # Redirect user to another route
                   render_template, # Render HTML page
                   request, # Read GET/POST request
                   send_from_directory, # Send uploaded file
                   url_for # Generate route URL
                   )

from flask_login import current_user, login_required

from SnapVault import app, db
from SnapVault.forms.document_forms import UploadForm
from SnapVault.models.document import Document
from SnapVault.services.classification_service import classify
from SnapVault.services.ocr_service import extract_text
from SnapVault.services.storage_service import (
    allowed_extension,
    compute_hash,
    save_file,
)


# ---------------------------------------------------------------------------
# Upload  GET, POST /upload
# ---------------------------------------------------------------------------

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_page():
    """
    GET  — Render the upload form.
    POST — Run the full upload pipeline:
             1. Validate the form (FileRequired + FileAllowed).
             2. Check the file extension (second layer of defence).
             3. Compute SHA-256 hash for duplicate detection.
             4. Reject if the same file has already been uploaded.
             5. Save the file to disk (UUID rename + Pillow verify).
             6. Create a Document row with ocr_status='pending'.
             7. Run OCR synchronously.
             8. Update ocr_text and ocr_status on the Document.
             9. Classify the text and update the category.
            10. Final commit and redirect to the detail page.
    """
    form = UploadForm()

    if form.validate_on_submit():

        file = form.file.data  # FileStorage object from Flask-WTF

        # ── Layer 2 extension check ───────────────────────────────────────
        # FileAllowed in the form (Layer 1) validates the extension by name.
        # allowed_extension() here is Layer 2 — it also strips path
        # components and lowercases, so it catches edge cases the form
        # validator may miss (e.g., browsers reporting wrong MIME types).
        if not allowed_extension(file.filename):
            flash(
                'Invalid file type. Only PNG, JPG, and JPEG are accepted.',
                'danger'
            )
            return redirect(url_for('upload_page'))

        # ── Duplicate detection ───────────────────────────────────────────
        # Compute the SHA-256 hash BEFORE writing anything to disk.
        # If a Document row already exists for this user with the same hash,
        # reject the upload immediately — no disk write needed.
        file_hash = compute_hash(file.stream)

        duplicate = Document.query.filter_by(
            user_id=current_user.id,
            file_hash=file_hash,
        ).first()

        if duplicate:
            flash(
                'This file has already been uploaded. '
                'View it in your document history.',
                'warning'
            )
            return redirect(url_for('history_page'))

        # ── Save the file to disk ─────────────────────────────────────────
        # save_file() handles UUID renaming, creates the user subfolder,
        # saves the file, and runs Pillow verification.
        # It raises ValueError if Pillow rejects the file as a non-image.
        try:
            file_info = save_file(
                file_storage=file,
                user_id=current_user.id,
                upload_folder=app.config['UPLOAD_FOLDER'],
            )
        except ValueError as e:
            flash(str(e), 'danger')
            return redirect(url_for('upload_page'))

        # ── Create the Document row with status='pending' ─────────────────
        # The row is committed before OCR runs so that the document exists
        # in the database even if OCR fails — the user can still see it
        # in their history with ocr_status='failed'.
        doc = Document(
            user_id=current_user.id,
            original_filename=file_info['original_filename'],
            stored_filename=file_info['stored_filename'],
            file_path=file_info['file_path'],
            file_size=file_info['file_size'],
            file_hash=file_info['file_hash'],
            ocr_status='pending',
            category='Miscellaneous',
        )
        db.session.add(doc)
        db.session.commit()

        # ── Run OCR ───────────────────────────────────────────────────────
        # Build the absolute path to the saved image for EasyOCR.
        # extract_text() returns '' on failure — it never raises.
        full_image_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            doc.file_path,
        )
        ocr_text = extract_text(full_image_path)

        # ── Update OCR results on the Document row ────────────────────────
        doc.ocr_text = ocr_text
        # A non-empty string means OCR produced output; empty means it failed.
        doc.ocr_status = 'success' if ocr_text else 'failed'

        # ── Classify the extracted text ───────────────────────────────────
        # classify() always returns a valid category string — never raises.
        # Returns 'Miscellaneous' if ocr_text is empty or no keywords match.
        doc.category = classify(ocr_text)

        # ── Final commit ──────────────────────────────────────────────────
        db.session.commit()

        flash('Document uploaded and processed successfully.', 'success')
        return redirect(url_for('document_detail_page', doc_id=doc.id))

    # GET request — render the empty upload form.
    return render_template('documents/upload.html', form=form)


# ---------------------------------------------------------------------------
# Document History  GET /history
# ---------------------------------------------------------------------------

@app.route('/history')
@login_required
def history_page():
    """
    Display a list of all documents uploaded by the current user.

    Supports full-text search via the ?q= query parameter.
    When q is present, the query is filtered across three columns:
        - original_filename (display name)
        - ocr_text          (extracted text content)
        - category          (auto-assigned label)

    ilike() is case-insensitive LIKE — works on both SQLite and PostgreSQL.

    Results are ordered newest-first (created_at DESC).
    """
    # Read the search query from the URL, e.g. /history?q=invoice
    q = request.args.get('q', '').strip()

    # Start with all documents owned by the current user.
    base_query = Document.query.filter_by(user_id=current_user.id)

    if q:
        # Wrap q in % wildcards for a "contains" search.
        search_term = f'%{q}%'

        # db.or_() chains multiple LIKE conditions with SQL OR.
        # A document matches if q appears in ANY of the three columns.
        base_query = base_query.filter(
            db.or_(
                Document.original_filename.ilike(search_term),
                Document.ocr_text.ilike(search_term),
                Document.category.ilike(search_term),
            )
        )

    # Order by newest upload first and execute the query.
    documents = base_query.order_by(Document.created_at.desc()).all()

    return render_template(
        'documents/history.html',
        documents=documents,
        search_query=q,  # passed back so the template can pre-fill the search box
    )


# ---------------------------------------------------------------------------
# Document Detail  GET /document/<doc_id>
# ---------------------------------------------------------------------------

@app.route('/document/<int:doc_id>')
@login_required
def document_detail_page(doc_id):
    """
    Display the detail view for a single document.

    IDOR protection: filter_by includes BOTH id AND user_id.
    Without the user_id check, any logged-in user could access any
    document by guessing or incrementing the doc_id in the URL.

    first_or_404() returns a 404 response if no matching row is found,
    which also covers the case where the doc_id belongs to another user.
    """
    doc = Document.query.filter_by(
        id=doc_id,
        user_id=current_user.id,
    ).first_or_404()

    return render_template('documents/detail.html', document=doc)


# ---------------------------------------------------------------------------
# Serve File  GET /uploads/<user_id>/<filename>
# ---------------------------------------------------------------------------

@app.route('/uploads/<int:user_id>/<path:filename>')
@login_required
def serve_file(user_id, filename):
    """
    Serve an uploaded image file to the authenticated owner.

    Files in the uploads/ folder are OUTSIDE Flask's static/ folder
    and are not publicly accessible via a direct URL. This route acts
    as a gatekeeper — it checks ownership before serving the file.

    Two-layer IDOR check:
      Layer 1: The user_id in the URL must match current_user.id.
               This is a fast integer comparison that rejects all
               cross-user requests before hitting the database.
      Layer 2: The Document row is queried with BOTH user_id and file_path.
               This ensures the file is registered in the database and
               actually belongs to the logged-in user.

    send_from_directory() safely serves the file from the user's
    subfolder. Flask prevents path traversal attacks internally.

    The <path:filename> converter allows slashes in the filename,
    future-proofing for nested subfolder structures.
    """
    # ── Layer 1: URL user_id must match the logged-in user ────────────────
    if user_id != current_user.id:
        # Return 403 Forbidden — the resource exists but access is denied.
        # Do NOT return 404, which would confirm the file does not exist.
        abort(403)

    # ── Layer 2: Document must exist and belong to the logged-in user ─────
    # Build the relative file_path as stored in the Document table:
    # e.g., "42/a3f82bc14e9d4012b6c3e7f8a1d09e2f.png"
    file_path = os.path.join(str(user_id), filename)

    Document.query.filter_by(
        file_path=file_path,
        user_id=current_user.id,
    ).first_or_404()

    # ── Serve the file ────────────────────────────────────────────────────
    # send_from_directory() requires the directory and the filename separately.
    # The directory is the user's subfolder inside UPLOAD_FOLDER.
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))

    return send_from_directory(user_folder, filename)