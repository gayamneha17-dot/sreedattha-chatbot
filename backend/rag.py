import json
import os
import math
import re

from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables from .env
load_dotenv()

# Create OpenAI client
client = OpenAI()


# --------------------------------------------------
# File paths and models
# --------------------------------------------------

BASE_DIR = os.path.dirname(__file__)

EMBEDDINGS_FILE = os.path.join(
    BASE_DIR,
    "knowledge",
    "embeddings.json",
)

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-5-mini"


# --------------------------------------------------
# Load stored knowledge
# --------------------------------------------------

def load_knowledge():
    with open(
        EMBEDDINGS_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


# --------------------------------------------------
# Create embedding for student's question
# --------------------------------------------------

def create_embedding(text):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response.data[0].embedding


# --------------------------------------------------
# Compare two embeddings
# --------------------------------------------------

def cosine_similarity(vector_a, vector_b):
    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
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


# --------------------------------------------------
# Break text into keywords
# --------------------------------------------------

def tokenize(text):
    return set(
        re.findall(
            r"[a-z0-9]+",
            text.lower(),
        )
    )


# --------------------------------------------------
# Keyword scoring
# --------------------------------------------------

def keyword_score(question, chunk):
    question_words = tokenize(question)

    title = chunk.get("title", "").lower()
    url = chunk.get("url", "").lower()
    text = chunk.get("text", "").lower()

    score = 0.0

    # General keyword overlap

    chunk_words = tokenize(
        title + " " + text
    )

    common_words = (
        question_words & chunk_words
    )

    score += len(common_words) * 0.005

    # Course/program intent

    course_question_words = {
        "program",
        "programs",
        "course",
        "courses",
        "study",
        "degree",
        "degrees",
    }

    has_course_intent = bool(
        question_words & course_question_words
    )

    if has_course_intent:

        if "courses offered" in text:
            score += 0.08

        if "courses offered" in title:
            score += 0.08

        if "courses-offered" in url:
            score += 0.12

        if "under graduate" in text:
            score += 0.03

        if "post graduate" in text:
            score += 0.03

        if "b.tech" in text:
            score += 0.03

        if "m.tech" in text:
            score += 0.02

        if "mba" in text:
            score += 0.02

        if "diploma" in text:
            score += 0.02

    return score


# --------------------------------------------------
# RAG retrieval
# --------------------------------------------------

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

        semantic_score = cosine_similarity(
            question_embedding,
            chunk_embedding,
        )

        lexical_score = keyword_score(
            question,
            chunk,
        )

        final_score = (
            semantic_score
            + lexical_score
        )

        results.append(
            {
                "score": final_score,
                "semantic_score": semantic_score,
                "keyword_score": lexical_score,
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


# --------------------------------------------------
# Generate final chatbot answer
# --------------------------------------------------

def generate_answer(question):
    results = search_knowledge(question)

    context = "\n\n".join(
        f"Source: {result['title']}\n"
        f"URL: {result['url']}\n"
        f"Information: {result['text']}"
        for result in results
    )

    prompt = f"""
You are the Sree Dattha Educational Institutions AI assistant.

Answer the student's question using only the information
provided in the context below.

If the answer is not available in the context, say:
"I could not find that information in the Sree Dattha knowledge base."

Keep the answer clear, simple, and helpful.

Student Question:
{question}

Context:
{context}
"""

    response = client.responses.create(
        model=CHAT_MODEL,
        input=prompt,
    )

    return response.output_text


# --------------------------------------------------
# Run chatbot from terminal
# --------------------------------------------------

if __name__ == "__main__":
    question = input(
        "Ask a Sree Dattha question: "
    )

    answer = generate_answer(question)

    print()
    print("CHATBOT ANSWER:")
    print(answer)