import os
import requests


def generate_responsive_search_ad(description, api_key, keyword_ideas):
    """
    Generates responsive search ad suggestions and a page title using GPT-4.

    Args:
        description (str): The product description.
        api_key (str): The OpenAI API key.
        keyword_ideas (list of dict): A list of keyword ideas, each with "text" and "avg_monthly_searches".

    Returns:
        str: The generated ad content and page title, or an empty string on error.
    """
    keywords = [idea["text"] for idea in keyword_ideas]
    keyword_list = ", ".join(keywords)

    prompt = (
        f"Generate SEO-optimized Responsive Search Ad content using the provided keywords, emphasizing the most relevant keywords. "
        f"Ensure that the generated content strictly adheres to the following character limits, including spaces and punctuation:\n"
        f"1. Headlines: Create 15 brief headlines, each no longer than 29 characters, including spaces and punctuation. Do not include numbering; just list each headline as a separate sentence.\n"
        f"2. Descriptions: Create 4 descriptions, each no longer than 89 characters, including spaces and punctuation. Again, do not include numbering; just list each description as a separate sentence.\n"
        f"3. Broad Match Keywords: Recommend broad match keywords from the list.\n"
        f"4. Phrase Match Keywords: Recommend phrase match keywords from the list.\n"
        f"5. Exact Match Keywords: Recommend exact match keywords from the list.\n"
        f"6. Page Title: Suggest an SEO-optimized page title no longer than 60 characters, including spaces and punctuation, using the keywords.\n"
        f"\nKeywords: {keyword_list}\n\nProduct Description: {description}"
    )

    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "gpt-4o",  # Or your preferred GPT-4 model
        "messages": [
            {
                "role": "system",
                "content": "Generate responsive search ad content and a page title based on the provided description and keywords.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.9,
        "max_tokens": 1500,
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", json=data, headers=headers
        )
        response.raise_for_status()
        content = response.json()
        message_content = (
            content.get("choices", [{}])[0].get("message", {}).get("content", "")
        )
        return message_content
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - {http_err.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return ""
