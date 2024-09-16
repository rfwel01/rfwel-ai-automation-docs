import requests


def advanced_description_with_highlights(description, api_key, keyword_ideas):
    """
    Generates SEO-optimized product content using GPT-4, integrating provided keywords.

    Args:
        description (str): The original product description.
        api_key (str): Your OpenAI API key.
        keyword_ideas (list): A list of keywords relevant to the product.

    Returns:
        dict: A dictionary containing:
            - "rewritten_description": The enhanced product description with keywords integrated.
            - "highlights": A list of key product highlights, each under 155 characters.
            - "title" : A concise, SEO-rich product title under 170 characters using keywords.
    """

    # Format the keywords for the prompt
    keywords_str = ", ".join(keyword_ideas)

    # Craft the prompt for GPT-4
    prompt = (
        "Generate SEO-optimized content for a product using the provided keywords, "
        "emphasizing the most relevant keywords. Include the following tasks:\n"
        "1. Product Title: Create an SEO-optimized title under 170 characters using the keywords.\n"
        "2. Enhanced Description: Integrate the keywords into a detailed product description.\n"
        "3. Key Specs and Features: List key specifications and features as product highlights, "
        "each under 155 characters, incorporating the keywords.\n"
        "4. Meta Description: Write a concise, SEO-rich meta description under 150 characters using the keywords.\n"
        "5. Meta Title: Develop a brief, keyword-rich meta title for product highlights, under 50 characters.\n"
        f"\nKeywords: {keywords_str}\n\nProduct Description: {description}"
    )

    # Prepare the API request payload
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": "Please generate a concise, SEO-rich product suggested title with less 170 characters, description in one paragraph. Then, must provide a list of product highlights in bullet points, each including relevant keywords naturally.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 1500,
    }

    try:
        # Make the API call to OpenAI
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", json=data, headers=headers
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        content = response.json()

        # Extract the generated content
        message_content = (
            content.get("choices", [{}])[0].get("message", {}).get("content", "")
        )

        # Split the response into description and highlights
        parts = message_content.split("**Product Highlights:**")
        formatted_description = parts[0].strip()
        highlights = parts[1].strip().split("\n") if len(parts) > 1 else []

        # Extract the title from the formatted description
        title = formatted_description.split("\n")[0]

        return {
            "rewritten_description": formatted_description,
            "highlights": highlights,
            "title": title,
        }

    # Handle potential errors
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - {http_err.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # Return empty values in case of errors
    return {"rewritten_description": "", "highlights": [], "title": ""}
