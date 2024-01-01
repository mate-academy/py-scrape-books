import re


def get_availability(availability_text: str) -> int | None:
    match = re.search(r"\d+", availability_text)

    if match:
        availability_count = int(match.group())
    else:
        availability_count = None

    return availability_count
