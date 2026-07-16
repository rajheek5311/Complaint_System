"""
utils/ai_logic.py
------------------
This is our "AI Logic". It's not a heavy machine-learning model —
it's a simple, fast KEYWORD-BASED classifier. This is a very common
first version of AI logic used in real ticketing tools (Zendesk,
Freshdesk, etc. started this way too) before upgrading to full ML.

It looks at the complaint TEXT and decides:
  1. PRIORITY  -> High / Medium / Low
  2. CATEGORY  -> Technical / Billing / General
"""

# Keywords are checked in lowercase, so "URGENT" and "urgent" both match.

PRIORITY_KEYWORDS = {
    'High': ['urgent', 'asap', 'immediately', 'emergency', 'critical', 'severe'],
    'Medium': ['problem', 'issue', 'trouble', 'not working', 'delay', 'delayed'],
}

CATEGORY_KEYWORDS = {
    'Technical': ['error', 'bug', 'crash', 'not loading', 'login', 'app', 'website',
                  'server', 'glitch', 'freeze', 'freezing', 'broken'],
    'Billing': ['payment', 'refund', 'invoice', 'charge', 'charged', 'billing',
                'money', 'transaction', 'subscription', 'price'],
}


def detect_priority(text: str) -> str:
    """
    Scans the complaint text for priority keywords.
    Checks High first, then Medium. If nothing matches -> Low.
    """
    text_lower = text.lower()

    for word in PRIORITY_KEYWORDS['High']:
        if word in text_lower:
            return 'High'

    for word in PRIORITY_KEYWORDS['Medium']:
        if word in text_lower:
            return 'Medium'

    return 'Low'


def detect_category(text: str) -> str:
    """
    Scans the complaint text for category keywords.
    Checks Technical first, then Billing. If nothing matches -> General.
    """
    text_lower = text.lower()

    for word in CATEGORY_KEYWORDS['Technical']:
        if word in text_lower:
            return 'Technical'

    for word in CATEGORY_KEYWORDS['Billing']:
        if word in text_lower:
            return 'Billing'

    return 'General'


def classify_complaint(subject: str, description: str) -> dict:
    """
    Combines subject + description, runs both detectors,
    and returns a dictionary the routes can use directly.
    """
    combined_text = f"{subject} {description}"
    return {
        'priority': detect_priority(combined_text),
        'category': detect_category(combined_text),
    }
