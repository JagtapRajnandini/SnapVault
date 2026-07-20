# SnapVault/routes/document_routes.py
#
# Routes for document upload, history, detail view, file serving, and deletion.
#
# Upload pipeline (POST /upload):
#   validate form → check extension → compute hash → detect duplicates
#   → save file → create Document row → run OCR → classify → commit → redirect
#
# Every route that touches a Document verifies ownership so that
# User A can never access User B's documents (IDOR protection).
#
# Day 3: upload_page, history_page, document_detail_page, serve_file
# Day 4: DeleteForm, delete_document_page (new)
#         document_detail_page updated to pass delete_form.
#
# Blueprint reference: Part 4 → app/routes/document_routes.py
#                      Part 6.2 Route Map

import os

from flask import (abort, flash, redirect, render_template,
                   request, send_from_directory, url_for)
from flask_login import current_user, login_required
from flask_wtf import FlaskForm

from SnapVault import app, db
from SnapVault.forms.document_forms import UploadForm
from SnapVault.models.document import Document
from SnapVault.services.classification_service import classify
from SnapVault.services.ocr_service import extract_text
from SnapVault.services.storage_service import (
    allowed_extension,
    compute_hash,
    delete_file,
    save_file,
)


# ---------------------------------------------------------------------------
# DeleteForm
# ---------------------------------------------------------------------------
# A minimal FlaskForm with no fields.
#
# Its only purpose is CSRF protection on the delete action.
# FlaskForm automatically embeds a hidden CSRF token when you call
# {{ delete_form.hidden_tag() }} in the template.
# When the form is submitted, validate_on_submit() verifies that token.
#
# Why not a plain POST with a manual CSRF token?
# Using FlaskForm is the idiomatic Flask-WTF pattern and keeps
# validation consistent with every other form in the project.

class DeleteForm(FlaskForm):
    """Minimal CSRF-protected form for the document delete endpoint."""
    pass


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
        # validator may miss.
        if not allowed_extension(file.filename):
            flash(
                'Invalid file type. Only PNG, JPG, and JPEG are accepted.',
                'danger'
            )
            return redirect(url_for('upload_page'))

        # ── Duplicate detection ───────────────────────────────────────────
        # Compute the SHA-256 hash BEFORE writing anything to disk.
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
        # Committed before OCR so the document exists even if OCR fails.
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
        full_image_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            doc.file_path,
        )
        ocr_text = extract_text(full_image_path)

        # ── Update OCR results ────────────────────────────────────────────
        doc.ocr_text = ocr_text
        doc.ocr_status = 'success' if ocr_text else 'failed'

        # ── Classify ──────────────────────────────────────────────────────
        doc.category = classify(ocr_text)

        # ── Final commit ──────────────────────────────────────────────────
        db.session.commit()

        flash('Document uploaded and processed successfully.', 'success')
        return redirect(url_for('document_detail_page', doc_id=doc.id))

    return render_template('documents/upload.html', form=form)


# ---------------------------------------------------------------------------
# Document History  GET /history
# ---------------------------------------------------------------------------

@app.route('/history')
@login_required
def history_page():
    """
    Display all documents uploaded by the current user.
    Supports full-text search via ?q= query parameter across
    original_filename, ocr_text, and category columns.
    Results are ordered newest-first (uploaded_at DESC).
    """
    q = request.args.get('q', '').strip()

    base_query = Document.query.filter_by(user_id=current_user.id)

    if q:
        search_term = f'%{q}%'
        base_query = base_query.filter(
            db.or_(
                Document.original_filename.ilike(search_term),
                Document.ocr_text.ilike(search_term),
                Document.category.ilike(search_term),
            )
        )

    # NOTE: The Document model uses 'uploaded_at' as the timestamp column name.
    documents = base_query.order_by(Document.uploaded_at.desc()).all()

    return render_template(
        'documents/history.html',
        documents=documents,
        search_query=q,
    )


# ---------------------------------------------------------------------------
# Document Detail  GET /document/<doc_id>
# ---------------------------------------------------------------------------

@app.route('/document/<int:doc_id>')
@login_required
def document_detail_page(doc_id):
    """
    Display the detail view for a single document.

    IDOR protection: both id AND user_id are used in the filter.
    first_or_404() returns 404 if no matching row exists — this covers
    the case where doc_id belongs to a different user.

    Day 4 addition: a DeleteForm instance is passed to the template so
    the delete button can render a CSRF-protected POST form.
    """
    doc = Document.query.filter_by(
        id=doc_id,
        user_id=current_user.id,
    ).first_or_404()

    # Create a blank DeleteForm — it has no fields, only a CSRF token.
    # The template calls {{ delete_form.hidden_tag() }} to embed the token.
    delete_form = DeleteForm()

    return render_template(
        'documents/detail.html',
        document=doc,
        delete_form=delete_form,
    )


# ---------------------------------------------------------------------------
# Delete Document  POST /document/<doc_id>/delete
# ---------------------------------------------------------------------------

@app.route('/document/<int:doc_id>/delete', methods=['POST'])
@login_required
def delete_document_page(doc_id):
    """
    Delete a document: removes the database row and the file from disk.

    POST-only: GET requests return 405 Method Not Allowed automatically.
    This prevents CSRF via embedded image tags or link prefetching.

    IDOR protection: filter_by includes both id AND user_id.
    A user can only delete their own documents.
    first_or_404() prevents leaking whether a document exists.

    CSRF protection: validate_on_submit() checks the hidden token
    injected by {{ delete_form.hidden_tag() }} in the template.
    Any request missing a valid token is rejected with a 400.

    Deletion order:
        1. Fetch and verify ownership.
        2. Save the file_path before the ORM object is deleted.
        3. Delete the database row and commit.
        4. Delete the file from disk.
    The DB row is deleted first. If disk deletion fails, the document
    is already gone from the user's perspective — the orphaned file
    is a minor disk-management concern, not a security or data issue.
    """
    # ── CSRF validation ───────────────────────────────────────────────────
    # DeleteForm has no fields, but validate_on_submit() checks that:
    #   - The request method is POST.
    #   - The CSRF token in the submitted form matches the session token.
    # If validation fails, abort with 400 Bad Request.
    form = DeleteForm()
    if not form.validate_on_submit():
        abort(400)

    # ── Ownership check (IDOR protection) ─────────────────────────────────
    # filter_by with BOTH id AND user_id means a logged-in user can only
    # delete a document if they own it.
    # first_or_404() returns 404 if no matching row is found — this covers:
    #   - The document does not exist.
    #   - The document belongs to a different user.
    # Both cases look identical to the requester (404), which is correct.
    doc = Document.query.filter_by(
        id=doc_id,
        user_id=current_user.id,
    ).first_or_404()

    # ── Save file path before deleting the ORM object ─────────────────────
    # After db.session.delete(doc) and commit(), the 'doc' object is
    # detached from the session and its attributes may not be accessible.
    # Capture file_path now while the object is still fully loaded.
    file_path = doc.file_path

    # ── Delete the database row ───────────────────────────────────────────
    db.session.delete(doc)
    db.session.commit()
    # The document is now permanently removed from the database.
    # Any Reminder rows linked to this document have document_id set to
    # NULL by the database's SET NULL cascade (defined in reminder.py).

    # ── Delete the file from disk ──────────────────────────────────────────
    # delete_file() silently ignores FileNotFoundError — the DB row is
    # already gone, so a missing file is not a problem.
    delete_file(
        upload_folder=app.config['UPLOAD_FOLDER'],
        file_path=file_path,
    )

    flash('Document deleted successfully.', 'success')
    return redirect(url_for('history_page'))


# ---------------------------------------------------------------------------
# Serve File  GET /uploads/<user_id>/<filename>
# ---------------------------------------------------------------------------

@app.route('/uploads/<int:user_id>/<path:filename>')
@login_required
def serve_file(user_id, filename):
    """
    Serve an uploaded image file to the authenticated owner.

    Two-layer IDOR check:
      Layer 1: URL user_id must equal current_user.id.
      Layer 2: Document row must exist with matching user_id and file_path.

    send_from_directory() safely serves from the user's subfolder.
    """
    # ── Layer 1: Integer comparison — no DB hit needed ────────────────────
    if user_id != current_user.id:
        abort(403)

    # ── Layer 2: DB ownership verification ───────────────────────────────
    file_path = os.path.join(str(user_id), filename)

    Document.query.filter_by(
        file_path=file_path,
        user_id=current_user.id,
    ).first_or_404()

    # ── Serve ─────────────────────────────────────────────────────────────
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))

    return send_from_directory(user_folder, filename)