import re

# High-risk trigger phrases that require immediate medical attention overrides
EMERGENCY_TRIGGERS = [
    r"\bchest\s*pain\b",
    r"\bsevere\s*bleeding\b",
    r"\bheart\s*attack\b",
    r"\bstroke\b",
    r"\bloss\s*of\s*consciousness\b",
    r"\bsudden\s*vision\s*loss\b",
    r"\bcan't\s*breathe\b",
    r"\bdifficulty\s*breathing\b",
    r"\bsuicid",
    r"\bkill\s*myself\b"
]

def check_for_emergency(text: str) -> bool:
    """
    Scans the user's input text for critical emergency trigger keywords.
    Returns True if a high-risk symptom is detected, False otherwise.
    """
    text_lower = text.lower()
    for pattern in EMERGENCY_TRIGGERS:
        if re.search(pattern, text_lower):
            return True
    return False

def get_emergency_override_message() -> str:
    """Standardized emergency escalation response."""
    return (
        "🚨 EMERGENCY ALERT: Your symptoms suggest a potential medical emergency. "
        "Please stop using this chatbot and seek immediate emergency medical attention. "
        "Call your local emergency services (e.g., 108) or visit the nearest emergency room immediately."
    )
