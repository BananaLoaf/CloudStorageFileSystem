import os


def flag2mode(flags: int) -> str:
    modes = {os.O_RDONLY: "rb", os.O_WRONLY: "wb", os.O_RDWR: "wb+"}
    mode = modes[flags & (os.O_RDONLY | os.O_WRONLY | os.O_RDWR)]

    if flags | os.O_APPEND:
        mode = mode.replace("w", "a", 1)

    return mode
