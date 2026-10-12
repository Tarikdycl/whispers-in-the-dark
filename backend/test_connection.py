import os

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Send our first request
response = client.responses.create(
    model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
    instructions="You are a mysterious survival-horror game narrator.",
    input="Describe an abandoned hospital hallway in exactly two sentences.",
    max_output_tokens=120,
    store=False,
)

print("\n=== AI RESPONSE ===")
print(response.output_text)
print("===================")
print("Connection successful!")