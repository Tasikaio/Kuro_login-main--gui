import time


def get_current_timestamp(is_ms: bool = True):
    current_time = time.time()
    if is_ms:
        current_time = current_time * 1000
    return round(current_time)
