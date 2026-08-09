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
        "boarding pass",
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
        # Common airline names & terms:
        "airline",
        "airways",
        "ryanair",
        "indigo",
        "emirates",
        "lufthansa",
        "airport",
        "terminal",
        "gate",
        "beszallokartya",  # International boarding pass
    ],

    "Food": [
        "restaurant",
        "food",
        "delivery",
        "menu",
        "swiggy",
        "zomato",
        "table no",
        "table number",
        "table #",
        "dine in",
        "dine-in",
        "bill total",
        "gst",
        "tip",
        "meal",
        "cuisine",
        "takeaway",
        "cafe",
        "bar",
        "coffee",
        "latte",
        "snack",
        "beverage",
        "drinks",
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
        "disc",
        "coupon",
        "refund",
        "return",
        "cart",
        "checkout",
        "tracking",
        "invoice no",
        "receipt",
        "retail",
        "wholesale",
        "cashier",
        "store",
        "shop",
        "qty",
    ],
    "Certificates": [
        "certificate",
        "award",
        "awarded",
        "honor",
        "honour",
        "recognition",
        "achievement",
        "completion",
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
        "felicitation",
        "excellence",
    ],

    "Miscellaneous": [],   # Default fallback — no keywords needed.
    # "Miscellaneous" is the default category when no keywords match.
}