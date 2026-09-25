import json
import os
import math

from dotenv import load_dotenv
from openai import OpenAI


# Load variables from .env
load_dotenv()

# Create OpenAI client
client = OpenAI()


BASE_DIR = os.path.dirname(__file__)

EMBEDDINGS_FILE = os.path.join(
    BASE_DIR,
    "knowledge",
    "embeddings.json",
)

EMBEDDING_MODEL = "text-embedding-3-small"


def load_knowledge():
    with open(
        EMBEDDINGS_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def create_embedding(text):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response.data[0].embedding


def cosine_similarity(vector_a, vector_b):

    dot_product = sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b,
        )
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    return dot_product / (
        magnitude_a * magnitude_b
    )


def search_knowledge(question, limit=5):

    knowledge = load_knowledge()

    question_embedding = create_embedding(
        question
    )

    results = []

    for chunk in knowledge:

        chunk_embedding = chunk.get(
            "embedding",
            [],
        )

        similarity = cosine_similarity(
            question_embedding,
            chunk_embedding,
        )

        results.append(
            {
                "score": similarity,
                "id": chunk.get("id"),
                "title": chunk.get(
                    "title",
                    "",
                ),
                "url": chunk.get(
                    "url",
                    "",
                ),
                "text": chunk.get(
                    "text",
                    "",
                ),
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:limit]


if __name__ == "__main__":

    question = input(
        "Ask a Sree Dattha question: "
    )

    results = search_knowledge(
        question
    )

    for index, result in enumerate(
        results,
        start=1,
    ):

        print()
        print("=" * 70)

        print(
            f"RESULT {index} "
            f"| SIMILARITY: "
            f"{result['score']:.4f} "
            f"| CHUNK: {result['id']}"
        )

        print("=" * 70)

        print(
            f"TITLE: {result['title']}"
        )

        print(
            f"URL: {result['url']}"
        )

        print()

        print(
            result["text"]
        )