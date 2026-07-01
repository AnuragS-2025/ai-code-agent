import os
import re


def _read_file(filename: str) -> str:

    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

    with open(filename, "r", encoding="utf-8") as file:
        return file.read()


def _write_file(filename: str, content: str) -> None:

    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)


def remove_extra_blank_lines(filename: str) -> None:

    content = _read_file(filename)

    content = re.sub(
        r"\n{3,}",
        "\n\n",
        content,
    )

    _write_file(filename, content)


def remove_trailing_whitespace(filename: str) -> None:

    lines = [
        line.rstrip()
        for line in _read_file(filename).splitlines()
    ]

    _write_file(
        filename,
        "\n".join(lines) + "\n",
    )


def ensure_single_newline(filename: str) -> None:

    content = _read_file(filename)

    content = content.rstrip() + "\n"

    _write_file(filename, content)


def cleanup_file(filename: str) -> None:

    remove_trailing_whitespace(filename)
    remove_extra_blank_lines(filename)
    ensure_single_newline(filename)