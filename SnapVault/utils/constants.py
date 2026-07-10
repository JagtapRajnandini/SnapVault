# ---------------------------------------------------------------------------
# File upload settings
# ---------------------------------------------------------------------------

# Allowed image formats for upload.
# Checked in both the form and storage service.
ALLOWED_EXTENSIONS: set[str] = {"png", "jpg", "jpeg"}

# Maximum upload size (16 MB).
MAX_FILE_SIZE: int = 16 * 1024 * 1024

# ---------------------------------------------------------------------------
# Document categories
# ---------------------------------------------------------------------------

# Every document is classified into one of these categories.
CATEGORIES: list[str] = [
    "Bills",
    "Medical",
    "Education",
    "Finance",
    "Travel",
    "Food",
    "Shopping",
    "Certificates",
    "Miscellaneous",
]

# ---------------------------------------------------------------------------
# Keywords for automatic document classification
# ---------------------------------------------------------------------------

# Format:
# {
#     "Category": ["keyword1", "keyword2", ...]
# }
#
# OCR text is converted to lowercase and matched against these keywords.
# The category with the highest number of matches is selected.
# If no keywords match, the document is classified as "Miscellaneous".
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Bills": [
        "bill",
        "invoice",
        "electricity",
        "water bill",
        "gas bill",
        "due date",
        "amount due",
        "payment due",
        "outstanding",
        "utility",
        "broadband",
        "internet bill",
        "mobile bill",
        "recharge",
        "subscription",
        "balance due",
    ],
    "Medical": [
        "prescription",
        "diagnosis",
        "doctor",
        "hospital",
        "clinic",
        "patient",
        "medicine",
        "tablet",
        "dosage",
        "pharmacy",
        "lab report",
        "blood test",
        "report",
        "discharge",
        "consultation",
        "treatment",
        "symptoms",
        "mg",
        "ml",
        "dr.",
    ],
    "Education": [
        "result",
        "marks",
        "grade",
        "cgpa",
        "gpa",
        "semester",
        "exam",
        "university",
        "college",
        "school",
        "certificate",
        "admit card",
        "hall ticket",
        "roll number",
        "timetable",
        "lecture",
        "assignment",
        "syllabus",
        "attendance",
    ],
    "Finance": [
        "bank",
        "account",
        "statement",
        "transaction",
        "credit",
        "debit",
        "balance",
        "transfer",
        "upi",
        "neft",
        "imps",
        "rtgs",
        "loan",
        "emi",
        "interest",
        "ifsc",
        "passbook",
        "savings",
        "fixed deposit",
        "mutual fund",
        "insurance",
    ],
    "Travel": [
        "ticket",
        "boarding",
        "flight",
        "train",
        "bus",
        "pnr",
        "reservation",
        "seat",
        "departure",
        "arrival",
        "itinerary",
        "hotel",
        "booking",
        "passport",
        "visa",
        "e-ticket",
        "platform",
        "coach",
    ],
    "Food": [
        "restaurant",
        "order",
        "food",
        "delivery",
        "menu",
        "swiggy",
        "zomato",
        "receipt",
        "table",
        "bill total",
        "gst",
        "tip",
        "meal",
        "cuisine",
        "takeaway",
        "cafe",
    ],
    "Shopping": [
        "order id",
        "shipped",
        "delivered",
        "amazon",
        "flipkart",
        "myntra",
        "product",
        "item",
        "quantity",
        "price",
        "discount",
        "coupon",
        "refund",
        "return",
        "cart",
        "checkout",
        "tracking",
        "invoice no",
    ],
    "Certificates": [
        "certificate",
        "awarded",
        "completion",
        "achievement",
        "this is to certify",
        "certified",
        "issued",
        "holder",
        "authorization",
        "accredited",
        "license",
        "internship certificate",
        "course completion",
        "participation",
    ],
    # Default fallback category.
    # "Miscellaneous" is the default category when no keywords match.
}