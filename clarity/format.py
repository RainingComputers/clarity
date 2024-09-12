import datetime


def format_timespan(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []

    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


def format_date(date: str) -> str:
    parsed = datetime.date.fromisoformat(date)
    return parsed.strftime("%A, %B %d, %Y")
