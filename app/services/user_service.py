import random
import string

def generate_username(name: str) -> str:
    """
    Generates a unique-ish username based on the name.
    Example: Jane Doe -> janedoe1234
    """
    base = "".join(name.split()).lower()
    if not base:
        base = "user"
    random_suffix = "".join(random.choices(string.digits, k=4))
    return f"{base}{random_suffix}"
