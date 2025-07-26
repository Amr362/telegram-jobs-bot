import re

def validate_url(url: str) -> bool:
    pattern = re.compile(r'^(https?://)([A-Za-z0-9-]+\.)+[A-Za-z]{2,}(/.*)?$')
    return bool(pattern.match(url))

def validate_telegram_id(user_id: str) -> bool:
    return user_id.isdigit()

def validate_skills(skills: list) -> bool:
    if not isinstance(skills, list) or not skills:
        return False
    return all(isinstance(skill, str) and skill.strip() for skill in skills)

