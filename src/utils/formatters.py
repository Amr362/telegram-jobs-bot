def format_job_message(job: dict) -> str:
    title = job.get("title", "وظيفة غير معروفة")
    company = job.get("company", "شركة غير معروفة")
    link = job.get("link", "#")
    return f"💼 {title}\n🏢 {company}\n🔗 {link}"

def format_notification(message: str) -> str:
    return f"📢 إشعار جديد:\n{message}"


