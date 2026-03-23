from google import genai


client = genai.Client(
    vertexai=True,
    project="adk-summarizer-sab08",
    location="us-central1",
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="AI is transforming industries.",
)

print(response.text)
