def extract_keywords(text: str) -> list:
    words = text.split()
    return [w.strip(".,!?") for w in words if len(w) > 3]

def clean_text(text: str) -> str:
    return " ".join(text.split())

def rate_limiter(user_id: int) -> bool:
    return True


