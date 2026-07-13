# SnapVault/forms/document_forms.py
#
# WTForms used for document upload.
# FlaskForm automatically adds CSRF protection to every form.
#
# This file defines UploadForm, which is used by the upload route
# to validate the file submitted by the user before any processing begins.
#
# Blueprint reference: Part 4 → app/forms/document_forms.py
# Day 3 Phase 4.

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SubmitField

from SnapVault.utils.constants import ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Upload Form
# ---------------------------------------------------------------------------

class UploadForm(FlaskForm):
    """
    Form used to upload a document image.

    Validates that:
    - A file has actually been selected (FileRequired).
    - The file extension is one of the allowed types (FileAllowed).

    Note: FileField uses different validators than StringField.
    - FileRequired()  replaces DataRequired() for file inputs.
    - FileAllowed()   takes a list of allowed extensions and an error message.

    CSRF protection is provided automatically by FlaskForm.
    The template must include {{ form.hidden_tag() }} inside the <form> tag.

    The HTML form tag must include enctype="multipart/form-data" or the
    browser will NOT send the file — it will send only the filename string.
    """

    file = FileField(
        # Label displayed above the file input in the template.
        'Upload Document Image',
        validators=[
            # FileRequired checks that the user has selected a file.
            # Without this, an empty form submission passes validation.
            FileRequired(message='Please select a file to upload.'),

            # FileAllowed checks the file extension against the allowed list.
            # ALLOWED_EXTENSIONS is a set e.g. {'png', 'jpg', 'jpeg'}.
            # Converting to list because FileAllowed expects a list or
            # an Upload object.
            # The second argument is the error message shown on failure.
            FileAllowed(
                list(ALLOWED_EXTENSIONS),
                f'Only {", ".join(sorted(ALLOWED_EXTENSIONS)).upper()} '
                f'files are allowed.'
            ),
        ]
    )

    submit = SubmitField('Upload')