import json
import os
import re
from collections import Counter


BASE_DIR = os.path.dirname(__file__)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "knowledge",
    "website_data.json",
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "knowledge",
    "chunks.json",
)


CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

BOILERPLATE_RATIO = 0.30


NOISE_LINES = {
    "toggle navigation",
    "toggle search",
    "scroll to top",
    "facebook",
    "twitter",
    "instagram",
    "youtube",
    "tumblr",
    "main home page",
}


def load_pages():
    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def normalize_line(line):
    """
    Remove unnecessary spaces from a line.
    """
    return re.sub(
        r"\s+",
        " ",
        line,
    ).strip()


def find_boilerplate_lines(pages):
    """
    Find short lines that appear on many pages.

    These repeated short lines are often
    navigation menus, headers, or footers.
    """

    page_frequency = Counter()

    for page in pages:

        text = page.get(
            "text",
            "",
        )

        unique_lines = set()

        for line in text.replace(
            "\r",
            "",
        ).split("\n"):

            line = normalize_line(line)

            if not line:
                continue

            # Only automatically classify
            # relatively short repeated lines.
            if len(line) <= 80:
                unique_lines.add(
                    line.lower()
                )

        page_frequency.update(
            unique_lines
        )

    minimum_pages = max(
        2,
        int(
            len(pages)
            * BOILERPLATE_RATIO
        ),
    )

    boilerplate_lines = {
        line
        for line, count
        in page_frequency.items()
        if count >= minimum_pages
    }

    print(
        f"Detected "
        f"{len(boilerplate_lines)} "
        f"repeated boilerplate lines."
    )

    return boilerplate_lines


def is_noise_line(
    line,
    boilerplate_lines,
):

    cleaned = line.strip().lower()

    if not cleaned:
        return True

    if cleaned in NOISE_LINES:
        return True

    if cleaned in boilerplate_lines:
        return True

    return False


def clean_text(
    text,
    boilerplate_lines,
):

    text = text.replace(
        "\r",
        "",
    )

    original_lines = text.split(
        "\n"
    )

    cleaned_lines = []

    previous_line = None

    for line in original_lines:

        line = normalize_line(line)

        if is_noise_line(
            line,
            boilerplate_lines,
        ):
            continue

        # Remove consecutive duplicates.
        if line == previous_line:
            continue

        cleaned_lines.append(line)

        previous_line = line

    return "\n".join(
        cleaned_lines
    ).strip()


def create_chunks(text):
    """
    Split cleaned text into chunks while
    keeping complete lines.

    This prevents the next chunk from
    starting in the middle of a word.
    """

    chunks = []

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    current_lines = []
    current_length = 0

    for line in lines:

        line_length = len(line) + 1

        if (
            current_lines
            and
            current_length + line_length
            > CHUNK_SIZE
        ):

            chunk = "\n".join(
                current_lines
            ).strip()

            if len(chunk) >= 100:
                chunks.append(chunk)

            # Preserve approximately 200
            # characters of complete lines
            # for contextual overlap.
            overlap_lines = []
            overlap_length = 0

            for previous_line in reversed(
                current_lines
            ):

                previous_length = (
                    len(previous_line) + 1
                )

                if (
                    overlap_length
                    + previous_length
                    > CHUNK_OVERLAP
                ):
                    break

                overlap_lines.insert(
                    0,
                    previous_line,
                )

                overlap_length += (
                    previous_length
                )

            current_lines = (
                overlap_lines.copy()
            )

            current_length = sum(
                len(item) + 1
                for item in current_lines
            )

        current_lines.append(line)

        current_length += line_length

    # Don't forget the last chunk.
    if current_lines:

        final_chunk = "\n".join(
            current_lines
        ).strip()

        if len(final_chunk) >= 100:
            chunks.append(
                final_chunk
            )

    return chunks


def build_knowledge():

    pages = load_pages()

    boilerplate_lines = (
        find_boilerplate_lines(
            pages
        )
    )

    all_chunks = []

    chunk_id = 1

    for page in pages:

        title = page.get(
            "title",
            "",
        )

        url = page.get(
            "url",
            "",
        )

        text = page.get(
            "text",
            "",
        )

        cleaned_text = clean_text(
            text,
            boilerplate_lines,
        )

        if not cleaned_text:
            continue

        page_chunks = create_chunks(
            cleaned_text
        )

        for chunk in page_chunks:

            all_chunks.append(
                {
                    "id": chunk_id,
                    "title": title,
                    "url": url,
                    "text": chunk,
                }
            )

            chunk_id += 1

    return all_chunks


def save_chunks(chunks):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print()

    print(
        f"Created "
        f"{len(chunks)} "
        f"cleaned chunks."
    )

    print(
        f"Saved to: "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":

    chunks = build_knowledge()

    save_chunks(chunks)