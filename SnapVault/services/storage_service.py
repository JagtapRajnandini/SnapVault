# SnapVault/services/storage_service.py
#
# Responsible for every file-system operation in the upload pipeline.
#
# Other modules (document_routes.py) call these functions and never
# touch the filesystem directly — all disk I/O is centralised here.
#
# Blueprint reference: Part 4 → app/services/storage_service.py
# Day 3 Phase 4.

import hashlib # hashing library
import os # Imports operating system utilities.
import uuid # Used to generate unique filenames.

from PIL import Image
from werkzeug.utils import secure_filename # Remove dangerous characters from filenames.

from SnapVault.utils.constants import ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Extension validation
# ---------------------------------------------------------------------------

def allowed_extension(filename: str) -> bool:
    """
    Return True if the filename has an allowed image extension.

    Checks against ALLOWED_EXTENSIONS from constants.py.
    This is the FIRST layer of validation (form layer is the second).
    Defence-in-depth: both layers must pass before a file is accepted.

    Examples:
        allowed_extension("photo.jpg")  -> True
        allowed_extension("script.exe") -> False
        allowed_extension("noextension") -> False
    """
    # A filename with no dot has no extension and is always rejected.
    if '.' not in filename:
        return False

    # Split on the last dot and take the part after it.
    # rsplit('.', 1) splits only on the LAST dot so "photo.backup.png"
    # correctly returns "png", not "backup.png".
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Image verification (Pillow)
# ---------------------------------------------------------------------------

def verify_image(file_path: str) -> bool:
    """
    Use Pillow to confirm the file on disk is a real, uncorrupted image.

    This is the SECOND validation layer. A user could rename "malware.exe"
    to "photo.png" — the extension check passes, but Pillow's verify()
    will raise an exception on a non-image or corrupted file.

    Returns True if the file is a valid image, False otherwise.

    Note: After calling img.verify(), Pillow marks the image object as
    "spent". The file_path on disk is unaffected — only the in-memory
    Image object cannot be reused. This is fine here because we only
    need the boolean result.
    """
    try:
        img = Image.open(file_path)
        img.verify()  # Raises exception if the file is not a valid image.
        return True
    except Exception:
        # Any exception means the file is not a valid image.
        return False


# ---------------------------------------------------------------------------
# SHA-256 hash computation
# ---------------------------------------------------------------------------

def compute_hash(file_stream) -> str:
    """
    Compute the SHA-256 hash of a file stream.

    Used for DUPLICATE DETECTION before saving to disk.
    If a Document row already exists for (user_id, file_hash), the route
    rejects the upload without writing anything to disk.

    The stream is read in 8 KB chunks to avoid loading the entire file
    into memory at once (important for large files near the 16 MB limit).

    The stream position is reset to 0 both before and after reading
    so the caller can still save the file after calling this function.
    """
    hasher = hashlib.sha256()

    # Always start reading from the beginning of the stream.
    file_stream.seek(0)

    while True:
        chunk = file_stream.read(8192)  # 8 KB chunks
        if not chunk:
            break
        hasher.update(chunk)

    # Reset position so the stream can be used again (e.g., for saving).
    file_stream.seek(0)

    return hasher.hexdigest()  # 64-character hex string


# ---------------------------------------------------------------------------
# Upload folder management
# ---------------------------------------------------------------------------

def get_user_upload_folder(upload_folder: str, user_id: int) -> str:
    """
    Return the absolute path to the upload subfolder for a specific user.

    Files are stored under:  uploads/<user_id>/<stored_filename>

    Keeping each user's files in their own subfolder:
      - Makes bulk deletion easy when a user account is removed.
      - Prevents filename collisions across users.
      - Matches a common cloud storage key pattern (easy to migrate).

    Creates the folder if it does not already exist.
    os.makedirs with exist_ok=True is idempotent — safe to call every upload.
    """
    user_folder = os.path.join(upload_folder, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    return user_folder


# ---------------------------------------------------------------------------
# Save file to disk
# ---------------------------------------------------------------------------

def save_file(file_storage, user_id: int, upload_folder: str) -> dict:
    """
    Run the full file-save pipeline and return metadata about the saved file.

    Pipeline steps:
      1. Sanitise the original filename with secure_filename().
      2. Extract the file extension.
      3. Generate a UUID-based stored filename (collision-proof).
      4. Compute the SHA-256 hash BEFORE saving (caller checks for duplicates).
      5. Get/create the user's upload subfolder.
      6. Save the file to disk.
      7. Record the file size in bytes.
      8. Verify the saved file is a real image using Pillow.
         If verification fails, delete the file and raise ValueError.

    Returns a dict with keys:
        original_filename (str)  — sanitised original name (for display)
        stored_filename   (str)  — UUID-based name on disk
        file_path         (str)  — relative path: "<user_id>/<stored_filename>"
                                   This is what Document.file_path stores.
        file_size         (int)  — size in bytes
        file_hash         (str)  — SHA-256 hex digest (for duplicate detection)

    Raises:
        ValueError — if Pillow rejects the file as an invalid image.
                     The partially-written file is deleted before raising.
    """
    # ── Step 1: Sanitise the original filename ────────────────────────────────
    # secure_filename() strips path separators, special chars, and dotfiles.
    # Example: "../../etc/passwd.jpg" → "etc_passwd.jpg"
    original_filename = secure_filename(file_storage.filename)

    # ── Step 2: Extract the file extension ───────────────────────────────────
    ext = original_filename.rsplit('.', 1)[1].lower()

    # ── Step 3: Generate a UUID-based stored filename ─────────────────────────
    # uuid4() is randomly generated — astronomically unlikely to collide.
    # hex removes the hyphens for a cleaner filename.
    # Example stored name: "a3f82bc14e9d4012b6c3e7f8a1d09e2f.png"
    stored_filename = f"{uuid.uuid4().hex}.{ext}"

    # ── Step 4: Compute the SHA-256 hash ──────────────────────────────────────
    # Done BEFORE saving so the caller can reject duplicates without
    # writing anything to disk. The stream is reset after reading.
    file_hash = compute_hash(file_storage.stream)

    # ── Step 5: Get/create the user's upload subfolder ───────────────────────
    user_folder = get_user_upload_folder(upload_folder, user_id)

    # ── Step 6: Build the full disk path and save the file ───────────────────
    full_path = os.path.join(user_folder, stored_filename)
    file_storage.save(full_path)

    # ── Step 7: Record the file size ──────────────────────────────────────────
    file_size = os.path.getsize(full_path)

    # ── Step 8: Verify the saved file is a real image ────────────────────────
    # Pillow re-reads the file from disk. If it raises any exception,
    # the file is not a valid image — delete it and surface the error.
    if not verify_image(full_path):
        os.remove(full_path)
        raise ValueError(
            "The uploaded file could not be verified as a valid image. "
            "Please upload a PNG, JPG, or JPEG file."
        )

    # ── Step 9: Build the relative file path ─────────────────────────────────
    # Stored as "<user_id>/<stored_filename>" so Document.file_path is
    # portable — the UPLOAD_FOLDER prefix is never baked in.
    # On PostgreSQL/cloud migration, only UPLOAD_FOLDER changes.
    file_path = os.path.join(str(user_id), stored_filename)

    return {
        'original_filename': original_filename,
        'stored_filename':   stored_filename,
        'file_path':         file_path,
        'file_size':         file_size,
        'file_hash':         file_hash,
    }


# ---------------------------------------------------------------------------
# Delete file from disk
# ---------------------------------------------------------------------------

def delete_file(upload_folder: str, file_path: str) -> None:
    """
    Delete a stored file from disk.

    file_path is the relative path stored in Document.file_path
    (e.g., "42/a3f82bc14e9d4012b6c3e7f8a1d09e2f.png").

    Silently ignores FileNotFoundError — the database row should be
    deleted even if the file was already removed or never saved.

    Called by document_routes when a user deletes a document (Day 3+).
    """
    full_path = os.path.join(upload_folder, file_path)
    try:
        os.remove(full_path)
    except FileNotFoundError:
        # File already deleted or never written — nothing to do.
        pass