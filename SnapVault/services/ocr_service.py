# SnapVault/services/ocr_service.py
#
# Responsible for all OCR (Optical Character Recognition) operations.
#
# EasyOCR is a deep-learning-based OCR library. Loading its model takes
# 3–10 seconds on first run (the model weights are downloaded and cached).
# To avoid this cost on every upload request, the Reader is created ONCE
# at module level — the first time this module is imported. All subsequent
# calls to extract_text() reuse the same Reader instance.
#
# Blueprint reference: Part 4 → app/services/ocr_service.py
# Day 3 Phase 4.

import easyocr

# ---------------------------------------------------------------------------
# Module-level Reader instantiation
# ---------------------------------------------------------------------------
# This line runs exactly ONCE — when Python first imports this module.
# After that, the Reader object lives in memory for the lifetime of the
# Flask process and is reused by every call to extract_text().
#
# gpu=False  — Use CPU only. Keeps the setup consistent across all
#              environments (local dev, CI, shared hosting) without
#              requiring a CUDA-enabled GPU. Slightly slower, but reliable.
#
# ['en']     — Load only the English language model. Adding more language
#              codes here (e.g., ['en', 'hi']) increases startup time and
#              memory usage. English-only is sufficient for the MVP.
#
# This will print a progress bar to stdout during the first startup while
# the model is loaded from disk. This is expected and harmless.

reader = easyocr.Reader(['en'], gpu=False)


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def extract_text(image_path: str) -> str:
    """
    Run OCR on the image at image_path and return the extracted text.

    EasyOCR returns a list of detections. Each detection is a tuple of:
        (bounding_box, text, confidence_score)

    Example raw output:
        [
            ([[10, 20], [200, 20], [200, 40], [10, 40]], 'Invoice', 0.98),
            ([[10, 50], [300, 50], [300, 70], [10, 70]], 'Total: $250', 0.91),
        ]

    This function extracts only the text strings, joins them with a single
    space, and returns a single string — ready to be stored in Document.ocr_text.

    If OCR fails for any reason (corrupt file, out of memory, EasyOCR bug),
    the exception is caught and an empty string is returned.
    The CALLER (document_routes.py) is responsible for recording
    ocr_status = 'failed' when this function returns an empty string.

    Graceful failure is critical here:
        - A failed OCR run should NOT crash the upload.
        - The document should still be saved with ocr_status = 'failed'.
        - The user can see the document in history even without OCR text.

    Args:
        image_path (str): Absolute path to the saved image on disk.

    Returns:
        str: The extracted text joined by spaces, or '' on failure.
    """
    try:
        # reader.readtext() accepts a file path string.
        # detail=1 (default) returns the full (bbox, text, confidence) tuples.
        results = reader.readtext(image_path)

        # Extract only the text part (index 1) from each detection tuple
        # and join them with a space to form a single readable string.
        # Index 0 = bounding box coordinates (not needed for storage/search).
        # Index 2 = confidence score (not stored in the MVP).
        extracted_text = ' '.join([detection[1] for detection in results])

        return extracted_text

    except Exception:
        # Catch-all: EasyOCR can raise various exceptions depending on
        # the image content, file format edge cases, or memory issues.
        # Returning '' signals to the caller that OCR did not produce output.
        # The empty string is falsy, so the route can check: `if not text`.
        return ''