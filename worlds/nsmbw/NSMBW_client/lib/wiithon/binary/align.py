def align(value: int, boundary: int) -> int:
    return (value + boundary - 1) & ~(boundary - 1)