from google import genai


def main() -> None:
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


if __name__ == "__main__":
    main()
