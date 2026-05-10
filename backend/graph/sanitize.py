"""Input sanitization to prevent prompt injection from user-supplied fields."""
import re

_INJECTION_PATTERNS = re.compile(
    r"(ignore\s+(all\s+)?(previous|prior|above)\s+instructions"
    r"|you\s+are\s+now\s+"
    r"|disregard\s+(all\s+)?"
    r"|forget\s+everything"
    r"|system\s*:\s*"
    r"|<\s*/?\s*system\s*>"
    r"|assistant\s*:\s*"
    r"|human\s*:\s*)",
    re.IGNORECASE,
)

_MAX_LENGTHS = {
    "short": 100,    # name, location
    "medium": 300,   # single field like lifestyle
    "list_item": 80, # each item in a list
}


def sanitize(text: str, max_length: int = 300) -> str:
    """Strip potential prompt injection patterns and enforce length limit."""
    if not isinstance(text, str):
        return ""
    text = text[:max_length]
    text = _INJECTION_PATTERNS.sub("[redacted]", text)
    # Collapse excessive whitespace
    text = re.sub(r"\s{3,}", "  ", text)
    return text.strip()


def sanitize_list(items: list[str], max_items: int = 10) -> list[str]:
    return [sanitize(item, _MAX_LENGTHS["list_item"]) for item in items[:max_items]]


def sanitize_profile(profile: dict) -> dict:
    """Sanitize all free-text fields in a UserProfile dict."""
    return {
        **profile,
        "location": sanitize(profile.get("location", ""), _MAX_LENGTHS["short"]),
        "health_issues": sanitize_list(profile.get("health_issues", [])),
        "lifestyle": sanitize(profile.get("lifestyle", ""), _MAX_LENGTHS["medium"]),
        "goals": sanitize_list(profile.get("goals", [])),
        "other_info": sanitize(profile.get("other_info", ""), _MAX_LENGTHS["medium"]),
    }
