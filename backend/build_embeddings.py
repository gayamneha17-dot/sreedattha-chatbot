import json
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI()


BASE_DIR = os.path.dirname(__file__)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "knowledge",
    "chunks.json",
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "knowledge",
    "embeddings.json",
)


MODEL = "text-embedding-3-small"


def load_chunks():
    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def create_embedding(text):

    response = client.embeddings.create(
        model=MODEL,
        input=text,
    )

    return response.data[0].embedding


def build_embeddings():

    chunks = load_chunks()

    embedded_chunks = []

    total = len(chunks)

    print(
        f"Found {total} chunks."
    )

    for index, chunk in enumerate(
        chunks,
        start=1,
    ):

        print(
            f"Embedding {index}/{total}..."
        )

        text = chunk.get(
            "text",
            "",
        )

        embedding = create_embedding(
            text
        )

        embedded_chunks.append(
            {
                "id": chunk.get("id"),
                "title": chunk.get(
                    "title",
                    "",
                ),
                "url": chunk.get(
                    "url",
                    "",
                ),
                "text": text,
                "embedding": embedding,
            }
        )

    return embedded_chunks


def save_embeddings(data):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
        )

    print()
    print(
        f"Saved {len(data)} embeddings."
    )

    print(
        f"File: {OUTPUT_FILE}"
    )


if __name__ == "__main__":

    data = build_embeddings()

    save_embeddings(data)