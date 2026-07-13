# SnapVault/services/classification_service.py
#
# Responsible for automatically classifying a document into one of the
# 9 categories defined in constants.py, based on its OCR-extracted text.
#
# Algorithm:
#   1. Lowercase the entire OCR text (case-insensitive matching).
#   2. For each category, count how many of its keywords appear in the text.
#   3. Return the category with the highest keyword-match count.
#   4. If no keywords match at all (all scores are zero), return 'Miscellaneous'.
#   5. If two categories tie for the highest score, Python's max() returns
#      whichever comes first in the dictionary — acceptable for an MVP.
#
# Blueprint reference: Part 4 → app/services/classification_service.py
# Day 3 Phase 4.

from SnapVault.utils.constants import CATEGORIES, CATEGORY_KEYWORDS


# ---------------------------------------------------------------------------
# Document classification
# ---------------------------------------------------------------------------

def classify(text: str) -> str:
    """
    Classify the document text into one of the 9 predefined categories.

    Uses simple keyword frequency scoring — no machine learning required.
    The text is lowercased so that "Invoice", "invoice", and "INVOICE"
    all match the keyword "invoice" equally.

    Args:
        text (str): OCR-extracted text from the document.
                    Pass an empty string if OCR failed — 'Miscellaneous'
                    will be returned in that case.

    Returns:
        str: The name of the best-matching category from CATEGORIES,
             or 'Miscellaneous' if no keywords match.

    Examples:
        classify("Invoice Total Amount Due Payment")  -> "Bills"
        classify("Prescription Doctor Hospital MRI")  -> "Medical"
        classify("")                                  -> "Miscellaneous"
        classify("random unrecognised words xyz")     -> "Miscellaneous"
    """
    # An empty or whitespace-only string cannot match any keywords.
    # Return 'Miscellaneous' immediately rather than running the loop.
    if not text or not text.strip():
        return 'Miscellaneous'

    # Lowercase once, before the loop, so we don't repeat the operation
    # for every keyword check.
    text_lower = text.lower()

    # ── Build a score dictionary ───────────────────────────────────────────
    # Start every category at 0. We will increment by 1 for each keyword
    # found in the text.
    #
    # CATEGORIES is a list of category name strings (e.g. ['Bills', 'Medical', ...]).
    # CATEGORY_KEYWORDS is a dict mapping each category name to its keyword list.
    scores = {category: 0 for category in CATEGORIES}

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            # The `in` operator checks for substring presence.
            # "invoice" in "this is an invoice for services" -> True
            # This is intentionally simple — no word boundary checks
            # needed for an MVP with focused keyword lists.
            if keyword in text_lower:
                scores[category] += 1

    # ── Find the best category ────────────────────────────────────────────
    # max() returns the key with the highest value.
    # If all values are 0, best_category is still set but best_score is 0,
    # so we handle that case explicitly below.
    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]

    # ── No keywords matched ───────────────────────────────────────────────
    # A best_score of 0 means no keyword from any category appeared in the
    # text. Return 'Miscellaneous' as the default/fallback category.
    if best_score == 0:
        return 'Miscellaneous'

    return best_category