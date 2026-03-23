from google import genai
import os
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite-001",
        contents="AI is transforming industries.",
    )
    print(response.text)


if __name__ == "__main__":
    main()
