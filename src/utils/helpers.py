def extract_keywords(text: str) -> list:
    """
    يستخرج كلمات مفتاحية من النص بشكل بسيط.
    """
    words = text.split()
    return [w.strip(".,!?") for w in words if len(w) > 3]

def clean_text(text: str) -> str:
    """
    ينظف النص من المسافات الزائدة.
    """
    return " ".join(text.split())

def rate_limiter(user_id: int) -> bool:
    """
    نموذج بسيط لتحديد الحد الأقصى لعدد الطلبات لكل مستخدم.
    (يمكنك تحسينه لاحقًا).
    """
    return True
