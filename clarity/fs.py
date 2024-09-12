import os


def write_file(path: str, contents: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as file:
        file.write(contents)


def read_file(path: str) -> str:
    with open(path, "r") as file:
        return file.read()


def write_plan_note(date: str, contents: str) -> None:
    write_file(f"plans/{date}.plan", contents)


def read_plan_note(date: str) -> str:
    try:
        return read_file(f"plans/{date}.plan")
    except FileNotFoundError:
        return ""
