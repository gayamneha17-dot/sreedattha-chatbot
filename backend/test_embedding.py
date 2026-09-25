from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

text = "Sree Dattha offers Computer Science and Engineering courses."

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=text
)

embedding = response.data[0].embedding

print("Embedding created successfully!")
print("Number of values:", len(embedding))
print("First 10 values:", embedding[:10])